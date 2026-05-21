"""apps_rg per-run C0 metrics artifact writer.

W3: Produces a durable c0_metrics.json artifact for each run.
W3 invariant: PARTIAL support_status is coerced to UNKNOWN before storage.

No agentic_core imports for app-specific logic — this module uses the
generic extractor from agentic_core.runtime.c0.evidence_metrics_extractor
and adds apps_rg-specific serialisation around it.

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W3
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
)
from agentic_core.runtime.c0.evidence_metrics_extractor import (
    SupportTarget,
    extract_evidence_metrics,
)
from apps_rg.runtime.profiles.retrieval_requirements import get_normative_source_classes
from apps_rg.runtime.bindings.briefing_mode_classifier import (
    BRIEFING_MODE_NONE,
    _VALID_BRIEFING_MODES,
    BriefingModeDecision,
)

_logger = logging.getLogger(__name__)

SCHEMA_VERSION: str = "c0_metrics.v1"

# Default apps_rg support target (driven by profile)
_DEFAULT_SUPPORT_TARGET = SupportTarget.from_prefix_list(
    ["jd_payload", "resume_payload"],
    label="apps_rg_default",
)

# Statuses that W3 coerces to UNKNOWN before writing (PARTIAL is not canonical)
_COERCE_TO_UNKNOWN: frozenset[str] = frozenset({"PARTIAL", "WEAK"})

# Canonical retrieval mode set (mirrors briefing_mode_classifier._VALID_BRIEFING_MODES + UNKNOWN)
_VALID_RETRIEVAL_MODES: frozenset[str] = _VALID_BRIEFING_MODES | frozenset({"UNKNOWN"})


def _coerce_support_status(status: str) -> str:
    """Coerce non-canonical support statuses before writing to artifact."""
    if status in _COERCE_TO_UNKNOWN:
        return STATUS_UNKNOWN
    return status


def _coerce_retrieval_mode(mode: Optional[str]) -> str:
    """Coerce non-canonical retrieval modes to UNKNOWN."""
    if mode in _VALID_RETRIEVAL_MODES:
        return mode
    return "UNKNOWN"


def _compute_evidence_digest(fec: FinalEvidenceContract) -> str:
    """Compute a deterministic SHA-256 digest from evidence content.

    The digest is derived from evidence item (source, content) pairs sorted
    by source so that insertion order does not affect the result.

    When there are no evidence items the digest is SHA-256 of the empty
    string (``sha256(b"").hexdigest()``), so callers can detect an empty
    FEC via the well-known sentinel ``e3b0c44298fc...``.
    """
    items: list[tuple[str, str]] = sorted(
        (getattr(item, "source", ""), getattr(item, "content", ""))
        for item in (getattr(fec, "evidence_items", None) or ())
    )
    if not items:
        return hashlib.sha256(b"").hexdigest()
    payload = json.dumps(items, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_empty_fec(
    run_id: str = "empty",
    support_status: str = SUPPORT_STATUS_EMPTY,
) -> FinalEvidenceContract:
    """Create a minimal empty FEC with the given support_status.

    Defaults to EMPTY status.  Used when no evidence could be retrieved at all.
    """
    return FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        evidence_items=(),
        retrieval_sources=(),
        support_target_met=False,
        support_status=support_status,
        l5_certification_ref="c0-empty-fec-stub",
    )


def build_c0_metrics(
    fec: Optional[FinalEvidenceContract],
    run_id: str,
    route_id: str,
    retrieval_mode: Optional[str] = None,
    briefing_source_type: Optional[str] = None,
    company_brief_provenance: Optional[Any] = None,
    briefing_decision: Optional[BriefingModeDecision] = None,
    support_target: Optional[SupportTarget] = None,
) -> dict[str, Any]:
    """Build the c0_metrics dict for a run without writing to disk.

    Parameters
    ----------
    fec:
        The FinalEvidenceContract for this run.  If None, an empty FEC is
        substituted.
    run_id:
        The run identifier.
    route_id:
        The routing decision identifier (e.g. "R0").
    retrieval_mode:
        Explicit retrieval mode string.  Non-canonical values are coerced to
        ``"UNKNOWN"``.  Overrides ``briefing_decision`` if supplied.
    briefing_source_type:
        Explicit briefing source type string.  Defaults to ``retrieval_mode``
        when omitted.
    company_brief_provenance:
        Provenance dict (or None) for the company brief.  Overrides
        ``briefing_decision`` when supplied.
    briefing_decision:
        Legacy briefing mode decision from the classifier.  Ignored when
        ``retrieval_mode`` is provided.
    support_target:
        Optional caller-supplied SupportTarget.  Defaults to the apps_rg
        profile-driven target (jd_payload + resume_payload).

    Returns
    -------
    dict[str, Any]
        A JSON-serialisable metrics dict with all required schema keys.
    """
    if fec is None:
        fec = make_empty_fec(run_id)

    target = support_target or _DEFAULT_SUPPORT_TARGET
    metrics = extract_evidence_metrics(fec, target)

    # Coerce support_status (W3: PARTIAL → UNKNOWN)
    support_status = _coerce_support_status(metrics.support_status)

    # Compute deterministic digest
    final_evidence_digest = _compute_evidence_digest(fec)

    # Resolve retrieval_mode / briefing_source_type / company_brief_provenance.
    # Direct kwargs take precedence over briefing_decision.
    if retrieval_mode is not None:
        resolved_retrieval_mode = _coerce_retrieval_mode(retrieval_mode)
        resolved_briefing_source_type = (
            briefing_source_type if briefing_source_type is not None
            else resolved_retrieval_mode
        )
        resolved_provenance = company_brief_provenance
    elif briefing_decision is not None:
        resolved_retrieval_mode = briefing_decision.retrieval_mode
        resolved_briefing_source_type = briefing_decision.briefing_source_type
        resolved_provenance = briefing_decision.company_brief_provenance
        if company_brief_provenance is not None:
            resolved_provenance = company_brief_provenance
    else:
        resolved_retrieval_mode = "UNKNOWN"
        resolved_briefing_source_type = briefing_source_type or "UNKNOWN"
        resolved_provenance = company_brief_provenance

    # Source class coverage: which normative classes are present?
    normative_classes = get_normative_source_classes()
    present_prefixes = {
        src.split(":", 1)[0] if ":" in src else src
        for src in metrics.retrieval_sources
    }
    source_class_coverage = {
        cls: (cls in present_prefixes) for cls in normative_classes
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "route_id": route_id,
        "retrieval_mode": resolved_retrieval_mode,
        "briefing_source_type": resolved_briefing_source_type,
        "company_brief_provenance": resolved_provenance,
        "source_class_coverage": source_class_coverage,
        "support_status": support_status,
        "support_target_met": metrics.support_target_met,
        "evidence_counts": {
            "total": metrics.evidence_count,
            "excluded": len(metrics.excluded_evidence_refs),
            "blocked": len(metrics.blocked_source_refs),
        },
        "retrieval_sources": list(metrics.retrieval_sources),
        "excluded_evidence_refs": list(metrics.excluded_evidence_refs),
        "blocked_source_refs": list(metrics.blocked_source_refs),
        "freshness_receipts": list(metrics.freshness_receipts),
        "citation_map": [list(pair) for pair in metrics.citation_map],
        "support_score_profile": metrics.support_score_profile,
        "final_evidence_digest": final_evidence_digest,
        "coercion_warnings": list(metrics.coercion_warnings),
    }


def write_c0_metrics(
    fec: Optional[FinalEvidenceContract],
    run_id: str,
    route_id: str,
    runs_root: Optional[Path] = None,
    retrieval_mode: Optional[str] = None,
    briefing_source_type: Optional[str] = None,
    company_brief_provenance: Optional[Any] = None,
    briefing_decision: Optional[BriefingModeDecision] = None,
    support_target: Optional[SupportTarget] = None,
) -> Optional[Path]:
    """Build and write c0_metrics.json to disk.

    Writes to ``<runs_root>/<run_id>/c0_metrics.json``.  Creates the
    directory if needed.  Fail-soft — returns None on any I/O error.

    Parameters
    ----------
    fec:
        FinalEvidenceContract for this run.
    run_id:
        Run identifier; used as the sub-directory name.
    route_id:
        Routing identifier.
    runs_root:
        Root directory for run artifacts.  Defaults to
        ``artifacts/apps_rg/runs`` relative to repo root.
    retrieval_mode:
        Explicit retrieval mode string.
    briefing_source_type:
        Explicit briefing source type string.
    company_brief_provenance:
        Provenance dict or None.
    briefing_decision:
        Optional briefing mode decision (legacy path).
    support_target:
        Optional caller-supplied SupportTarget.

    Returns
    -------
    Path | None
        Path of the written file, or None on failure.
    """
    try:
        if runs_root is None:
            repo_root = Path(__file__).parents[4]
            runs_root = repo_root / "artifacts" / "apps_rg" / "runs"

        run_dir = runs_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = run_dir / "c0_metrics.json"

        data = build_c0_metrics(
            fec=fec,
            run_id=run_id,
            route_id=route_id,
            retrieval_mode=retrieval_mode,
            briefing_source_type=briefing_source_type,
            company_brief_provenance=company_brief_provenance,
            briefing_decision=briefing_decision,
            support_target=support_target,
        )
        artifact_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return artifact_path
    except Exception as exc:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        _logger.warning("write_c0_metrics failed (fail-soft): %s", exc)
        return None


__all__ = [
    "SCHEMA_VERSION",
    "build_c0_metrics",
    "make_empty_fec",
    "write_c0_metrics",
]
