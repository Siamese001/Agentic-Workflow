"""apps_rg FEC producer - resume-generation grounded variant.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W3.P1.

apps_rg generates resumes grounded against job description evidence, role
evidence, and repository signals. Its evidence_required rubric dims are
factual_grounding, role_alignment, executive_positioning, specificity, and
one additional dim. The producer surfaces three source ladders:

  - jd_evidence_sources: retrieval sources from the job description
  - role_evidence_sources: retrieval sources from prior role evidence
  - repo_signal_sources: retrieval sources from repository signals

Authority: READ-ONLY. Never mutates run_context. Returns a fresh dict.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.1"
_PRODUCER_ID = "apps_rg.cert.fec_producer"


def _safe_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _safe_list_str(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a FEC-shaped dict from apps_rg's run_context."""
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id"))
    if not route_id:
        rc = ctx.get("route_contract")
        if isinstance(rc, Mapping):
            route_id = _safe_str(rc.get("route_id"))

    jd_sources = _safe_list_str(ctx.get("jd_evidence_sources"))
    role_sources = _safe_list_str(ctx.get("role_evidence_sources"))
    repo_sources = _safe_list_str(ctx.get("repo_signal_sources"))

    # Aggregate retrieval surface for X1D consumption
    all_retrieval = list(jd_sources) + list(role_sources) + list(repo_sources)
    template_ids = _safe_list_str(ctx.get("template_ids"))

    explicit_grounded = ctx.get("grounded")
    if isinstance(explicit_grounded, bool):
        grounded = explicit_grounded
    else:
        # apps_rg requires at least JD + (role OR repo) evidence to be grounded
        grounded = bool(jd_sources) and bool(role_sources or repo_sources)

    if grounded:
        sufficiency = "grounded"
    elif jd_sources or role_sources or repo_sources:
        sufficiency = "partial"
    elif template_ids:
        sufficiency = "template_only"
    else:
        sufficiency = "empty"

    # W3.P2 (apps-rg-spine-deferred-followup-d4e7b2): enrichment fields
    prompt_bom_hashes = _safe_list_str(ctx.get("prompt_bom_hashes"))
    cache_hit_type = _safe_str(ctx.get("cache_hit_type"), default="none")
    e5_seal_hash = _safe_str(ctx.get("e5_seal_hash"))
    intent_hash = _safe_str(ctx.get("intent_hash"))

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
    jd_to_company_evidence_map_present = bool(claim_evidence_map.get("jd_to_company_evidence_map_present", False)) if isinstance(claim_evidence_map, Mapping) else False

    # citation_anchor_count: count from jd+role+repo sources or explicit override
    citation_anchor_count = int(ctx.get("citation_anchor_count", len(all_retrieval)))

    # recruiter_outreach_overlay_present: apps_rg always surfaces outreach overlay when JD present
    recruiter_outreach_overlay_present = jd_present and bool(role_sources or repo_sources)

    # research_depth_profile: optional depth tier for this run
    research_depth_profile = _safe_str(ctx.get("research_depth_profile"))

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": all_retrieval,
        "template_ids": template_ids,
        "route_id": route_id,
        "evidence_sufficiency": sufficiency,
        "source_ladder": {
            "jd_evidence_sources": jd_sources,
            "role_evidence_sources": role_sources,
            "repo_signal_sources": repo_sources,
        },
        "prompt_bom_hashes": prompt_bom_hashes,
        "cache_hit_type": cache_hit_type,
        "e5_seal_hash": e5_seal_hash,
        "intent_hash": intent_hash,
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
