"""apps_exec FEC producer — builds FinalEvidenceContract dict.

Plan: ``.windsurf/plans/apps-exec-c0-fec-producer-wiring-c2e8a5.md`` W1.P1.

Pattern source: ``apps_qna/cert/fec_producer.py``. apps_exec is a
deterministic single-step execution app (brief assembly for executive
content); FEC surfaces research snippets used by the brief, the
brief-template id, and route id.

Shape
-----
    {
        "schema_version": "1.0",
        "producer": "apps_exec.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<snippet_id>, ...],
        "template_ids": ["exec_brief_v1"],
        "route_id": "apps_exec.execution_v1",
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
    }

Source extraction ladder (defensive, READ-ONLY):

1. ``run_context["c0_retrieval_sources"]`` (forward-compat override).
2. ``run_context["research_snippets"]`` — list of snippet ids.
3. Empty → ``template_only`` with default template id.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_exec.cert.fec_producer"
_DEFAULT_ROUTE = "apps_exec.execution_v1"
_DEFAULT_TEMPLATE_IDS = ("exec_brief_v1",)


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item)]


def _safe_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id")) or _DEFAULT_ROUTE
    rc = ctx.get("route_contract")
    if isinstance(rc, Mapping):
        route_id = _safe_str(rc.get("route_id"), route_id) or route_id

    template_ids = _safe_list(ctx.get("template_ids")) or list(_DEFAULT_TEMPLATE_IDS)

    retrieval_sources = _safe_list(ctx.get("c0_retrieval_sources"))
    if not retrieval_sources:
        retrieval_sources = _safe_list(ctx.get("research_snippets"))

    # De-dup preserve order.
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
