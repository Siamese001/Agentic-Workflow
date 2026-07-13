"""apps_rg Exit binding — C0 evidence and authenticated L5 packet evaluation.

The local ``ExitGateVerdict`` is not the 00C ``GateVerdict`` type.  L5 remains
an evidence-only plane; Exit consumes its verified packet as a fail-closed
precondition and never lets L5 authorize a runtime disposition.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

from apps_rg.runtime.bindings.judge_calibration_baseline import (
    APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY,
)
from apps_rg.runtime.schemas import SectionCacheWriteProposal

if TYPE_CHECKING:
    from agentic_core.L4_state.contracts.app_domain import (
        ApprovedJudgeCalibrationBaseline,
    )
    from agentic_core.L4_state.contracts.app_domain_lookup import (
        InMemoryAppDomainStore,
    )
    from agentic_core.runtime.exhaust.runtime_exhaust_bundle import RuntimeExhaustBundle

_BLOCKING_SUPPORT_STATUSES: frozenset[str] = frozenset(
    {
        STATUS_UNKNOWN,
        SUPPORT_STATUS_EMPTY,
        SUPPORT_STATUS_BLOCKED,
        SUPPORT_STATUS_CONFLICTED,
    }
)
_NON_BLOCKING_STATUSES: frozenset[str] = frozenset({SUPPORT_STATUS_PASS, SUPPORT_STATUS_WEAK_WITH_CAVEATS})
_PLACEHOLDER_TEST_L5_CERT_REF = "test:valid:w6"


class ExitGateVerdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ExitGateResult:
    gate_id: str
    verdict: ExitGateVerdict
    reason: str = ""


@dataclass(frozen=True)
class InertArtifactCommitCandidate:
    """Non-durable proposal; UWG remains the sole durable-write authority."""

    artifact_type: str
    proposed_path: str
    content_digest: str
    serialized_content: dict[str, Any]
    mutation_candidate_inert: bool = True
    non_durable: bool = True
    not_l4_truth: bool = True
    not_replay_source: bool = True
    proposal_status: str = "PENDING_UWG"


@dataclass(frozen=True)
class ExitDisposition:
    outcome_authorized: bool
    gate_results: list[ExitGateResult]
    c0_blocking: bool
    blocking_reason: str = ""
    final_output: Optional[str] = None


@dataclass(frozen=True)
class ExitResult:
    disposition: ExitDisposition
    artifact_commit_candidates: list[InertArtifactCommitCandidate]
    cache_write_proposals: tuple[SectionCacheWriteProposal, ...] = ()


def _evaluate_judge_reliability_gate(
    baseline: "ApprovedJudgeCalibrationBaseline | None",
) -> ExitGateResult:
    """Validate a future-run L4 baseline without computing calibration."""
    if baseline is None:
        return ExitGateResult(
            "G_JUDGE_RELIABILITY",
            ExitGateVerdict.WARN,
            "informational judge has no approved future-run baseline",
        )
    expected = {
        **APPS_RG_EXEC_POSITIONING_CALIBRATION_IDENTITY,
        "created_by_surface": "UWG",
    }
    mismatches = [key for key, value in expected.items() if str(getattr(baseline, key, "") or "") != value]
    if not str(getattr(baseline, "uwg_receipt_ref", "") or ""):
        mismatches.append("uwg_receipt_ref")
    if not str(getattr(baseline, "promotion_receipt_ref", "") or ""):
        mismatches.append("promotion_receipt_ref")
    if not str(getattr(baseline, "deterministic_digest", "") or ""):
        mismatches.append("deterministic_digest")
    try:
        approved_at = datetime.fromisoformat(str(baseline.approved_at))
        expires_at = datetime.fromisoformat(str(baseline.expires_at))
        if approved_at.tzinfo is None or expires_at.tzinfo is None:
            raise ValueError("baseline timestamps must be timezone-aware")
        now = datetime.now(timezone.utc)
        expired = expires_at <= now
        if approved_at > now:
            mismatches.append("approved_at")
    except (TypeError, ValueError):
        expired = True
        mismatches.append("expires_at")
    if mismatches or expired or getattr(baseline, "status", "") != "active":
        reason = "baseline rejected: " + ",".join(sorted(set(mismatches)))
        if expired:
            reason += ",expired"
        return ExitGateResult(
            "G_JUDGE_RELIABILITY",
            ExitGateVerdict.UNKNOWN,
            reason,
        )
    approved_use = str(getattr(baseline, "approved_use", "") or "")
    if approved_use == "ALLOW_FOR_EVAL":
        return ExitGateResult(
            "G_JUDGE_RELIABILITY",
            ExitGateVerdict.PASS,
            "approved future-run baseline may inform evaluation; never authorizes alone",
        )
    if approved_use == "REQUIRE_HUMAN_REVIEW":
        return ExitGateResult(
            "G_JUDGE_RELIABILITY",
            ExitGateVerdict.UNKNOWN,
            "approved future-run posture requires human review",
        )
    if approved_use == "REQUIRE_HYBRID":
        reason = "approved future-run posture requires corroborating signal"
    elif approved_use == "DISABLE_FOR_SURFACE":
        reason = "approved future-run posture disables judge use for this surface"
    else:
        reason = "approved future-run posture is advisory only"
    return ExitGateResult(
        "G_JUDGE_RELIABILITY",
        ExitGateVerdict.WARN,
        f"{reason}; posture={approved_use}",
    )


def _resolve_judge_reliability_gate(
    baseline_ref: str,
    *,
    store: "InMemoryAppDomainStore | None" = None,
) -> ExitGateResult:
    """Resolve an approved baseline through the read-only L4 lookup surface."""
    if not baseline_ref:
        return _evaluate_judge_reliability_gate(None)
    from agentic_core.L4_state.contracts.app_domain_lookup import (
        AppDomainLookupError,
        get_default_app_domain_store,
    )

    try:
        baseline = (store or get_default_app_domain_store()).get_judge_calibration_baseline(baseline_ref)
    except (AppDomainLookupError, KeyError, ValueError) as exc:
        return ExitGateResult(
            "G_JUDGE_RELIABILITY",
            ExitGateVerdict.UNKNOWN,
            f"approved baseline could not be resolved: {type(exc).__name__}",
        )
    return _evaluate_judge_reliability_gate(baseline)


def _evaluate_c0_evidence_gates(
    fec: Optional[FinalEvidenceContract],
) -> tuple[list[ExitGateResult], bool, str]:
    results: list[ExitGateResult] = []
    is_blocking = False
    blocking_reasons: list[str] = []

    if fec is None:
        return (
            [
                ExitGateResult(
                    "G_SUPPORT_STATUS",
                    ExitGateVerdict.WARN,
                    "fec=None; no C0 evidence for this run",
                ),
                ExitGateResult("G09", ExitGateVerdict.WARN, "fec=None; no freshness receipts"),
                ExitGateResult("G13", ExitGateVerdict.WARN, "fec=None; no citation map"),
            ],
            False,
            "",
        )

    support_status = str(getattr(fec, "support_status", STATUS_UNKNOWN) or STATUS_UNKNOWN)
    support_target_met = bool(getattr(fec, "support_target_met", False))
    if support_status in _BLOCKING_SUPPORT_STATUSES:
        results.append(
            ExitGateResult(
                "G_SUPPORT_STATUS",
                ExitGateVerdict.FAIL,
                f"support_status={support_status} is blocking",
            )
        )
        is_blocking = True
        blocking_reasons.append(support_status)
    elif not support_target_met:
        results.append(
            ExitGateResult(
                "G_SUPPORT_STATUS",
                ExitGateVerdict.WARN,
                f"support_status={support_status} but support_target_met=False",
            )
        )
    else:
        results.append(
            ExitGateResult(
                "G_SUPPORT_STATUS",
                ExitGateVerdict.PASS,
                f"support_status={support_status}",
            )
        )

    freshness = tuple(getattr(fec, "freshness_receipts", ()) or ())
    results.append(
        ExitGateResult(
            "G09",
            ExitGateVerdict.PASS if freshness else ExitGateVerdict.WARN,
            f"{len(freshness)} freshness receipts" if freshness else "no freshness receipts",
        )
    )

    citation_map = tuple(getattr(fec, "citation_map", ()) or ())
    excluded_refs = tuple(getattr(fec, "excluded_evidence_refs", ()) or ())
    if citation_map:
        results.append(ExitGateResult("G13", ExitGateVerdict.PASS, f"{len(citation_map)} citation(s)"))
    elif excluded_refs:
        results.append(
            ExitGateResult(
                "G13",
                ExitGateVerdict.FAIL,
                f"G13: citation_map is empty but {len(excluded_refs)} excluded_evidence_refs present",
            )
        )
        is_blocking = True
        blocking_reasons.append("G13")
    else:
        results.append(ExitGateResult("G13", ExitGateVerdict.WARN, "citation_map empty; no excluded refs"))

    return results, is_blocking, ", ".join(blocking_reasons)


def _is_valid_l5_packet_digest(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _l5_verification(
    sealed: SealedL2Artifact,
    *,
    prompt_artifact: Any = None,
    fec: Optional[FinalEvidenceContract] = None,
    allow_test_l5_cert_ref: bool = False,
):
    from apps_rg.runtime.l5.packet_builder import verify_l5_packet_against_runtime

    return verify_l5_packet_against_runtime(
        sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
        allow_test_l5_cert_ref=allow_test_l5_cert_ref,
        require_stored_verification=True,
    )


def _evaluate_l5_certification_gate(
    sealed: SealedL2Artifact,
    *,
    prompt_artifact: Any = None,
    fec: Optional[FinalEvidenceContract] = None,
    allow_test_l5_cert_ref: bool = False,
) -> tuple[ExitGateResult, bool, str]:
    """Verify the full attached packet and its runtime binding, fail closed."""

    verification = _l5_verification(
        sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
        allow_test_l5_cert_ref=allow_test_l5_cert_ref,
    )
    if not verification.verified:
        reason = "L5 packet verification failed: " + ";".join(verification.reason_codes)
        return (
            ExitGateResult("G_L5_CERTIFICATION", ExitGateVerdict.FAIL, reason),
            True,
            reason,
        )
    return (
        ExitGateResult("G_L5_CERTIFICATION", ExitGateVerdict.PASS, "L5_CERTIFIED_VERIFIED"),
        False,
        "",
    )


def _compute_apps_rg_owned_fields(
    fec: Optional[FinalEvidenceContract],
    sealed: SealedL2Artifact,
) -> dict[str, Any]:
    if fec is None:
        return {
            "jd_keyword_coverage": 0.0,
            "overfit_score": 0.0,
            "provenance_valid": False,
            "material_claim_support_rate": 0.0,
            "unsupported_material_claim_rate": 1.0,
            "citation_anchor_coverage": 0.0,
        }

    retrieval_sources = tuple(getattr(fec, "retrieval_sources", ()) or ())
    jd_count = sum(1 for source in retrieval_sources if source.startswith("jd_payload"))
    jd_coverage = jd_count / len(retrieval_sources) if retrieval_sources else 0.0
    citation_map = tuple(getattr(fec, "citation_map", ()) or ())
    evidence_count = len(getattr(fec, "evidence_items", ()) or ())
    citation_coverage = min(len(citation_map) / evidence_count, 1.0) if evidence_count else 0.0
    provenance_valid = bool(
        getattr(sealed, "compilation_hash", "")
        and _is_valid_l5_packet_digest(str(getattr(sealed, "l5_certification_packet_digest", "") or ""))
        and getattr(sealed, "l5_certification_status", "") == "L5_CERTIFIED"
        and bool(getattr(sealed, "l5_certification_verified", False))
    )
    return {
        "jd_keyword_coverage": round(jd_coverage, 4),
        "overfit_score": 0.0,
        "provenance_valid": provenance_valid,
        "material_claim_support_rate": round(jd_coverage, 4),
        "unsupported_material_claim_rate": round(1.0 - jd_coverage, 4),
        "citation_anchor_coverage": round(citation_coverage, 4),
    }


def exit_finalize_apps_rg(
    sealed: SealedL2Artifact,
    prompt_artifact: Any = None,
    *,
    fec: Optional[FinalEvidenceContract] = None,
    target_company: str = "",
    target_role: str = "",
    approved_judge_calibration_baseline_ref: str = "",
    app_domain_store: "InMemoryAppDomainStore | None" = None,
) -> ExitResult:
    from apps_rg.runtime.spine.governed_l2_exit_compose import (
        governed_exit_finalize_integrated,
        governed_l2_exit_enabled,
    )

    if governed_l2_exit_enabled():
        bundle = governed_exit_finalize_integrated(
            sealed,
            fec=fec,
            target_company=target_company,
            target_role=target_role,
            prompt_artifact=prompt_artifact,
            approved_judge_calibration_baseline_ref=approved_judge_calibration_baseline_ref,
            app_domain_store=app_domain_store,
        )
        result = bundle.exit_result
        object.__setattr__(result, "_governed_integrated_exit_bundle", bundle)
        return result
    return _exit_finalize_apps_rg_impl(
        sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
        target_company=target_company,
        target_role=target_role,
        approved_judge_calibration_baseline_ref=approved_judge_calibration_baseline_ref,
        app_domain_store=app_domain_store,
    )


def _exit_finalize_apps_rg_impl(
    sealed: SealedL2Artifact,
    prompt_artifact: Any = None,
    *,
    fec: Optional[FinalEvidenceContract] = None,
    target_company: str = "",
    target_role: str = "",
    allow_test_l5_cert_ref: bool = False,
    approved_judge_calibration_baseline_ref: str = "",
    app_domain_store: "InMemoryAppDomainStore | None" = None,
) -> ExitResult:
    gate_results, c0_blocking, blocking_reason = _evaluate_c0_evidence_gates(fec)
    verification = _l5_verification(
        sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
        allow_test_l5_cert_ref=allow_test_l5_cert_ref,
    )
    l5_gate, l5_blocking, l5_blocking_reason = _evaluate_l5_certification_gate(
        sealed,
        prompt_artifact=prompt_artifact,
        fec=fec,
        allow_test_l5_cert_ref=allow_test_l5_cert_ref,
    )
    gate_results.append(l5_gate)
    gate_results.append(
        _resolve_judge_reliability_gate(
            approved_judge_calibration_baseline_ref,
            store=app_domain_store,
        )
    )
    if l5_blocking:
        blocking_reason = ", ".join(reason for reason in (blocking_reason, l5_blocking_reason) if reason)

    owned_fields = _compute_apps_rg_owned_fields(fec, sealed)
    outcome_authorized = not c0_blocking and not l5_blocking
    run_id = str(getattr(sealed, "run_id", "") or "")
    metadata_payload = {
        "run_id": run_id,
        "target_company": target_company,
        "target_role": target_role,
        "outcome_authorized": outcome_authorized,
        "w4_c0_evidence": {
            "c0_blocking": c0_blocking,
            "l5_blocking": l5_blocking,
            "blocking_reason": blocking_reason,
            "l5_certification_packet_ref": str(getattr(sealed, "l5_certification_packet_ref", "") or ""),
            "l5_certification_packet_digest": str(
                getattr(sealed, "l5_certification_packet_digest", "") or ""
            ),
            "l5_certification_status": str(getattr(sealed, "l5_certification_status", "") or ""),
            "l5_runtime_binding_digest": str(getattr(sealed, "l5_runtime_binding_digest", "") or ""),
            "l5_certification_verified": verification.verified,
            "l5_certification_verification_digest": verification.verification_digest,
            "l5_verification_reason_codes": list(verification.reason_codes),
            "gate_results": [
                {
                    "gate_id": gate.gate_id,
                    "verdict": gate.verdict.value,
                    "reason": gate.reason,
                }
                for gate in gate_results
            ],
            **owned_fields,
        },
    }
    run_metadata_candidate = InertArtifactCommitCandidate(
        artifact_type="run_metadata",
        proposed_path=f"virtual/apps_rg/runs/{run_id}/run_metadata.json",
        content_digest=hashlib.sha256(
            json.dumps(metadata_payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest(),
        serialized_content=metadata_payload,
    )

    disposition = ExitDisposition(
        outcome_authorized=outcome_authorized,
        gate_results=gate_results,
        c0_blocking=c0_blocking or l5_blocking,
        blocking_reason=blocking_reason,
        final_output=getattr(sealed, "generated_content", None),
    )

    cache_proposals: tuple[SectionCacheWriteProposal, ...] = ()
    if outcome_authorized:
        section_id = _exit_section_id(fec, sealed)
        intent_digest = _exit_c0_intent_digest(fec)
        content = str(getattr(sealed, "generated_content", "") or "")
        content_digest = (
            str(getattr(sealed, "compilation_hash", "") or "")
            or hashlib.sha256(content.encode("utf-8")).hexdigest()
        )
        cache_proposals = (
            SectionCacheWriteProposal(
                section_id=section_id,
                cache_key=intent_digest or f"c0_intent:{run_id}:{section_id}",
                content_digest=content_digest,
                metadata_ref=f"virtual/apps_rg/runs/{run_id}/c02_semantic_cache_payload.json",
                proposal_status="PENDING_UWG",
                l5_certification_packet_ref=str(getattr(sealed, "l5_certification_packet_ref", "") or ""),
                l5_certification_packet_digest=str(
                    getattr(sealed, "l5_certification_packet_digest", "") or ""
                ),
                l5_runtime_binding_digest=str(getattr(sealed, "l5_runtime_binding_digest", "") or ""),
                l5_certification_verified=verification.verified,
                l5_certification_verification_digest=verification.verification_digest,
            ),
        )

    return ExitResult(
        disposition=disposition,
        artifact_commit_candidates=[run_metadata_candidate],
        cache_write_proposals=cache_proposals,
    )


def _exit_section_id(fec: Optional[FinalEvidenceContract], sealed: SealedL2Artifact) -> str:
    for source in (fec, sealed):
        section_id = getattr(source, "section_id", "") if source is not None else ""
        if isinstance(section_id, str) and section_id.strip():
            return section_id.strip()
    return ""


def _exit_c0_intent_digest(fec: Optional[FinalEvidenceContract]) -> str:
    if fec is None:
        return ""
    return str(getattr(fec, "c0_section_intent_digest", "") or "").strip()


def build_exhaust_bundle_from_exit(
    exit_result: ExitResult,
    sealed: SealedL2Artifact,
    *,
    learning_profile_ref: str = "",
    meta_feedback_profile_ref: str = "",
    exit_disposition_ref: str | None = None,
    gate_mesh_result_ref: str | None = None,
    sealed_result_ref: str | None = None,
) -> "RuntimeExhaustBundle":
    from agentic_core.runtime.exhaust.runtime_exhaust_bundle import (
        build_runtime_exhaust_bundle,
    )

    exit_ref = str(exit_disposition_ref or "").strip()
    if not exit_ref:
        exit_ref = str(getattr(sealed, "compilation_hash", "") or "").strip()
        if not exit_ref:
            exit_ref = _synthetic_exit_disposition_digest(exit_result)

    gate_ref = gate_mesh_result_ref
    if gate_ref is None:
        refs = tuple(getattr(sealed, "gate_verdict_refs", ()) or ())
        gate_ref = ",".join(refs) if refs else ""
    sealed_ref = sealed_result_ref
    if sealed_ref is None:
        sealed_ref = (
            str(getattr(sealed, "replay_key", "") or "").strip()
            or str(getattr(sealed, "compilation_hash", "") or "").strip()
        )

    return build_runtime_exhaust_bundle(
        request_id=getattr(sealed, "request_id", "") or "",
        run_id=getattr(sealed, "run_id", "") or "",
        trace_root=getattr(sealed, "trace_id", "") or "",
        gate_mesh_result_ref=gate_ref or "",
        exit_disposition_ref=exit_ref,
        sealed_result_ref=sealed_ref or "",
        learning_profile_ref=learning_profile_ref,
        meta_feedback_profile_ref=meta_feedback_profile_ref,
        l5_certification_packet_ref=str(getattr(sealed, "l5_certification_packet_ref", "") or ""),
        l5_certification_packet_digest=str(getattr(sealed, "l5_certification_packet_digest", "") or ""),
        l5_certification_status=str(getattr(sealed, "l5_certification_status", "") or ""),
    )


def _synthetic_exit_disposition_digest(exit_result: ExitResult) -> str:
    disposition = exit_result.disposition
    payload = {
        "outcome_authorized": disposition.outcome_authorized,
        "c0_blocking": disposition.c0_blocking,
        "blocking_reason": disposition.blocking_reason,
        "gate_ids": [gate.gate_id for gate in disposition.gate_results],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256::" + hashlib.sha256(raw.encode()).hexdigest()[:40]


def build_apps_rg_exit_harness(
    sealed: SealedL2Artifact,
    fec: Optional[FinalEvidenceContract] = None,
) -> ExitResult:
    state_diff = dict(getattr(sealed, "proposed_state_diff", {}) or {})
    return exit_finalize_apps_rg(
        sealed,
        fec=fec,
        target_company=str(state_diff.get("target_company", "")),
        target_role=str(state_diff.get("target_role", "")),
    )


APPS_RG_EXIT_CERT_REF: str = "exit-apps-rg-resume-generation-w3p5"

try:
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition  # noqa: F401
except ImportError:
    X3Disposition = None  # type: ignore[assignment,misc]


@dataclass(frozen=True)
class AppsRgGateResult:
    gate_id: str
    verdict: str
    reason: str = ""


ExitBindingResult = ExitResult


def _resolve_repo_root() -> "Any":
    from pathlib import Path

    return Path(__file__).resolve().parents[4]


def _safe_run_dirname(run_id: str) -> str:
    return run_id.replace("/", "_").replace("\\", "_")


def _build_artifact_commit_candidate(
    artifact_type: str,
    proposed_path: str,
    content_digest: str,
    serialized_content: dict,
) -> InertArtifactCommitCandidate:
    return InertArtifactCommitCandidate(
        artifact_type=artifact_type,
        proposed_path=proposed_path,
        content_digest=content_digest,
        serialized_content=serialized_content,
    )


def extract_apps_rg_exit_gate_policy() -> dict:
    return {
        "required_gates": ["G21", "G22", "G23", "G24", "G26", "G28"],
        "conditional_gates": ["G25", "G27"],
        "blocking_verdicts": ["FAIL"],
    }


def produce_structured_resume_from_docx(docx_path: str) -> dict:
    try:
        from apps_rg.resume.docx_reader import read_structured_resume_from_docx

        return read_structured_resume_from_docx(docx_path)
    except Exception:  # guardian: allow-broad-exception -- optional parse boundary
        return {"source_path": docx_path, "sections": {}, "_parse_error": True}


__all__ = [
    "APPS_RG_EXIT_CERT_REF",
    "_BLOCKING_SUPPORT_STATUSES",
    "_build_artifact_commit_candidate",
    "_compute_apps_rg_owned_fields",
    "_evaluate_c0_evidence_gates",
    "_evaluate_l5_certification_gate",
    "_evaluate_judge_reliability_gate",
    "_resolve_judge_reliability_gate",
    "_resolve_repo_root",
    "_safe_run_dirname",
    "AppsRgGateResult",
    "ExitBindingResult",
    "ExitDisposition",
    "ExitGateResult",
    "ExitGateVerdict",
    "ExitResult",
    "InertArtifactCommitCandidate",
    "X3Disposition",
    "build_apps_rg_exit_harness",
    "build_exhaust_bundle_from_exit",
    "exit_finalize_apps_rg",
    "extract_apps_rg_exit_gate_policy",
    "produce_structured_resume_from_docx",
]
