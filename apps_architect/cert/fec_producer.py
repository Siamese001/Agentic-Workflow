"""apps_architect FEC producer — builds FinalEvidenceContract dict.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W1.P2.

Pattern source: ``apps_research/cert/fec_producer.py``. apps_architect is a
pattern collection and repo hardening engine; FEC surfaces retrieval sources
from plans/rules/core_patterns, prompt-assembly template ids, and the cert
route id.

Shape
-----
    {
        "schema_version": "1.0",
        "producer": "apps_architect.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<source_id>, ...],
        "template_ids": [<template_id>, ...],
        "route_id": "apps_architect.pattern_scan_v1",
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
    }

Source ladder (defensive, READ-ONLY):

1. ``run_context["c0_retrieval_sources"]`` — explicit override.
2. ``run_context["pattern_sources"]`` — list[str] of source identifiers.
3. ``run_context["scan_result"].sources`` — attribute on scan result.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_architect.cert.fec_producer"
_DEFAULT_ROUTE = "apps_architect.pattern_scan_v1"
_DEFAULT_TEMPLATE_IDS = ("pattern_scan_v1",)


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item)]


def _safe_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _extract_result_sources(result: Any) -> list[str]:
    for attr in ("sources", "retrieval_sources", "citations"):
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
        retrieval_sources = _safe_list(ctx.get("pattern_sources"))
    if not retrieval_sources:
        scan_result = ctx.get("scan_result")
        if scan_result is not None:
            retrieval_sources = _extract_result_sources(scan_result)

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
