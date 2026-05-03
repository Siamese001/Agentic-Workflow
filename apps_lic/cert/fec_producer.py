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

_SCHEMA_VERSION = "1.0"
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

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": profile_data_sources,
        "template_ids": outreach_template_ids,
        "route_id": route_id,
        "evidence_sufficiency": sufficiency,
        "compliance_check_status": compliance_check_status,
    }


__all__ = ["produce_fec"]
