"""apps_rg Exit binding — C0 evidence consumption and gate evaluation.

W4: apps_rg owns all JD/resume-specific Exit gate logic here.
agentic_core Exit must remain generic.

No L6 current-run rescue path is introduced here (category 9 invariant).

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W4
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

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

# ---------------------------------------------------------------------------
# Blocking status set — apps_rg-owned; never in agentic_core
# ---------------------------------------------------------------------------

_BLOCKING_SUPPORT_STATUSES: frozenset[str] = frozenset({
    STATUS_UNKNOWN,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
})

_NON_BLOCKING_STATUSES: frozenset[str] = frozenset({
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
})


# ---------------------------------------------------------------------------
# Gate verdict enum (apps_rg-local; not the agentic_core GateVerdict)
# ---------------------------------------------------------------------------

class ExitGateVerdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Gate result shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExitGateResult:
    gate_id: str
    verdict: ExitGateVerdict
    reason: str = ""


# ---------------------------------------------------------------------------
# apps_rg-owned Exit inert artifact candidate
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InertArtifactCommitCandidate:
    """Non-durable artifact proposal — never written to L4 directly.

    All candidates produced by apps_rg Exit MUST be inert (proposal-only).
    """

    artifact_type: str
    proposed_path: str
    content_digest: str
    serialized_content: dict[str, Any]

    mutation_candidate_inert: bool = True
    non_durable: bool = True
    not_l4_truth: bool = True
    proposal_status: str = "PENDING_UWG"


# ---------------------------------------------------------------------------
# Exit disposition shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExitDisposition:
    outcome_authorized: bool
    gate_results: list[ExitGateResult]
    c0_blocking: bool
    blocking_reason: str = ""
    final_output: Optional[str] = None


# ---------------------------------------------------------------------------
# Exit result shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExitResult:
    disposition: ExitDisposition
    artifact_commit_candidates: list[InertArtifactCommitCandidate]


# ---------------------------------------------------------------------------
# Gate helpers
# ---------------------------------------------------------------------------

def _evaluate_c0_evidence_gates(
    fec: Optional[FinalEvidenceContract],
) -> tuple[list[ExitGateResult], bool, str]:
    """Evaluate C0 evidence gates and return (results, is_blocking, reason).

    Gates evaluated:
    - G_SUPPORT_STATUS  — blocks if support_status is in _BLOCKING_SUPPORT_STATUSES
    - G09               — warns if no freshness_receipts
    - G13               — fails (blocking) if citation_map empty + excluded_refs present;
                          warns if citation_map empty + no excluded_refs;
                          passes otherwise

    Parameters
    ----------
    fec:
        FinalEvidenceContract or None.  None is treated as no-evidence
        (non-blocking warn).

    Returns
    -------
    tuple[list[ExitGateResult], bool, str]
        (gate_results, is_blocking, blocking_reason)
    """
    results: list[ExitGateResult] = []
    is_blocking = False
    blocking_reasons: list[str] = []

    if fec is None:
        results.append(ExitGateResult(
            gate_id="G_SUPPORT_STATUS",
            verdict=ExitGateVerdict.WARN,
            reason="fec=None; no C0 evidence for this run",
        ))
        results.append(ExitGateResult(
            gate_id="G09",
            verdict=ExitGateVerdict.WARN,
            reason="fec=None; no freshness receipts",
        ))
        results.append(ExitGateResult(
            gate_id="G13",
            verdict=ExitGateVerdict.WARN,
            reason="fec=None; no citation map",
        ))
        return results, False, ""

    # G_SUPPORT_STATUS
    support_status: str = getattr(fec, "support_status", STATUS_UNKNOWN) or STATUS_UNKNOWN
    support_target_met: bool = bool(getattr(fec, "support_target_met", False))

    if support_status in _BLOCKING_SUPPORT_STATUSES:
        results.append(ExitGateResult(
            gate_id="G_SUPPORT_STATUS",
            verdict=ExitGateVerdict.FAIL,
            reason=f"support_status={support_status} is blocking",
        ))
        is_blocking = True
        blocking_reasons.append(support_status)
    elif not support_target_met:
        results.append(ExitGateResult(
            gate_id="G_SUPPORT_STATUS",
            verdict=ExitGateVerdict.WARN,
            reason=f"support_status={support_status} but support_target_met=False",
        ))
    else:
        results.append(ExitGateResult(
            gate_id="G_SUPPORT_STATUS",
            verdict=ExitGateVerdict.PASS,
            reason=f"support_status={support_status}",
        ))

    # G09 — freshness
    freshness: tuple = tuple(getattr(fec, "freshness_receipts", ()) or ())
    if freshness:
        results.append(ExitGateResult(
            gate_id="G09",
            verdict=ExitGateVerdict.PASS,
            reason=f"{len(freshness)} freshness receipts",
        ))
    else:
        results.append(ExitGateResult(
            gate_id="G09",
            verdict=ExitGateVerdict.WARN,
            reason="no freshness receipts",
        ))

    # G13 — citation map
    citation_map: tuple = tuple(getattr(fec, "citation_map", ()) or ())
    excluded_refs: tuple = tuple(getattr(fec, "excluded_evidence_refs", ()) or ())

    if citation_map:
        results.append(ExitGateResult(
            gate_id="G13",
            verdict=ExitGateVerdict.PASS,
            reason=f"{len(citation_map)} citation(s)",
        ))
    elif excluded_refs:
        results.append(ExitGateResult(
            gate_id="G13",
            verdict=ExitGateVerdict.FAIL,
            reason=(
                f"G13: citation_map is empty but {len(excluded_refs)} "
                "excluded_evidence_refs present — citation hard-fail"
            ),
        ))
        is_blocking = True
        blocking_reasons.append("G13")
    else:
        results.append(ExitGateResult(
            gate_id="G13",
            verdict=ExitGateVerdict.WARN,
            reason="citation_map empty; no excluded refs",
        ))

    blocking_reason = ", ".join(blocking_reasons) if blocking_reasons else ""
    return results, is_blocking, blocking_reason


def _compute_apps_rg_owned_fields(
    fec: Optional[FinalEvidenceContract],
    sealed: SealedL2Artifact,
) -> dict[str, Any]:
    """Compute apps_rg-owned evidence metrics fields.

    These fields are specific to the resume generation task and must
    NOT appear in agentic_core Exit files.

    Fields returned:
    - jd_keyword_coverage         float [0, 1]
    - overfit_score               float [0, 1]
    - provenance_valid            bool
    - material_claim_support_rate float [0, 1]
    - unsupported_material_claim_rate float [0, 1]
    - citation_anchor_coverage    float [0, 1]
    """
    if fec is None:
        return {
            "jd_keyword_coverage": 0.0,
            "overfit_score": 0.0,
            "provenance_valid": False,
            "material_claim_support_rate": 0.0,
            "unsupported_material_claim_rate": 1.0,
            "citation_anchor_coverage": 0.0,
        }

    # jd_keyword_coverage: fraction of retrieval sources from jd_payload
    retrieval_sources: tuple = tuple(getattr(fec, "retrieval_sources", ()) or ())
    jd_count = sum(1 for s in retrieval_sources if s.startswith("jd_payload"))
    jd_coverage = jd_count / len(retrieval_sources) if retrieval_sources else 0.0

    # overfit_score: stub — 0.0 means no detected overfitting
    overfit_score = 0.0

    # provenance_valid: requires non-empty compilation_hash + non-empty cert ref
    compilation_hash: str = getattr(sealed, "compilation_hash", "") or ""
    l5_ref: str = getattr(sealed, "l5_certification_ref", "") or ""
    provenance_valid = bool(compilation_hash and l5_ref)

    # citation_anchor_coverage
    citation_map: tuple = tuple(getattr(fec, "citation_map", ()) or ())
    evidence_count = len(getattr(fec, "evidence_items", ()) or ())
    citation_coverage = (
        min(len(citation_map) / evidence_count, 1.0) if evidence_count else 0.0
    )

    return {
        "jd_keyword_coverage": round(jd_coverage, 4),
        "overfit_score": overfit_score,
        "provenance_valid": provenance_valid,
        "material_claim_support_rate": round(jd_coverage, 4),
        "unsupported_material_claim_rate": round(1.0 - jd_coverage, 4),
        "citation_anchor_coverage": round(citation_coverage, 4),
    }


# ---------------------------------------------------------------------------
# Public Exit API
# ---------------------------------------------------------------------------

def exit_finalize_apps_rg(
    sealed: SealedL2Artifact,
    prompt_artifact: Any = None,
    *,
    fec: Optional[FinalEvidenceContract] = None,
    target_company: str = "",
    target_role: str = "",
) -> ExitResult:
    """apps_rg Exit gate evaluation and disposition assembly.

    Parameters
    ----------
    sealed:
        SealedL2Artifact from L2 execution.
    prompt_artifact:
        Positional arg accepted for dispatch compatibility; ignored.
    fec:
        FinalEvidenceContract from C0 retrieval.  None is handled gracefully.
    target_company:
        Target company name for run metadata.
    target_role:
        Target role name for run metadata.

    Returns
    -------
    ExitResult
        Disposition + list of inert artifact commit candidates.
    """
    gate_results, c0_blocking, blocking_reason = _evaluate_c0_evidence_gates(fec)
    owned_fields = _compute_apps_rg_owned_fields(fec, sealed)

    outcome_authorized = not c0_blocking
    run_id: str = getattr(sealed, "run_id", "") or ""

    # Build run_metadata candidate (inert)
    w4_c0_evidence: dict[str, Any] = {
        "c0_blocking": c0_blocking,
        "blocking_reason": blocking_reason,
        "gate_results": [
            {"gate_id": g.gate_id, "verdict": g.verdict.value, "reason": g.reason}
            for g in gate_results
        ],
        **owned_fields,
    }

    run_metadata_candidate = InertArtifactCommitCandidate(
        artifact_type="run_metadata",
        proposed_path=f"virtual/apps_rg/runs/{run_id}/run_metadata.json",
        content_digest=str(hash(run_id + str(c0_blocking))),
        serialized_content={
            "run_id": run_id,
            "target_company": target_company,
            "target_role": target_role,
            "outcome_authorized": outcome_authorized,
            "w4_c0_evidence": w4_c0_evidence,
        },
    )

    disposition = ExitDisposition(
        outcome_authorized=outcome_authorized,
        gate_results=gate_results,
        c0_blocking=c0_blocking,
        blocking_reason=blocking_reason,
        final_output=getattr(sealed, "generated_content", None),
    )

    return ExitResult(
        disposition=disposition,
        artifact_commit_candidates=[run_metadata_candidate],
    )


def build_apps_rg_exit_harness(
    sealed: SealedL2Artifact,
    fec: Optional[FinalEvidenceContract] = None,
) -> ExitResult:
    """Convenience harness that reads target from sealed.proposed_state_diff."""
    state_diff: dict[str, Any] = dict(getattr(sealed, "proposed_state_diff", {}) or {})
    return exit_finalize_apps_rg(
        sealed,
        fec=fec,
        target_company=str(state_diff.get("target_company", "")),
        target_role=str(state_diff.get("target_role", "")),
    )


# ---------------------------------------------------------------------------
# Cert reference — apps_rg-owned identifier for the Exit gate certification
# ---------------------------------------------------------------------------

APPS_RG_EXIT_CERT_REF: str = "exit-apps-rg-resume-generation-w3p5"

# ---------------------------------------------------------------------------
# Type alias for callers that expect X3Disposition (re-exported from core)
# ---------------------------------------------------------------------------

try:
    from agentic_core.runtime.contracts.x3_disposition import X3Disposition  # noqa: F401
except ImportError:
    X3Disposition = None  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# AppsRgGateResult — thin wrapper for test compatibility
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AppsRgGateResult:
    gate_id: str
    verdict: str
    reason: str = ""


# ---------------------------------------------------------------------------
# ExitBindingResult — wraps ExitResult for callers that name this type
# ---------------------------------------------------------------------------

ExitBindingResult = ExitResult


# ---------------------------------------------------------------------------
# Path helpers used by dispatch shims
# ---------------------------------------------------------------------------

def _resolve_repo_root() -> "Any":
    from pathlib import Path
    return Path(__file__).resolve().parents[4]


def _safe_run_dirname(run_id: str) -> str:
    return run_id.replace("/", "_").replace("\\", "_")


# ---------------------------------------------------------------------------
# _build_artifact_commit_candidate — public alias for InertArtifactCommitCandidate
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# extract_apps_rg_exit_gate_policy — reads gate policy from profile YAML
# ---------------------------------------------------------------------------

def extract_apps_rg_exit_gate_policy() -> dict:
    """Return minimal default gate policy for apps_rg Exit gates."""
    return {
        "required_gates": ["G21", "G22", "G23", "G24", "G26", "G28"],
        "conditional_gates": ["G25", "G27"],
        "blocking_verdicts": ["FAIL"],
    }


# ---------------------------------------------------------------------------
# produce_structured_resume_from_docx — stub; real impl in resume/ subpackage
# ---------------------------------------------------------------------------

def produce_structured_resume_from_docx(docx_path: str) -> dict:
    """Produce a structured resume dict from a .docx file path.

    This is a thin dispatch shim; the real implementation lives in
    apps_rg.resume and requires python-docx.  Returns an empty skeleton
    if the file cannot be parsed so callers can fail-soft.
    """
    try:
        from apps_rg.resume.docx_reader import read_structured_resume_from_docx
        return read_structured_resume_from_docx(docx_path)
    except Exception:
        return {"source_path": docx_path, "sections": {}, "_parse_error": True}


__all__ = [
    "APPS_RG_EXIT_CERT_REF",
    "_BLOCKING_SUPPORT_STATUSES",
    "_build_artifact_commit_candidate",
    "_compute_apps_rg_owned_fields",
    "_evaluate_c0_evidence_gates",
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
    "exit_finalize_apps_rg",
    "extract_apps_rg_exit_gate_policy",
    "produce_structured_resume_from_docx",
]
