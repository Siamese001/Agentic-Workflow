"""Query Cache - Performance optimization for agent GraphDB queries.

This module provides intelligent caching for frequently used GraphDB queries
to improve real-time agent responsiveness.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from threading import RLock

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL and metadata."""

    value: Any
    timestamp: float
    ttl: float
    hit_count: int = 0
    access_frequency: float = 0.0

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > (self.timestamp + self.ttl)

    def record_hit(self) -> None:
        """Record a cache hit for analytics."""
        self.hit_count += 1
        age = time.time() - self.timestamp
        if age > 0:
            self.access_frequency = self.hit_count / age


class QueryCache:
    """Intelligent cache for GraphDB queries with TTL and analytics."""

    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """Initialize query cache.

        Args:
            max_size: Maximum number of cached entries
            default_ttl: Default TTL in seconds (5 minutes)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = RLock()

        # Analytics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

        logger.info(f"QueryCache initialized: max_size={max_size}, default_ttl={default_ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None

            entry.record_hit()
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            # Evict if necessary
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()

            entry = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

            self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
        logger.info("QueryCache cleared")

    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.

        Returns:
            Number of expired entries removed
        """
        with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find entry with lowest access frequency
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_frequency)

        del self._cache[lru_key]
        self._evictions += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            # Calculate average TTL and age
            current_time = time.time()
            total_age = sum(current_time - entry.timestamp for entry in self._cache.values())
            avg_age = total_age / len(self._cache) if self._cache else 0.0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "average_age_seconds": avg_age,
                "memory_estimate_bytes": self._estimate_memory_usage(),
            }

    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes (rough approximation).

        Returns:
            Estimated memory usage in bytes
        """
        import sys

        total_size = 0
        for key, entry in self._cache.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(entry.value)
            total_size += 200  # Overhead for CacheEntry object

        return total_size

    def get_hot_keys(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently accessed cache keys.

        Args:
            top_n: Number of top keys to return

        Returns:
            List of hot key information
        """
        with self._lock:
            sorted_entries = sorted(self._cache.items(), key=lambda item: item[1].hit_count, reverse=True)

            return [
                {
                    "key": key,
                    "hit_count": entry.hit_count,
                    "access_frequency": entry.access_frequency,
                    "age_seconds": time.time() - entry.timestamp,
                }
                for key, entry in sorted_entries[:top_n]
            ]


class SmartQueryCache(QueryCache):
    """Smart cache that adapts TTL based on query patterns."""

    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """Initialize smart query cache.

        Args:
            max_size: Maximum number of cached entries
            default_ttl: Default TTL in seconds
        """
        super().__init__(max_size, default_ttl)

        # Query pattern learning
        self._query_patterns: Dict[str, Dict[str, float]] = {}

        # TTL multipliers based on query type
        self._ttl_multipliers = {
            "illegal_paths": 0.5,  # Changes frequently
            "blast_radius": 0.8,  # Moderately stable
            "spine_completeness": 2.0,  # Very stable
            "structural": 1.5,  # Fairly stable
            "historical": 5.0,  # Very stable
        }

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value with adaptive TTL."""
        if ttl is None:
            ttl = self._calculate_adaptive_ttl(key)

        super().set(key, value, ttl)

        # Update query patterns
        self._update_query_pattern(key)

    def _calculate_adaptive_ttl(self, key: str) -> float:
        """Calculate adaptive TTL based on query type and patterns."""
        # Base TTL on query type
        query_type = self._extract_query_type(key)
        multiplier = self._ttl_multipliers.get(query_type, 1.0)

        # Adjust based on historical patterns
        pattern = self._query_patterns.get(key, {})
        avg_access_interval = pattern.get("avg_interval", self.default_ttl)

        # Use shorter TTL for frequently changing queries
        if avg_access_interval < 60:  # Very frequent access
            multiplier *= 0.5
        elif avg_access_interval > 3600:  # Infrequent access
            multiplier *= 2.0

        return self.default_ttl * multiplier

    def _extract_query_type(self, key: str) -> str:
        """Extract query type from cache key."""
        key_lower = key.lower()

        if "illegal_paths" in key_lower:
            return "illegal_paths"
        elif "blast_radius" in key_lower:
            return "blast_radius"
        elif "spine_completeness" in key_lower:
            return "spine_completeness"
        elif "historical" in key_lower:
            return "historical"
        elif "structural" in key_lower:
            return "structural"
        else:
            return "general"

    def _update_query_pattern(self, key: str) -> None:
        """Update query pattern statistics."""
        current_time = time.time()

        if key not in self._query_patterns:
            self._query_patterns[key] = {
                "first_access": current_time,
                "last_access": current_time,
                "access_count": 0,
                "avg_interval": self.default_ttl,
            }

        pattern = self._query_patterns[key]
        pattern["access_count"] += 1

        # Update average access interval
        if pattern["access_count"] > 1:
            interval = current_time - pattern["last_access"]
            pattern["avg_interval"] = (
                pattern["avg_interval"] * (pattern["access_count"] - 1) + interval
            ) / pattern["access_count"]

        pattern["last_access"] = current_time
