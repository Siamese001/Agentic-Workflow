"""Version-Aware Cache.

Multi-factor cache with semantic lookup, freshness management, and ACL integration.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.knowledge.cache.catalog_keymaker import CatalogKeymaker
from agentic_core.knowledge.cache.fast_terminal import FastTerminal
from agentic_core.knowledge.cache.policy_evaluator import PolicyEvaluator
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    data: dict[str, Any]
    query_vector: list[float] | None = None
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheLookupResult:
    """Result of cache lookup."""
    found: bool
    entry: CacheEntry | None = None
    match_type: str = "none"  # exact, semantic, none
    score: float = 0.0
    freshness_ok: bool = True
    acl_ok: bool = True


class VersionAwareCache:
    """Version-aware cache with multi-factor keys.

    The VersionAwareCache provides exact and semantic matching with
    freshness verification and ACL integration.
    """

    def __init__(
        self,
        keymaker: CatalogKeymaker | None = None,
        evaluator: PolicyEvaluator | None = None,
        terminal: FastTerminal | None = None,
        semantic_threshold: float = 0.95,
    ):
        """Initialize the version-aware cache.

        Args:
            keymaker: Key generator
            evaluator: Policy evaluator
            terminal: Storage backend
            semantic_threshold: Similarity threshold for semantic match
        """
        self.keymaker = keymaker or CatalogKeymaker()
        self.evaluator = evaluator or PolicyEvaluator()
        self.terminal = terminal or FastTerminal()
        self.semantic_threshold = semantic_threshold

        # Semantic index (query_vector -> key mapping)
        self._semantic_index: dict[str, list[float]] = {}

        log.info("VersionAwareCache initialized")

    def lookup(
        self,
        query: str,
        query_context: dict[str, Any],
        scope_metadata: dict[str, Any],
        check_semantic: bool = True,
    ) -> CacheLookupResult:
        """Lookup cache with exact and semantic matching.

        Args:
            query: Query string
            query_context: Query context
            scope_metadata: Scope metadata
            check_semantic: Whether to check semantic matches

        Returns:
            CacheLookupResult with entry if found
        """
        trace_id = f"cache_lookup_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "VersionAwareCache.lookup",
        )

        # Generate cache key
        cache_key = self.keymaker.make_key(
            query,
            query_context.get("routing_signal"),
            scope_metadata,
            query_context.get("freshness_band", "daily"),
        )

        # Try exact lookup
        stored = self.terminal.lookup(cache_key.key_hash)
        if stored:
            entry = CacheEntry(
                key=cache_key.key_hash,
                data=stored.get("data", {}),
                timestamp=stored.get("timestamp", 0),
                metadata=stored.get("metadata", {}),
            )

            # Evaluate policy
            policy_result = self.evaluator.evaluate(
                {"timestamp": entry.timestamp, **entry.metadata},
                query_context,
                scope_metadata,
            )

            if policy_result.can_use_cache:
                _emit_records_telemetry_event(
                    trace_id,
                    "VersionAwareCache",
                    "cache_hit_exact",
                )
                entry.access_count += 1
                return CacheLookupResult(
                    found=True,
                    entry=entry,
                    match_type="exact",
                    score=1.0,
                )

        # Try semantic lookup if enabled
        if check_semantic and query_context.get("query_vector"):
            semantic_result = self._semantic_lookup(
                query_context["query_vector"],
                query_context,
                scope_metadata,
            )
            if semantic_result.found:
                _emit_records_telemetry_event(
                    trace_id,
                    "VersionAwareCache",
                    "cache_hit_semantic",
                )
                return semantic_result

        _emit_records_telemetry_event(
            trace_id,
            "VersionAwareCache",
            "cache_miss",
        )
        return CacheLookupResult(found=False)

    def store(
        self,
        query: str,
        data: dict[str, Any],
        query_context: dict[str, Any],
        scope_metadata: dict[str, Any],
        query_vector: list[float] | None = None,
    ) -> bool:
        """Store data in cache.

        Args:
            query: Query string
            data: Data to cache
            query_context: Query context
            scope_metadata: Scope metadata
            query_vector: Optional vector for semantic indexing

        Returns:
            True if stored successfully
        """
        # Generate cache key
        cache_key = self.keymaker.make_key(
            query,
            query_context.get("routing_signal"),
            scope_metadata,
            query_context.get("freshness_band", "daily"),
        )

        # Store in terminal
        entry_data = {
            "data": data,
            "query": query,
            "routing_signal": query_context.get("routing_signal"),
            "required_permissions": scope_metadata.get("required_permissions", []),
        }

        success = self.terminal.store(cache_key.key_hash, entry_data)

        # Index for semantic lookup
        if success and query_vector:
            self._semantic_index[cache_key.key_hash] = query_vector

        log.debug(f"Stored cache entry: {cache_key.key_hash[:16]}...")
        return success

    def invalidate_query(
        self,
        query: str,
        query_context: dict[str, Any],
        scope_metadata: dict[str, Any],
    ) -> bool:
        """Invalidate cache for a query.

        Args:
            query: Query string
            query_context: Query context
            scope_metadata: Scope metadata

        Returns:
            True if invalidated
        """
        cache_key = self.keymaker.make_key(
            query,
            query_context.get("routing_signal"),
            scope_metadata,
            query_context.get("freshness_band", "daily"),
        )

        # Remove from semantic index
        if cache_key.key_hash in self._semantic_index:
            del self._semantic_index[cache_key.key_hash]

        return self.terminal.invalidate(cache_key.key_hash)

    def invalidate_scope(self, scope_pattern: str) -> int:
        """Invalidate cache entries matching scope pattern.

        Args:
            scope_pattern: Pattern to match in keys

        Returns:
            Number of entries invalidated
        """
        return self.terminal.invalidate_pattern(scope_pattern)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        terminal_stats = self.terminal.get_stats()

        return {
            **terminal_stats,
            "semantic_index_size": len(self._semantic_index),
        }

    def _semantic_lookup(
        self,
        query_vector: list[float],
        query_context: dict[str, Any],
        scope_metadata: dict[str, Any],
    ) -> CacheLookupResult:
        """Perform semantic similarity lookup."""
        best_match = None
        best_score = 0.0

        for key, cached_vector in self._semantic_index.items():
            # Cosine similarity
            score = self._cosine_similarity(query_vector, cached_vector)

            if score > best_score and score >= self.semantic_threshold:
                best_score = score
                best_match = key

        if best_match:
            stored = self.terminal.lookup(best_match)
            if stored:
                entry = CacheEntry(
                    key=best_match,
                    data=stored.get("data", {}),
                    timestamp=stored.get("timestamp", 0),
                    metadata=stored.get("metadata", {}),
                )

                # Verify policy
                policy_result = self.evaluator.evaluate(
                    {"timestamp": entry.timestamp, **entry.metadata},
                    query_context,
                    scope_metadata,
                )

                if policy_result.can_use_cache:
                    entry.access_count += 1
                    return CacheLookupResult(
                        found=True,
                        entry=entry,
                        match_type="semantic",
                        score=best_score,
                    )

        return CacheLookupResult(found=False)

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)


# Global instance
_global_cache: VersionAwareCache | None = None


def get_version_aware_cache() -> VersionAwareCache:
    """Get or create the global version-aware cache."""
    global _global_cache
    if _global_cache is None:
        _global_cache = VersionAwareCache()
    return _global_cache
