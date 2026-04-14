"""
agentic_core/interfaces/embeddings_shim.py

C0-informational-only embedding interface for apps_* consumption.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)

_MAX_TOP_K = 20
_PREVIEW_CHARS = 200


@dataclass(frozen=True, slots=True)
class SimilarityResult:
    """Informational-only embedding result."""

    content_hash: str
    similarity_score: float
    content_preview: str


def _normalize_top_k(top_k: int) -> int:
    if top_k < 1:
        return 1
    return min(top_k, _MAX_TOP_K)


def query_similarity(query: str, top_k: int = _MAX_TOP_K, namespace: str = "") -> list[SimilarityResult]:
    """Query existing embeddings in a bounded, informational-only way."""
    normalized_query = query.strip()
    if not normalized_query:
        return []

    try:
        from agentic_core.L4_state.utils.memory.sovereign_semantic_cache import SovereignSemanticCache
    except ImportError as exc:
        LOGGER.warning("Embedding cache unavailable: %s", exc)
        return []

    cache = SovereignSemanticCache()
    try:
        raw_results = cache.query(normalized_query, top_k=_normalize_top_k(top_k), namespace=namespace)
    except (RuntimeError, ValueError, TypeError) as exc:
        LOGGER.warning("Embedding query failed: %s", exc)
        return []

    results: list[SimilarityResult] = []
    for row in raw_results:  # progress_bar: bounded at _MAX_TOP_K rows
        if not isinstance(row, dict):
            LOGGER.debug("Skipping malformed embedding row: %r", row)
            continue
        results.append(
            SimilarityResult(
                content_hash=str(row.get("content_hash", "")),
                similarity_score=float(row.get("score", 0.0)),
                content_preview=str(row.get("content", ""))[:_PREVIEW_CHARS],
            )
        )
    return results


__all__ = ["SimilarityResult", "query_similarity"]
