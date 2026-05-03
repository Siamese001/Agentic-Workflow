"""apps_underwriting_ai FEC producer — builds FinalEvidenceContract dict.

Plan: ``.windsurf/plans/apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9.md`` W1.P1.

Pattern source: ``apps_qna/cert/fec_producer.py`` (completed via
``apps-qna-c0-fec-producer-wiring-d4f1e8``).

Shape
-----
Returned dict follows ``ExitReviewPacket.final_evidence_contract``:

    {
        "schema_version": "1.0",
        "producer": "apps_underwriting_ai.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<document_id | section_anchor>, ...],
        "template_ids": ["decision_packet_v1"],
        "route_id": "apps_underwriting_ai.decision_packet_v1",
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
    }

Source extraction — in priority order:

1. Explicit ``run_context["c0_retrieval_sources"]`` (forward-compat override).
2. ``run_context["uw_result"].register`` — EvidenceRegister rows expose
   ``source_doc`` / ``source_id`` attributes per parser convention.
3. ``run_context["uw_result"].request.statements`` — parsed document
   ids carried on the request envelope.

When none yields sources, returns ``grounded=False``,
``evidence_sufficiency="template_only"``. Empty/malformed context never
raises — producer is READ-ONLY and degrades to an ``empty`` packet.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_underwriting_ai.cert.fec_producer"
_DEFAULT_ROUTE = "apps_underwriting_ai.decision_packet_v1"
_DEFAULT_TEMPLATE_IDS = ("decision_packet_v1",)


def _safe_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float)) and str(item)]


def _safe_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _extract_register_sources(uw_result: Any) -> list[str]:
    register = getattr(uw_result, "register", None)
    rows = getattr(register, "rows", None) if register is not None else None
    if not isinstance(rows, (list, tuple)):
        return []
    ids: list[str] = []
    for row in rows:
        for attr in ("source_doc", "source_id", "doc_id", "anchor"):
            value = getattr(row, attr, None)
            if isinstance(value, str) and value:
                ids.append(value)
                break
    return ids


def _extract_statement_ids(uw_result: Any) -> list[str]:
    request = getattr(uw_result, "request", None)
    statements = getattr(request, "statements", None) if request is not None else None
    if not isinstance(statements, (list, tuple)):
        return []
    ids: list[str] = []
    for stmt in statements:
        for attr in ("document_id", "id", "path"):
            value = getattr(stmt, attr, None)
            if isinstance(value, str) and value:
                ids.append(value)
                break
    return ids


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    """Produce FEC dict from apps_underwriting_ai run_context. Never raises."""
    ctx = run_context if isinstance(run_context, Mapping) else {}

    route_id = _safe_str(ctx.get("route_id")) or _DEFAULT_ROUTE
    rc = ctx.get("route_contract")
    if isinstance(rc, Mapping):
        route_id = _safe_str(rc.get("route_id"), route_id) or route_id

    template_ids = _safe_list(ctx.get("template_ids")) or list(_DEFAULT_TEMPLATE_IDS)

    # Source extraction ladder.
    retrieval_sources = _safe_list(ctx.get("c0_retrieval_sources"))
    if not retrieval_sources:
        uw_result = ctx.get("uw_result")
        if uw_result is not None:
            retrieval_sources = _extract_register_sources(uw_result)
            if not retrieval_sources:
                retrieval_sources = _extract_statement_ids(uw_result)

    # De-duplicate preserving order.
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
