"""apps_rfp FEC producer — builds FinalEvidenceContract dict.

Plan: ``.windsurf/plans/apps-rfp-c0-fec-producer-wiring-b9d4f1.md`` W1.P1.

Pattern source: ``apps_qna/cert/fec_producer.py``. apps_rfp is a hop
proposal-assembly pipeline; FEC surfaces RFP document sections cited by
the proposal assembly, proposal-template ids, and the cert route id.

Shape
-----
    {
        "schema_version": "1.0",
        "producer": "apps_rfp.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<section_anchor | rfp_doc_id>, ...],
        "template_ids": ["proposal_assembly_v1"],
        "route_id": "apps_rfp.proposal_assembly_v1",
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
    }

Source ladder (defensive, READ-ONLY):

1. ``run_context["c0_retrieval_sources"]`` — explicit override.
2. ``run_context["rfp_sections_cited"]`` — list[str].
3. ``run_context["proposal_result"].sections_cited`` — attribute on result.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_rfp.cert.fec_producer"
_DEFAULT_ROUTE = "apps_rfp.proposal_assembly_v1"
_DEFAULT_TEMPLATE_IDS = ("proposal_assembly_v1",)


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item)]


def _safe_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _extract_result_sections(result: Any) -> list[str]:
    for attr in ("sections_cited", "citations", "rfp_sections"):
        value = getattr(result, attr, None)
        if isinstance(value, (list, tuple)):
            return [str(v) for v in value if isinstance(v, (str, int, float)) and str(v)]
    return []


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id")) or _DEFAULT_ROUTE
    rc = ctx.get("route_contract")
    if isinstance(rc, Mapping):
        route_id = _safe_str(rc.get("route_id"), route_id) or route_id

    template_ids = _safe_list(ctx.get("template_ids")) or list(_DEFAULT_TEMPLATE_IDS)

    retrieval_sources = _safe_list(ctx.get("c0_retrieval_sources"))
    if not retrieval_sources:
        retrieval_sources = _safe_list(ctx.get("rfp_sections_cited"))
    if not retrieval_sources:
        result = ctx.get("proposal_result")
        if result is not None:
            retrieval_sources = _extract_result_sections(result)

    seen: set[str] = set()
    deduped: list[str] = []
    for src in retrieval_sources:
        if src not in seen:
            deduped.append(src)
            seen.add(src)
    retrieval_sources = deduped

    explicit_grounded = ctx.get("grounded")
    grounded = (
        explicit_grounded if isinstance(explicit_grounded, bool) else bool(retrieval_sources)
    )
    if grounded:
        sufficiency = "grounded"
    elif template_ids:
        sufficiency = "template_only"
    else:
        sufficiency = "empty"

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": retrieval_sources,
        "template_ids": template_ids,
        "route_id": route_id,
        "evidence_sufficiency": sufficiency,
    }


__all__ = ["produce_fec"]
