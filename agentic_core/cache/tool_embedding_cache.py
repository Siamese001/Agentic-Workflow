"""Tool Embedding Cache — Redis-backed cache for tool registry embedding matrices.

Caches expensive numpy embedding computations for tool discovery.
Keyed by tool set fingerprint (hash of tool names + descriptions).
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from agentic_core.cache.cache_key_builders import _require_hash_segment
from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)
_DEFAULT_EMBEDDING_TTL = 3600 * 24 * 7


class ToolEmbeddingCache:
    """Cache for tool registry embedding matrices.

    Eliminates repeated expensive embedding computations for the same tool set.
    Automatically invalidates when tool set changes via fingerprint keying.
    """

    def __init__(
        self, cache: DeterministicRedisCache | None = None, ttl_seconds: int = _DEFAULT_EMBEDDING_TTL
    ):
        self._cache = cache or get_hot_cache()
        self._ttl = ttl_seconds

    def get_or_fetch(
        self, tool_definitions: list[dict[str, Any]], fetch_embeddings: Any, *, replay_mode: bool = False
    ) -> tuple[list[list[float]], list[str]]:
        """Read-through helper: return cached embeddings or call *fetch_embeddings*.

        *fetch_embeddings* is a zero-argument callable that computes and returns
        (embedding_matrix, tool_names) tuple.  Called only on cache miss.

        Args:
            tool_definitions: List of tool definition dicts (name, description, tags)
            fetch_embeddings: Callable that returns (embeddings, tool_names) tuple
            replay_mode: If True, bypass cache entirely

        Returns:
            Tuple of (embedding_matrix, tool_names)

        Raises:
            ValueError: If tool_definitions is empty
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ToolEmbeddingCache.get_or_fetch")

        if not tool_definitions:
            raise ValueError("Tool definitions list must not be empty")
        if not replay_mode:
            try:
                fingerprint = self._compute_tool_fingerprint(tool_definitions)
                cache_key = f"tool_embeddings:{fingerprint}"
                cached = self._cache.get_json(cache_key)
                if cached is not None:
                    logger.debug("[Tool embedding cache] HIT")
                    return (cached["embeddings"], cached["tool_names"])
            except ValueError:
                raise
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Tool embedding cache] Cache read failed: {e}")
        logger.debug("[Tool embedding cache] MISS — computing embeddings")
        embeddings, tool_names = fetch_embeddings()
        if not replay_mode:
            try:
                fingerprint = self._compute_tool_fingerprint(tool_definitions)
                cache_key = f"tool_embeddings:{fingerprint}"
                self._cache.set_json(
                    cache_key, {"embeddings": embeddings, "tool_names": tool_names}, ttl_seconds=self._ttl
                )
            except ValueError:
                pass
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[Tool embedding cache] Cache write failed: {e}")
        return (embeddings, tool_names)

    def _compute_tool_fingerprint(self, tool_definitions: list[dict[str, Any]]) -> str:
        """Compute deterministic fingerprint of tool set for cache key."""
        sorted_tools = sorted(tool_definitions, key=lambda t: t.get("name", ""))
        fingerprint_data = json.dumps(
            [
                {
                    "name": t.get("name", ""),
                    "description": t.get("description", ""),
                    "tags": sorted(t.get("tags", [])),
                }
                for t in sorted_tools
            ],
            sort_keys=True,
        )
        tool_hash = hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()
        _require_hash_segment("tool_fingerprint", tool_hash)
        return tool_hash

    def invalidate_all(self) -> None:
        """Invalidate all cached embeddings.

        Note: This is a no-op since cache keys are fingerprint-addressed.
        Tool set changes automatically invalidate via different fingerprint.
        """
        logger.debug("[Tool embedding cache] invalidate_all called (no-op for fingerprint-addressed cache)")


def get_tool_embedding_cache() -> ToolEmbeddingCache:
    """Get the singleton tool embedding cache instance."""
    return ToolEmbeddingCache()
