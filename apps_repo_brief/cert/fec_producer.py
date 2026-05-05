"""apps_repo_brief FEC producer — builds FinalEvidenceContract dict.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P1.11
Pattern source: apps_exec/cert/fec_producer.py (canonical predecessor).

apps_repo_brief is R3_SIMPLE_GROUNDED_READ with mandatory C0 retrieval.
The FEC producer surfaces C0 retrieval sources, template ids, and the
canonical route id. When C0 retrieval is wired (W3), grounded=True
automatically from c0_retrieval_sources being non-empty.

Shape
-----
    {
        "schema_version": "1.0",
        "producer": "apps_repo_brief.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<snippet_id>, ...],
        "template_ids": ["repo_brief_v1"],
        "route_id": "apps_repo_brief.executive_brief_v1",
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
        "source_collection": "repo_brief_docs",
    }

Source extraction ladder (defensive, READ-ONLY):
1. ``run_context["c0_retrieval_sources"]`` (authoritative C0 output, W3+).
2. ``run_context["research_snippets"]`` — legacy snippet ids.
3. Empty → template_only with default template id.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_repo_brief.cert.fec_producer"
_DEFAULT_ROUTE = "apps_repo_brief.executive_brief_v1"
_DEFAULT_TEMPLATE_IDS = ("repo_brief_v1",)
_SOURCE_COLLECTION = "repo_brief_docs"


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item)]


def _safe_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


_FEC_PRODUCER_RETIRED = (
    "apps_repo_brief.cert.fec_producer.produce_fec is RETIRED (W4 P4.5). "
    "Authoritative FEC.v1 is minted by C0 only (P3.7). "
    "Use apps_repo_brief.cert.cert_projection_adapter.CertProjectionAdapter "
    "to project C0 FEC fields for Exit pipeline consumption. "
    "This function will raise RuntimeError in W5."
)


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    _LOGGER.warning(_FEC_PRODUCER_RETIRED)
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id")) or _DEFAULT_ROUTE
    rc = ctx.get("route_contract")
    if isinstance(rc, Mapping):
        route_id = _safe_str(rc.get("route_id"), route_id) or route_id

    template_ids = _safe_list(ctx.get("template_ids")) or list(_DEFAULT_TEMPLATE_IDS)

    retrieval_sources = _safe_list(ctx.get("c0_retrieval_sources"))
    if not retrieval_sources:
        retrieval_sources = _safe_list(ctx.get("research_snippets"))

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
        "source_collection": _SOURCE_COLLECTION,
    }


__all__ = ["produce_fec"]
