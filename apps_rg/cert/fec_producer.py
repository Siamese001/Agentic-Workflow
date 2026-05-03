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

_SCHEMA_VERSION = "1.0"
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
    }


__all__ = ["produce_fec"]
