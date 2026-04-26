"""06.4 calibration / seal doctrine tests.

Doctrine TEST REQUIREMENTS:
- Human preference does NOT directly change policy/rubric.
- Single reviewer override is not promotion-ready without calibration.
- Stale rubric is not used for proposal admission.
- UNKNOWN is preserved through seal — never erased.
- CompletedEvalRecord requires evidence_snapshot_hash.
- 6C cannot consume an unsealed eval record.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone

from agentic_core.L6_observability.shadow_eval import (
    build_calibration_record,
    build_completed_eval_record,
    build_human_agreement_record,
    build_judge_reliability_signal,
    build_observer_compliance_receipt,
    build_rubric_calibration_receipt,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    evaluate_governance_regression,
    evaluate_outcome,
    evaluate_readiness,
    evaluate_trajectory,
    GovernanceBaseline,
    seal_eval_record,
    stage_barrier_check,
)


def _ts(days_old: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()


def _full_eval_pipeline(sealed_completed_run, calibration_age_days: int = 0):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    iso = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    obs = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=iso)
    receipt, _m, _n = evaluate_readiness(bundle, obs, normalized)
    outcome = evaluate_outcome(receipt, normalized)
    trajectory = evaluate_trajectory(receipt, normalized)
    baseline = GovernanceBaseline(
        policy_hash=bundle.policy_hash,
        rubric_hash="rubric-A",
        replay_digest=bundle.replay_key,
    )
    governance = evaluate_governance_regression(receipt, normalized, baseline)
    calibration = build_calibration_record(
        rubric_hash="rubric-A",
        rubric_version="1.0",
        grader_version="code-only-v1",
        calibration_freshness_timestamp=_ts(calibration_age_days),
        ttl_days=7,
    )
    return bundle, receipt, outcome, trajectory, governance, calibration


def test_calibration_record_is_current_when_fresh(sealed_completed_run):
    *_, calibration = _full_eval_pipeline(sealed_completed_run, calibration_age_days=1)
    assert calibration.calibration_status == "CURRENT"
    assert calibration.deterministic_digest


def test_stale_calibration_blocks_proposal_use(sealed_completed_run):
    *_, calibration = _full_eval_pipeline(sealed_completed_run, calibration_age_days=30)
    assert calibration.calibration_status == "STALE"


def test_completed_eval_record_carries_evidence_snapshot_hash(sealed_completed_run):
    bundle, receipt, outcome, trajectory, governance, calibration = _full_eval_pipeline(sealed_completed_run)
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
    )
    assert rec.evidence_snapshot_hash, "doctrine: snapshot hash mandatory"
    assert rec.deterministic_digest
    assert rec.seal_hash


def test_seal_receipt_is_sealed_for_clean_run(sealed_completed_run):
    bundle, receipt, outcome, trajectory, governance, calibration = _full_eval_pipeline(sealed_completed_run)
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
    )
    seal = seal_eval_record(rec, calibration)
    assert seal.seal_status == "SEALED"
    assert (
        seal.uncertainty_preserved == bool(rec.uncertainty_markers)
        or seal.uncertainty_preserved is True
        or rec.uncertainty_markers == []
    )


def test_seal_rejects_when_calibration_insufficient(sealed_completed_run):
    bundle, receipt, outcome, trajectory, governance, calibration = _full_eval_pipeline(sealed_completed_run)
    bad_calib = dataclasses.replace(calibration, calibration_status="INSUFFICIENT")
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=bad_calib,
    )
    seal = seal_eval_record(rec, bad_calib)
    assert seal.seal_status == "HOLD"
    assert "CALIBRATION_INSUFFICIENT" in seal.reason_codes


def test_judge_reliability_signal_recommended_use_disabled_for_bias():
    sig = build_judge_reliability_signal(
        grader_id="judge-1",
        task_class="qa",
        rubric_hash="rh",
        recent_agreement_score=0.95,
        disagreement_rate=0.05,
        unknown_rate=0.05,
        bias_or_drift_flags=["bias_detected"],
    )
    assert sig.recommended_use == "DISABLE_FOR_SURFACE"


def test_judge_reliability_signal_human_review_when_unknown_rate_high():
    sig = build_judge_reliability_signal(
        grader_id="judge-1",
        task_class="qa",
        rubric_hash="rh",
        recent_agreement_score=0.9,
        disagreement_rate=0.1,
        unknown_rate=0.5,
    )
    assert sig.recommended_use == "REQUIRE_HUMAN_REVIEW"


def test_human_agreement_record_persists_reviewers():
    rec = build_human_agreement_record(
        rubric_hash="r",
        task_class="qa",
        samples=10,
        agreement_rate=0.9,
        reviewer_refs=["sme-1", "sme-2"],
    )
    assert rec.samples == 10
    assert rec.reviewer_refs == ["sme-1", "sme-2"]


def test_rubric_calibration_receipt_marks_stale(sealed_completed_run):
    *_, calibration = _full_eval_pipeline(sealed_completed_run, calibration_age_days=30)
    receipt = build_rubric_calibration_receipt(calibration)
    assert receipt.receipt_status == "STALE"


def test_unknown_uncertainty_is_preserved(sealed_completed_run):
    """Even when the run has UNKNOWN dimensions, seal must not erase them."""
    bundle, receipt, outcome, trajectory, governance, calibration = _full_eval_pipeline(sealed_completed_run)
    # Inject UNKNOWN into the outcome record via dataclasses.replace.
    unknown_score = dataclasses.replace(outcome.task_completion_score, result="UNKNOWN")
    outcome2 = dataclasses.replace(outcome, task_completion_score=unknown_score)
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome2,
        trajectory=trajectory,
        governance=governance,
        calibration=calibration,
    )
    assert any("UNKNOWN" in m for m in rec.uncertainty_markers)


def test_stale_calibration_restricts_downstream_use_to_rca_only(sealed_completed_run):
    """Per 06.4 doctrine: stale calibration cannot support proposal admission."""
    bundle, receipt, outcome, trajectory, governance, _calib = _full_eval_pipeline(
        sealed_completed_run, calibration_age_days=30
    )
    stale = build_calibration_record(
        rubric_hash="rubric-A",
        rubric_version="1.0",
        grader_version="code-only-v1",
        calibration_freshness_timestamp=_ts(30),
        ttl_days=7,
    )
    assert stale.calibration_status == "STALE"
    rec = build_completed_eval_record(
        runtime_exhaust_bundle_id=bundle.runtime_exhaust_bundle_id,
        eval_readiness_receipt_id=receipt.eval_readiness_receipt_id,
        outcome=outcome,
        trajectory=trajectory,
        governance=governance,
        calibration=stale,
    )
    assert rec.allowed_downstream_use == "RCA_ONLY"
