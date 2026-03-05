"""C0 / RAG — top-k retrieval memoisation cache seam.

Provides ``RagRetrievalCache`` which stores memoised top-k retrieval result
sets keyed by ``(u0_hash, embedder_version, seed_pack_manifest_hash, k,
cutoff)``.

Sovereignty contract
--------------------
* This cache is **strictly informational** — it caches retrieval results for
  identical query/corpus inputs only.  It MUST NOT influence routing,
  safety, or tier decisions.
* L4 remains the sole data authority.  This cache stores memoised derivatives
  only; a cache miss falls through to the live retrieval pipeline.
* ``replay_mode=True`` bypasses every read so replay reconstruction
  re-runs the full retrieval and records results in the transcript.
* Writing to this cache does NOT modify any L4 state.

Key schema::

    rag_topk:{u0_hash}:{embedder_version}:{seed_pack_manifest_hash}:{k}:{cutoff_r6}

``cutoff`` is rounded to 6 decimal places so semantically identical cutoffs
produce the same key regardless of floating-point representation noise.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_rag_topk_key
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)

logger = logging.getLogger(__name__)

_DEFAULT_RAG_TOPK_TTL: int = 600  # 10 minutes — retrieval results are short-lived


class RagRetrievalCache:
    """Memoises top-k retrieval result sets for identical C0 inputs.

    The cached value is a list of result dicts, e.g.::

        [
            {
                "chunk_id":   "<stable-id>",
                "score":      0.923,
                "text":       "...",
                "source":     "seed-pack/...",
            },
            ...
        ]

    **Informational only** — callers must NOT use cached retrieval results
    to gate routing or safety decisions.  Use only to avoid redundant
    embedding/retrieval I/O for identical query inputs.

    Input segments:

    +---------------------------+----------------------------------------------+
    | ``u0_hash``               | SHA-256 of the canonical query / u0 context  |
    | ``embedder_version``      | stable embedder model version slug           |
    | ``seed_pack_manifest_hash`` | hash of the active seed-pack manifest      |
    | ``k``                     | number of results requested                  |
    | ``cutoff``                | minimum similarity score threshold           |
    +---------------------------+----------------------------------------------+

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.  Default 10 minutes; keep
        short because corpus updates invalidate results via manifest-hash
        rotation rather than by TTL.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_RAG_TOPK_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        u0_hash: str,
        embedder_version: str,
        seed_pack_manifest_hash: str,
        k: int,
        cutoff: float,
        *,
        replay_mode: bool = False,
    ) -> list[dict[str, Any]] | None:
        """Return the cached top-k result list or ``None`` on miss/bypass.

        Returns ``None`` (forcing a live retrieval) when:
        - The key is not present in Redis or the fallback store.
        - Redis is unreachable and the fallback store has no entry.
        - ``replay_mode=True``.
        """
        key = build_rag_topk_key(u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff)
        result = self._cache.get_json(key, replay_mode=replay_mode)
        if result is None:
            return None
        if not isinstance(result, list):
            return None
        return result

    def set(
        self,
        u0_hash: str,
        embedder_version: str,
        seed_pack_manifest_hash: str,
        k: int,
        cutoff: float,
        results: list[dict[str, Any]],
    ) -> None:
        """Store *results* under the deterministic key.

        *results* must be a list of chunk dicts produced by the retrieval
        pipeline.  Each dict must be JSON-serialisable (no numpy arrays,
        no datetime objects).
        """
        key = build_rag_topk_key(u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff)
        self._cache.set_json(key, results, ttl_seconds=self._ttl)

    def invalidate(
        self,
        u0_hash: str,
        embedder_version: str,
        seed_pack_manifest_hash: str,
        k: int,
        cutoff: float,
    ) -> None:
        """Explicitly evict a cached retrieval result set."""
        key = build_rag_topk_key(u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singleton
# ---------------------------------------------------------------------------

_rag_retrieval_cache: RagRetrievalCache | None = None


def get_rag_retrieval_cache() -> RagRetrievalCache:
    """Return the process-global ``RagRetrievalCache`` instance."""
    global _rag_retrieval_cache
    if _rag_retrieval_cache is None:
        _rag_retrieval_cache = RagRetrievalCache()
    return _rag_retrieval_cache


__all__ = ["RagRetrievalCache", "get_rag_retrieval_cache"]
