"""Final Evidence Contract (FEC) Producer for apps_lic.

Wave 7 (W7) upgrade: schema_version 1.1 — adds JD overlay fields,
c0_bundle claim-evidence fields, and recruiter outreach overlay flag.

Pattern Source: apps-qna-c0-fec-producer-wiring-d4f1e8 (established pattern)
"""

from __future__ import annotations

from typing import Any

# Schema version for this FEC producer
FEC_SCHEMA_VERSION = "1.1"

# Producer identifier
PRODUCER_ID = "apps_lic.cert.fec_producer"


# -----------------------------------------------------------------------------
# FEC Producer
# -----------------------------------------------------------------------------

def produce_fec(run_context: dict[str, Any] | None) -> dict[str, Any]:
    """Produce Final Evidence Contract for apps_lic (schema v1.1).

    v1.1 adds JD overlay fields, c0_bundle claim-evidence fields,
    recruiter outreach overlay flag, and research depth profile.

    Parameters
    ----------
    run_context : dict[str, Any] | None
        The run context. Safe to call with None or partial dicts.
        Expected keys:
        - profile_data_sources: list[str] — populated sources signal grounding
        - compliance_check_status: str — "passed" / "failed" / "not_run"
        - template_ids: list[str]
        - route_id: str
        - jd_context: dict — optional JD overlay {jd_ref, jd_content_hash}
        - c0_bundle: dict — optional c0 evidence bundle
        - context_signals: dict — optional context freshness signals
    """
    # Safe context handling — never raise on bad inputs
    if not isinstance(run_context, dict):
        run_context = {}

    # Grounding: profile_data_sources list signals retrieved evidence
    raw_sources = run_context.get("profile_data_sources", [])
    if not isinstance(raw_sources, (list, tuple)):
        raw_sources = []
    retrieval_sources: list[str] = [str(s) for s in raw_sources if s]

    grounded: bool = len(retrieval_sources) > 0

    # Compliance
    compliance_status: str = str(run_context.get("compliance_check_status", "not_run"))
    if compliance_status not in ("passed", "failed", "not_run", "pending"):
        compliance_status = "not_run"

    # Evidence sufficiency
    if not run_context:
        evidence_sufficiency = "empty"
    elif grounded and compliance_status == "pending":
        evidence_sufficiency = "grounded_compliance_pending"
    elif grounded:
        evidence_sufficiency = "grounded"
    else:
        evidence_sufficiency = "template_only"

    # Template IDs
    raw_tids = run_context.get("template_ids", [])
    template_ids: list[str] = list(raw_tids) if isinstance(raw_tids, (list, tuple)) else []

    # Route ID
    route_id: str = str(run_context.get("route_id", ""))

    # ── v1.1: JD overlay fields ────────────────────────────────────────────
    jd_ctx: dict[str, Any] = run_context.get("jd_context") or {}
    if not isinstance(jd_ctx, dict):
        jd_ctx = {}
    jd_present: bool = bool(jd_ctx)
    jd_ref: str | None = jd_ctx.get("jd_ref") or None
    jd_content_hash: str | None = jd_ctx.get("jd_content_hash") or None
    recruiter_outreach_overlay_present: bool = jd_present

    # ── v1.1: c0_bundle claim-evidence fields ─────────────────────────────
    c0_bundle: dict[str, Any] = run_context.get("c0_bundle") or {}
    if not isinstance(c0_bundle, dict):
        c0_bundle = {}
    claim_evidence = c0_bundle.get("claim_evidence_map") or {}
    if not isinstance(claim_evidence, dict):
        claim_evidence = {}
    unsupported_claim_count: int = int(claim_evidence.get("unsupported_claim_count", 0))
    jd_unsupported_claim_count: int = int(claim_evidence.get("jd_unsupported_claim_count", 0))
    jd_to_company_evidence_map_present: bool = bool(
        claim_evidence.get("jd_to_company_evidence_map_present", False)
    )

    freshness_report = c0_bundle.get("freshness_report") or {}
    if not isinstance(freshness_report, dict):
        freshness_report = {}
    freshness_violations: int = int(freshness_report.get("violation_count", 0))

    # ── v1.1: citation anchor + depth profile ─────────────────────────────
    citation_anchor_count: int = int(run_context.get("citation_anchor_count", 0))
    research_depth_profile: str = str(run_context.get("research_depth_profile", "standard"))

    fec: dict[str, Any] = {
        "schema_version": FEC_SCHEMA_VERSION,
        "producer": PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": retrieval_sources,
        "template_ids": template_ids,
        "route_id": route_id,
        "evidence_sufficiency": evidence_sufficiency,
        "compliance_check_status": compliance_status,
        # v1.1 JD overlay
        "jd_present": jd_present,
        "jd_ref": jd_ref,
        "recruiter_outreach_overlay_present": recruiter_outreach_overlay_present,
        # v1.1 c0_bundle claim evidence
        "unsupported_claim_count": unsupported_claim_count,
        "jd_unsupported_claim_count": jd_unsupported_claim_count,
        "jd_to_company_evidence_map_present": jd_to_company_evidence_map_present,
        "freshness_violations": freshness_violations,
        # v1.1 citation + depth
        "citation_anchor_count": citation_anchor_count,
        "research_depth_profile": research_depth_profile,
    }
    if jd_content_hash is not None:
        fec["jd_content_hash"] = jd_content_hash

    return fec


# -----------------------------------------------------------------------------
# Side-Effect Registration
# -----------------------------------------------------------------------------

def register() -> None:
    """Register this FEC producer with the apps_shared registry.

    Called as a side-effect when apps_lic.cert is imported.
    """
    try:
        from apps_shared.cert.fec_producer import register_producer
        register_producer("apps_lic", produce_fec)
    except ImportError:
        pass


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "produce_fec",
    "register",
    "PRODUCER_ID",
    "FEC_SCHEMA_VERSION",
]
