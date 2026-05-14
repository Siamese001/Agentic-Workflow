"""C0 binding — adapts AppIngressRunner route to apps_rfp C0 retrieval.

AppIngressRunner calls: fec = c0(route, validated)

Consumes: RouteContract (from rfp_l0) + ValidatedRequest (from rfp_u0)
Emits:    FinalEvidenceContract dict (compatible with apps_rfp PA assembly)

apps_rfp C0 retrieves from the 'rfp_docs' collection and shapes chunks into
a FinalEvidenceContract. Degrades gracefully when rfp_docs is absent (mirrors
GovernedRfpRun's existing behaviour).

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def rfp_c0(route: Any, validated: Any) -> dict[str, Any]:
    """C0 stage binding for apps_rfp.

    Retrieves grounding evidence from rfp_docs and returns a
    FinalEvidenceContract-shaped dict for the PA binding.
    Fail-soft on retrieval unavailability — returns empty grounding rather
    than raising, matching the GovernedRfpRun precedent.

    Args:
        route: RfpRouteContract from rfp_l0.
        validated: ValidatedRequest from rfp_u0.

    Returns:
        FinalEvidenceContract-shaped dict with chunks, collection, and metadata.
        AppIngressRunner passes this opaquely to the pa binding.
    """
    request_id: str = getattr(route, "request_id", "") or ""
    collection: str = getattr(route, "collection", "rfp_docs") or "rfp_docs"
    sub_queries: list = list(getattr(route, "sub_queries", []) or [])
    raw_payload: dict = getattr(validated, "raw_payload", {}) or {}

    query = sub_queries[0] if sub_queries else raw_payload.get("rfp_document_path", "") or ""

    _LOGGER.debug(
        "rfp_c0: request_id=%s collection=%s query=%s",
        request_id,
        collection,
        query[:80],
    )

    chunks: list[dict] = []
    raw_count: int = 0
    shaped_count: int = 0

    try:
        from agentic_core.C0_context.retrieval.hybrid_search import hybrid_search  # type: ignore[import]

        results = hybrid_search(
            query=query,
            collection=collection,
            top_k=8,
        )
        raw_count = len(results)
        chunks = [
            {
                "text": r.get("text", ""),
                "score": r.get("score", 0.0),
                "source": r.get("source", "rfp_docs"),
            }
            for r in results
            if r.get("text")
        ]
        shaped_count = len(chunks)
    except (ImportError, OSError, ValueError, RuntimeError, KeyError) as exc:
        _LOGGER.warning(
            "rfp_c0: retrieval unavailable (collection=%s): %s — proceeding with empty grounding",
            collection,
            exc,
        )

    return {
        "request_id": request_id,
        "app_id": "apps_rfp",
        "collection": collection,
        "chunks": chunks,
        "raw_count": raw_count,
        "shaped_count": shaped_count,
        "grounded": shaped_count > 0,
        "metadata": {
            "query": query,
            "rfp_document_path": raw_payload.get("rfp_document_path", ""),
            "target_company": raw_payload.get("target_company", ""),
        },
    }


__all__ = ["rfp_c0"]
