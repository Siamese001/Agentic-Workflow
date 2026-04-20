"""L1 Exact Cache - Redis-based Exact Match Cache

Implements spec-compliant L1 Exact Cache from Agentic Retrieval Models v9:
- Matching Logic: Exact Match / O(1) Hash
- Data Payload: Strings, hashes, JSON
- Latency: Ultra-Low / Zero Cost
- Primary Failure Mode: Cache Misses & Stale Data
- Data Contract: [1] CacheHit

Provides O(1) hash-based exact matching for queries and responses.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class CacheHit:
    """L1 Cache hit data contract [1]."""

    cache_key: str
    query_hash: str
    response: str
    hit_timestamp: str
    ttl_seconds: int = 3600
    metadata: dict[str, Any] = field(default_factory=dict)


class L1ExactCache:
    """L1 Exact Cache - Ultra-low latency exact match cache.

    Features:
    - O(1) hash-based lookups
    - Redis backend
    - TTL-based expiration
    - Cache hit/miss tracking
    - Deterministic key generation
    """

    def __init__(
        self,
        redis_client: Any | None = None,
        default_ttl: int = 3600,
        key_prefix: str = "l1_exact:",
    ):
        """Initialize L1 Exact Cache.

        Args:
            redis_client: Redis client instance
            default_ttl: Default TTL in seconds
            key_prefix: Key prefix for Redis
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix

        self._hit_count = 0
        self._miss_count = 0
        self._local_cache: dict[str, Any] = {}  # Fallback local cache
        self._use_local = redis_client is None

    @staticmethod
    def _deserialize_entry(raw: bytes | str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(raw, dict):
            entry = raw
        else:
            text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
            entry = json.loads(text)
        if not isinstance(entry, dict):
            raise ValueError("Cache entry must decode to a dict")
        for required in ("response", "timestamp", "ttl"):
            if required not in entry:
                raise ValueError(f"Cache entry missing required field: {required}")
        return entry

    @staticmethod
    def _serialize_entry(entry: dict[str, Any]) -> str:
        return json.dumps(entry, separators=(",", ":"))

    def _generate_key(self, query: str) -> str:
        """Generate deterministic cache key from query.

        Args:
            query: Query string

        Returns:
            Cache key (SHA-256 hash)
        """
        # Normalize query for consistent hashing
        normalized = query.strip().lower()
        query_hash = hashlib.sha256(normalized.encode()).hexdigest()
        return f"{self.key_prefix}{query_hash}"

    def get(self, query: str) -> CacheHit | None:
        """Get cached response for query.

        Args:
            query: Query string

        Returns:
            CacheHit if cache hit, None if miss
        """
        _trace_id = f"l1_get_{hashlib.sha256(query.encode()).hexdigest()[:16]}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "L1ExactCache.get")

        cache_key = self._generate_key(query)
        query_hash = cache_key[len(self.key_prefix) :]

        try:
            if self._use_local:
                # Use local cache
                if cache_key in self._local_cache:
                    entry = self._deserialize_entry(self._local_cache[cache_key])
                    self._hit_count += 1
                    return CacheHit(
                        cache_key=cache_key,
                        query_hash=query_hash,
                        response=entry["response"],
                        hit_timestamp=entry["timestamp"],
                        ttl_seconds=entry["ttl"],
                        metadata=entry.get("metadata", {}),
                    )
            else:
                # Use Redis
                data = self.redis.get(cache_key)
                if data:
                    entry = self._deserialize_entry(data)
                    self._hit_count += 1
                    # _emit_records_cache_hit(_trace_id, cache_key, "l1_exact")
                    return CacheHit(
                        cache_key=cache_key,
                        query_hash=query_hash,
                        response=entry["response"],
                        hit_timestamp=entry["timestamp"],
                        ttl_seconds=entry["ttl"],
                        metadata=entry.get("metadata", {}),
                    )

            # Cache miss
            self._miss_count += 1
            # _emit_records_cache_miss(_trace_id, cache_key, "l1_exact")
            return None

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            Logger.warning(f"L1 cache get failed: {e}")
            return None

    def set(
        self,
        query: str,
        response: str,
        ttl: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Cache response for query.

        Args:
            query: Query string
            response: Response to cache
            ttl: TTL in seconds (defaults to default_ttl)
            metadata: Optional metadata

        Returns:
            True if cached successfully
        """
        _trace_id = f"l1_set_{hashlib.sha256(query.encode()).hexdigest()[:16]}"

        cache_key = self._generate_key(query)
        ttl = ttl or self.default_ttl

        from datetime import datetime

        entry = {
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "ttl": ttl,
            "metadata": metadata or {},
        }

        try:
            if self._use_local:
                self._local_cache[cache_key] = entry
            else:
                self.redis.setex(cache_key, ttl, self._serialize_entry(entry))

            Logger.debug(f"Cached L1 entry: {cache_key[:32]}...")
            return True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.warning(f"L1 cache set failed: {e}")
            return False

    def delete(self, query: str) -> bool:
        """Delete cached entry for query.

        Args:
            query: Query string

        Returns:
            True if deleted
        """
        cache_key = self._generate_key(query)

        try:
            if self._use_local:
                if cache_key in self._local_cache:
                    del self._local_cache[cache_key]
                    return True
                return False
            else:
                return bool(self.redis.delete(cache_key))

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.warning(f"L1 cache delete failed: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cached entries.

        Returns:
            True if cleared
        """
        try:
            if self._use_local:
                self._local_cache.clear()
            else:
                # Find and delete all keys with prefix
                for key in self.redis.scan_iter(match=f"{self.key_prefix}*"):
                    self.redis.delete(key)

            Logger.info("Cleared L1 exact cache")
            return True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"L1 cache clear failed: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hit_count + self._miss_count
        hit_rate = self._hit_count / total_requests if total_requests > 0 else 0.0

        return {
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "key_count": len(self._local_cache) if self._use_local else None,
            "ttl_seconds": self.default_ttl,
            "cache_type": "local" if self._use_local else "redis",
        }

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: Pattern to match in query strings

        Returns:
            Number of entries invalidated
        """
        count = 0
        pattern_lower = pattern.lower()

        try:
            if self._use_local:
                # Scan local cache
                keys_to_delete = []
                for key, entry in self._local_cache.items():
                    response = entry.get("response", "")
                    if pattern_lower in response.lower():
                        keys_to_delete.append(key)

                for key in keys_to_delete:
                    del self._local_cache[key]
                    count += 1
            else:
                # Scan Redis (expensive, use sparingly)
                for key in self.redis.scan_iter(match=f"{self.key_prefix}*"):
                    data = self.redis.get(key)
                    if data:
                        entry = self._deserialize_entry(data)
                        if pattern_lower in entry.get("response", "").lower():
                            self.redis.delete(key)
                            count += 1

            Logger.info(f"Invalidated {count} L1 cache entries matching '{pattern}'")
            return count

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            Logger.error(f"L1 cache pattern invalidation failed: {e}")
            return 0


class L1CacheManager:
    """Manager for L1 Exact Cache with multiple cache zones.

    Provides separate caches for different data types:
    - queries: User query responses
    - embeddings: Embedding results
    - completions: LLM completions
    """

    def __init__(self, redis_client: Any | None = None):
        """Initialize L1 Cache Manager.

        Args:
            redis_client: Redis client instance
        """
        self.caches = {
            "queries": L1ExactCache(redis_client, key_prefix="l1:query:"),
            "embeddings": L1ExactCache(redis_client, key_prefix="l1:embed:"),
            "completions": L1ExactCache(redis_client, key_prefix="l1:complete:"),
        }

    def get_cache(self, zone: str) -> L1ExactCache:
        """Get cache for a specific zone.

        Args:
            zone: Cache zone (queries, embeddings, completions)

        Returns:
            L1ExactCache for the zone
        """
        return self.caches.get(zone, self.caches["queries"])

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get stats for all cache zones."""
        return {zone: cache.get_stats() for zone, cache in self.caches.items()}

    def clear_all(self) -> bool:
        """Clear all cache zones."""
        for cache in self.caches.values():
            cache.clear()
        return True


# Global instance
_global_l1_cache: L1ExactCache | None = None
_global_l1_manager: L1CacheManager | None = None


def get_global_l1_cache() -> L1ExactCache:
    """Get or create global L1 cache."""
    global _global_l1_cache
    if _global_l1_cache is None:
        _global_l1_cache = L1ExactCache()
    return _global_l1_cache


def get_global_l1_manager() -> L1CacheManager:
    """Get or create global L1 cache manager."""
    global _global_l1_manager
    if _global_l1_manager is None:
        _global_l1_manager = L1CacheManager()
    return _global_l1_manager


def l1_cache_get(query: str) -> str | None:
    """Convenience function for L1 cache get."""
    hit = get_global_l1_cache().get(query)
    return hit.response if hit else None


def l1_cache_set(query: str, response: str, ttl: int | None = None) -> bool:
    """Convenience function for L1 cache set."""
    return get_global_l1_cache().set(query, response, ttl)
