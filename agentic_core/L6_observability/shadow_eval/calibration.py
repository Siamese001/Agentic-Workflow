"""06.4 — Human Calibration and Eval Record Seal.

Implements:

* CalibrationRecord
* JudgeReliabilitySignal
* HumanAgreementRecord
* RubricCalibrationReceipt
* CompletedEvalRecord
* EvalRecordSealReceipt

Doctrine rules enforced:

- Calibration freshness within configured TTL is required for proposal use.
- Stale rubrics block proposal admission unless explicitly held.
- ``UNKNOWN`` is preserved through the seal — never erased.
- A single reviewer override is calibration evidence, not live authority.
- 6C cannot consume an eval record that was not sealed here.
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

from agentic_core.L6_observability.shadow_eval._digest import (
    canonical_json,
    compute_digest,
    stamp_digest,
)
from agentic_core.L6_observability.shadow_eval.contracts import (
    ALLOWED_DOWNSTREAM_USE,
    CalibrationRecord,
    CompletedEvalRecord,
    EvalRecordSealReceipt,
    GovernanceRegressionRecord,
    HumanAgreementRecord,
    JudgeReliabilitySignal,
    OutcomeEvalRecord,
    RubricCalibrationReceipt,
    TrajectoryEvalRecord,
)


class CalibrationError(Exception):
    """Raised when calibration / seal preconditions are violated."""


CALIBRATION_TTL_DAYS_DEFAULT = 7  # 06.8 KPI: calibration <= 7 days per rubric


def _gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# CalibrationRecord builders
# ---------------------------------------------------------------------------


def build_calibration_record(
    *,
    rubric_hash: str,
    rubric_version: str,
    grader_version: str,
    calibration_source_refs: Iterable[str] = (),
    reviewer_refs: Iterable[str] = (),
    golden_set_refs: Iterable[str] = (),
    hitl_decision_refs: Iterable[str] = (),
    kappa_or_agreement_score: float = 0.0,
    false_positive_estimate: float = 0.0,
    false_negative_estimate: float = 0.0,
    unknown_budget_status: str = "WITHIN_BUDGET",
    calibration_freshness_timestamp: str | None = None,
    ttl_days: int = CALIBRATION_TTL_DAYS_DEFAULT,
) -> CalibrationRecord:
    """Build a CalibrationRecord; deterministic_digest is stamped on return."""
    ts = calibration_freshness_timestamp or _now().isoformat()
    parsed = _parse_iso(ts)
    if parsed is None:
        status = "INSUFFICIENT"
    else:
        delta = _now() - parsed
        status = "CURRENT" if delta <= timedelta(days=ttl_days) else "STALE"
    if unknown_budget_status not in {"WITHIN_BUDGET", "OVER_BUDGET", "UNKNOWN"}:
        unknown_budget_status = "UNKNOWN"
    rec = CalibrationRecord(
        calibration_record_id=_gen_id("calib"),
        rubric_hash=rubric_hash,
        rubric_version=rubric_version,
        grader_version=grader_version,
        calibration_source_refs=list(calibration_source_refs),
        reviewer_refs=list(reviewer_refs),
        golden_set_refs=list(golden_set_refs),
        hitl_decision_refs=list(hitl_decision_refs),
        kappa_or_agreement_score=kappa_or_agreement_score,
        false_positive_estimate=false_positive_estimate,
        false_negative_estimate=false_negative_estimate,
        unknown_budget_status=unknown_budget_status,
        calibration_freshness_timestamp=ts,
        calibration_status=status,
    )
    return stamp_digest(rec)


def build_judge_reliability_signal(
    *,
    grader_id: str,
    task_class: str,
    rubric_hash: str,
    recent_agreement_score: float,
    disagreement_rate: float,
    unknown_rate: float,
    forced_certainty_flags: Iterable[str] = (),
    bias_or_drift_flags: Iterable[str] = (),
) -> JudgeReliabilitySignal:
    if disagreement_rate > 0.4 or recent_agreement_score < 0.5:
        recommended = "REQUIRE_HYBRID"
    if unknown_rate > 0.3:
        recommended = "REQUIRE_HUMAN_REVIEW"
    elif disagreement_rate > 0.4 or recent_agreement_score < 0.5:
        recommended = "REQUIRE_HYBRID"
    elif forced_certainty_flags or bias_or_drift_flags:
        recommended = "DISABLE_FOR_SURFACE"
    else:
        recommended = "ALLOW_FOR_EVAL"
    return JudgeReliabilitySignal(
        judge_reliability_signal_id=_gen_id("judge"),
        grader_id=grader_id,
        task_class=task_class,
        rubric_hash=rubric_hash,
        recent_agreement_score=recent_agreement_score,
        disagreement_rate=disagreement_rate,
        unknown_rate=unknown_rate,
        forced_certainty_flags=list(forced_certainty_flags),
        bias_or_drift_flags=list(bias_or_drift_flags),
        recommended_use=recommended,
    )


def build_human_agreement_record(
    *,
    rubric_hash: str,
    task_class: str,
    samples: int,
    agreement_rate: float,
    reviewer_refs: Iterable[str] = (),
) -> HumanAgreementRecord:
    return HumanAgreementRecord(
        human_agreement_id=_gen_id("hum"),
        rubric_hash=rubric_hash,
        task_class=task_class,
        samples=samples,
        agreement_rate=agreement_rate,
        reviewer_refs=list(reviewer_refs),
    )


def build_rubric_calibration_receipt(
    calibration: CalibrationRecord,
) -> RubricCalibrationReceipt:
    if calibration.calibration_status == "CURRENT":
        status = "FRESH"
    elif calibration.calibration_status in {"STALE", "INSUFFICIENT", "CONFLICTED"}:
        status = "STALE"
    else:
        status = "INSUFFICIENT"
    return RubricCalibrationReceipt(
        rubric_calibration_receipt_id=_gen_id("rubric_recpt"),
        rubric_hash=calibration.rubric_hash,
        calibration_record_id=calibration.calibration_record_id,
        receipt_status=status,
        notes="",
    )


# ---------------------------------------------------------------------------
# CompletedEvalRecord seal
# ---------------------------------------------------------------------------


def _evidence_snapshot_hash(
    outcome: OutcomeEvalRecord,
    trajectory: TrajectoryEvalRecord,
    governance: GovernanceRegressionRecord,
) -> str:
    payload = {
        "outcome": outcome.outcome_eval_id,
        "outcome_digest": outcome.deterministic_digest,
        "trajectory": trajectory.trajectory_eval_id,
        "trajectory_digest": trajectory.deterministic_digest,
        "governance": governance.governance_regression_id,
        "governance_digest": governance.deterministic_digest,
        "outcome_refs": list(outcome.normalized_record_refs),
        "trajectory_refs": list(trajectory.normalized_record_refs),
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _collect_uncertainty(
    outcome: OutcomeEvalRecord,
    trajectory: TrajectoryEvalRecord,
) -> list[str]:
    markers: list[str] = []
    markers.extend(outcome.uncertainty_markers)
    markers.extend(trajectory.trajectory_flags)
    # Preserve UNKNOWN dimension results
    for f in (
        outcome.task_completion_score,
        outcome.answer_correctness_score,
        outcome.groundedness_score,
        outcome.citation_support_score,
        outcome.evidence_sufficiency_score,
        outcome.usefulness_score,
    ):
        if f.result == "UNKNOWN" and f"{f.dimension_name}=UNKNOWN" not in markers:
            markers.append(f"{f.dimension_name}=UNKNOWN")
    return markers


def _derive_downstream_use(
    calibration: CalibrationRecord,
    governance: GovernanceRegressionRecord,
) -> str:
    """Per 06.4 doctrine, calibration status governs downstream use.

    - INSUFFICIENT / CONFLICTED / STALE calibration -> RCA_ONLY (no proposal).
    - Governance severity is signal for the proposal author but does not
      auto-restrict downstream use; reviewers may flag for SME at admission.
    """
    if calibration.calibration_status in {"INSUFFICIENT", "CONFLICTED", "STALE"}:
        return "RCA_ONLY"
    return "RCA_AND_PROPOSAL"


def build_completed_eval_record(
    *,
    runtime_exhaust_bundle_id: str,
    eval_readiness_receipt_id: str,
    outcome: OutcomeEvalRecord,
    trajectory: TrajectoryEvalRecord,
    governance: GovernanceRegressionRecord,
    calibration: CalibrationRecord,
    grader_versions: Iterable[str] = (),
    reviewer_override_refs: Iterable[str] = (),
    support_rationale_refs: Iterable[str] = (),
    hmac_sig: str | None = None,
) -> CompletedEvalRecord:
    snapshot_hash = _evidence_snapshot_hash(outcome, trajectory, governance)
    score_bundle: dict[str, float] = {
        "outcome.task_completion": outcome.task_completion_score.score,
        "outcome.answer_correctness": outcome.answer_correctness_score.score,
        "outcome.groundedness": outcome.groundedness_score.score,
        "outcome.citation_support": outcome.citation_support_score.score,
        "trajectory.route_fit": trajectory.route_fit_score.score,
        "trajectory.tool_order": trajectory.tool_order_score.score,
        "trajectory.retry_thrash": trajectory.retry_thrash_score.score,
        "governance.policy_drift_count": float(len(governance.policy_drift_flags)),
        "governance.replay_drift_count": float(len(governance.replay_digest_drift_flags)),
    }
    rec = CompletedEvalRecord(
        completed_eval_record_id=_gen_id("ceval"),
        runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=eval_readiness_receipt_id,
        outcome_eval_ref=outcome.outcome_eval_id,
        trajectory_eval_ref=trajectory.trajectory_eval_id,
        governance_regression_ref=governance.governance_regression_id,
        calibration_record_ref=calibration.calibration_record_id,
        rubric_hash=calibration.rubric_hash,
        rubric_version=calibration.rubric_version,
        grader_versions=list(grader_versions) or [calibration.grader_version],
        evidence_snapshot_hash=snapshot_hash,
        immutable_score_bundle=score_bundle,
        uncertainty_markers=_collect_uncertainty(outcome, trajectory),
        support_rationale_refs=list(support_rationale_refs),
        reviewer_override_refs=list(reviewer_override_refs),
        allowed_downstream_use=_derive_downstream_use(calibration, governance),
        hmac_sig=hmac_sig,
    )
    # Compute the seal_hash over the canonical content, then digest.
    seal_hash = compute_digest(rec)
    object.__setattr__(rec, "seal_hash", seal_hash)
    return stamp_digest(rec)


def seal_eval_record(
    record: CompletedEvalRecord,
    calibration: CalibrationRecord,
) -> EvalRecordSealReceipt:
    refs_present = all(
        bool(getattr(record, name))
        for name in (
            "outcome_eval_ref",
            "trajectory_eval_ref",
            "governance_regression_ref",
            "calibration_record_ref",
        )
    )
    rubric_integrity = "OK" if record.rubric_hash == calibration.rubric_hash else "MISMATCH"
    seal_status = (
        "SEALED"
        if (
            refs_present
            and rubric_integrity == "OK"
            and record.allowed_downstream_use in ALLOWED_DOWNSTREAM_USE
            and record.evidence_snapshot_hash
            and record.uncertainty_markers is not None
        )
        else "REJECTED"
    )
    if calibration.calibration_status not in {"CURRENT", "STALE"}:
        seal_status = "HOLD"
    reasons: list[str] = []
    if not refs_present:
        reasons.append("MISSING_EVAL_REFS")
    if rubric_integrity != "OK":
        reasons.append("RUBRIC_HASH_MISMATCH")
    if calibration.calibration_status not in {"CURRENT", "STALE"}:
        reasons.append("CALIBRATION_INSUFFICIENT")
    return EvalRecordSealReceipt(
        seal_receipt_id=_gen_id("seal"),
        completed_eval_record_id=record.completed_eval_record_id,
        required_eval_refs_present=refs_present,
        calibration_status=calibration.calibration_status,
        rubric_integrity_status=rubric_integrity,
        evidence_snapshot_bound=bool(record.evidence_snapshot_hash),
        uncertainty_preserved=bool(record.uncertainty_markers),
        downstream_use_scope=record.allowed_downstream_use,
        seal_status=seal_status,
        reason_codes=reasons,
    )


__all__ = [
    "CalibrationError",
    "CALIBRATION_TTL_DAYS_DEFAULT",
    "build_calibration_record",
    "build_judge_reliability_signal",
    "build_human_agreement_record",
    "build_rubric_calibration_receipt",
    "build_completed_eval_record",
    "seal_eval_record",
]
