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
    from agentic_core.interfaces.embeddings import (
        SimilarityResult,
        query_similarity,
    )
"""

from __future__ import annotations

from dataclasses import dataclass


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True)
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


def query_similarity(
    query: str,
    top_k: int = 20,
    namespace: str = "",
) -> list[SimilarityResult]:
    """
    Query existing embeddings — informational only, C0 context.

    Args:
        query: The query text
        top_k: Maximum results (capped at 20 per C0 spec)
        namespace: Optional namespace for seed pack lookup

    Returns:
        List of SimilarityResult — score + hash + preview only
    """
    if top_k > 20:
        top_k = 20
    try:
        from agentic_core.L4_state.memory.sovereign_semantic_cache import (
            SovereignSemanticCache,
        )

        cache = SovereignSemanticCache()
        raw = cache.query(query, top_k=top_k, namespace=namespace)
        return [
            SimilarityResult(
                content_hash=r.get("content_hash", ""),
                similarity_score=float(r.get("score", 0.0)),
                content_preview=r.get("content", "")[:200],
            )
            for r in raw
        ]
    except Exception:
        return []


__all__ = [
    "SimilarityResult",
    "query_similarity",
]
