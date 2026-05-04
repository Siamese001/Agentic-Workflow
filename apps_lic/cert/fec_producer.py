"""apps_lic FEC producer - cold-outreach grounded variant.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W2.P1.

apps_lic generates cold-outreach messages grounded against profile data,
outreach templates, and compliance rules. Its evidence_required rubric
dims are audience_fit, personalization_integrity, compliance, and
brevity_and_channel_fit. The producer surfaces:

  - profile_data_sources: retrieval sources used to ground personalization
  - outreach_template_ids: deterministic template ids consumed
  - compliance_check_status: whether compliance rules ran clean

Authority: READ-ONLY. Never mutates run_context. Returns a fresh dict.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.1"
_PRODUCER_ID = "apps_lic.cert.fec_producer"


def _safe_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _safe_list_str(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a FEC-shaped dict from apps_lic's run_context."""
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id"))
    if not route_id:
        rc = ctx.get("route_contract")
        if isinstance(rc, Mapping):
            route_id = _safe_str(rc.get("route_id"))

    profile_data_sources = _safe_list_str(ctx.get("profile_data_sources"))
    outreach_template_ids = _safe_list_str(ctx.get("template_ids")) or _safe_list_str(
        ctx.get("outreach_template_ids")
    )
    compliance_check_status = _safe_str(
        ctx.get("compliance_check_status"), default="not_run"
    )

    explicit_grounded = ctx.get("grounded")
    if isinstance(explicit_grounded, bool):
        grounded = explicit_grounded
    else:
        grounded = bool(profile_data_sources)

    if grounded and compliance_check_status == "passed":
        sufficiency = "grounded"
    elif grounded:
        sufficiency = "grounded_compliance_pending"
    elif outreach_template_ids:
        sufficiency = "template_only"
    else:
        sufficiency = "empty"

    # v1.1 fields — C0 bundle / JD context integration
    jd_context = ctx.get("jd_context") or {}
    if isinstance(jd_context, Mapping):
        jd_present = bool(jd_context)
        jd_ref = _safe_str(jd_context.get("jd_ref"))
        jd_content_hash = jd_context.get("jd_content_hash")
    else:
        jd_present = False
        jd_ref = ""
        jd_content_hash = None

    c0_bundle = ctx.get("c0_bundle") or {}
    claim_evidence_map = c0_bundle.get("claim_evidence_map") or {} if isinstance(c0_bundle, Mapping) else {}
    freshness_report = c0_bundle.get("freshness_report") or {} if isinstance(c0_bundle, Mapping) else {}

    freshness_violations = int(freshness_report.get("violation_count", 0)) if isinstance(freshness_report, Mapping) else 0
    unsupported_claim_count = int(claim_evidence_map.get("unsupported_claim_count", 0)) if isinstance(claim_evidence_map, Mapping) else 0
    jd_unsupported_claim_count = int(claim_evidence_map.get("jd_unsupported_claim_count", 0)) if isinstance(claim_evidence_map, Mapping) else 0
    jd_to_company_evidence_map_present = bool(
        claim_evidence_map.get("jd_to_company_evidence_map_present", False)
    ) if isinstance(claim_evidence_map, Mapping) else False

    citation_anchor_count = int(ctx.get("citation_anchor_count", len(profile_data_sources)))
    research_depth_profile = _safe_str(ctx.get("research_depth_profile"))

    # apps_lic: outreach overlay is present when JD + profile data are both available
    recruiter_outreach_overlay_present = jd_present and bool(profile_data_sources)

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": profile_data_sources,
        "template_ids": outreach_template_ids,
        "route_id": route_id,
        "evidence_sufficiency": sufficiency,
        "compliance_check_status": compliance_check_status,
        # v1.1 fields
        "research_depth_profile": research_depth_profile,
        "jd_present": jd_present,
        "jd_ref": jd_ref,
        "jd_content_hash": jd_content_hash,
        "freshness_violations": freshness_violations,
        "unsupported_claim_count": unsupported_claim_count,
        "jd_unsupported_claim_count": jd_unsupported_claim_count,
        "jd_to_company_evidence_map_present": jd_to_company_evidence_map_present,
        "citation_anchor_count": citation_anchor_count,
        "recruiter_outreach_overlay_present": recruiter_outreach_overlay_present,
    }


__all__ = ["produce_fec"]
