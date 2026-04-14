"""
agentic_core/interfaces/embeddings.py

C0-informational-only embedding interface for apps_* consumption.

AUTHORITY CONSTRAINTS:
- Embedding results are score + content_hash + preview ONLY
- No raw vectors exposed
- No FAISS index handles
- No routing metadata that could influence tier selection
- No instantiation authority — embeddings created only via EmbeddingServiceFactory
- query_similarity is read-only with bounded top_k

USAGE (apps_*):
    from agentic_core.interfaces.embeddings_shim import (
        SimilarityResult,
        query_similarity,
    )
"""

from __future__ import annotations

from dataclasses import dataclass
import logging

Logger = logging.getLogger(__name__)

_MAX_TOP_K = 20
_PREVIEW_CHARS = 200


@dataclass(frozen=True, slots=True)
class SimilarityResult:
    """
    Informational-only embedding result.

    DELIBERATELY EXCLUDES:
    - Raw embedding vectors (no routing influence)
    - FAISS index handles
    - Routing metadata
    - Tier selection data
    - Any mutable state

    Contains only: content_hash, similarity_score, content_preview.
    """

    content_hash: str
    similarity_score: float
    content_preview: str


def query_similarity(query: str, top_k: int = _MAX_TOP_K, namespace: str = "") -> list[SimilarityResult]:
    """
    Query existing embeddings — informational only, C0 context.

    Args:
        query: The query text
        top_k: Maximum results (capped at _MAX_TOP_K per C0 spec)
        namespace: Optional namespace for seed pack lookup

    Returns:
        List of SimilarityResult — score + hash + preview only
    """
    query = query.strip()
    if not query:
        Logger.warning("[query_similarity] Empty query received; returning no results.")
        return []
    top_k = min(max(top_k, 1), _MAX_TOP_K)
    try:
        from agentic_core.L4_state.utils.memory.sovereign_semantic_cache import SovereignSemanticCache
    except ImportError as exc:
        Logger.warning("[query_similarity] SovereignSemanticCache unavailable: %s", exc)
        return []
    try:
        cache = SovereignSemanticCache()
        raw = cache.query(query, top_k=top_k, namespace=namespace)
        results: list[SimilarityResult] = []
        for r in raw:  # progress_bar: assemble similarity results
            if not isinstance(r, dict):
                Logger.warning("[query_similarity] Malformed embedding row (not a dict): %r", r)
                continue
            results.append(
                SimilarityResult(
                    content_hash=r.get("content_hash", ""),
                    similarity_score=float(r.get("score", 0.0)),
                    content_preview=r.get("content", "")[:_PREVIEW_CHARS],
                )
            )
        return results
    except (RuntimeError, ValueError, TypeError) as exc:
        Logger.warning("[query_similarity] Cache query failed: %s", exc)
        return []


__all__ = ["SimilarityResult", "query_similarity"]
