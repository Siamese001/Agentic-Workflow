"""Fast Terminal.

Stale item eviction, access log updates, and zero generation cost for cache hits.
"""

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

log = logging.getLogger(__name__)


@dataclass
class AccessLogEntry:
    """Cache access log entry."""
    key: str
    timestamp: float
    hit: bool
    latency_ms: float


class FastTerminal:
    """Fast cache terminal for lookups and eviction.

    The FastTerminal provides O(1) cache lookups with LRU eviction,
    access logging, and stale item detection.
    """

    def __init__(
        self,
        max_size: int = 10000,
        default_ttl: float = 86400,  # 24 hours
    ):
        """Initialize the fast terminal.

        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl

        # LRU cache using OrderedDict
        self._cache: OrderedDict[str, dict[str, Any]] = OrderedDict()

        # Access log (circular buffer)
        self._access_log: list[AccessLogEntry] = []
        self._max_log_size = 1000

        # Statistics
        self._hits = 0
        self._misses = 0

        log.info(f"FastTerminal initialized (max_size={max_size})")

    def lookup(self, key: str) -> dict[str, Any] | None:
        """Lookup cache entry by key.

        Args:
            key: Cache key

        Returns:
            Cache entry if found and fresh, None otherwise
        """
        trace_id = f"lookup_{key[:16]}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "FastTerminal.lookup"
        )

        start_time = time.time()

        if key not in self._cache:
            self._misses += 1
            self._log_access(key, False, (time.time() - start_time) * 1000)
            return None

        entry = self._cache[key]

        # Check TTL
        if self._is_expired(entry):
            # Evict expired entry
            del self._cache[key]
            self._misses += 1
            self._log_access(key, False, (time.time() - start_time) * 1000)
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)

        self._hits += 1
        self._log_access(key, True, (time.time() - start_time) * 1000)

        log.debug(f"Cache hit for key: {key[:16]}...")
        return entry

    def store(
        self,
        key: str,
        data: dict[str, Any],
        ttl: float | None = None,
    ) -> bool:
        """Store data in cache.

        Args:
            key: Cache key
            data: Data to cache
            ttl: Optional TTL override

        Returns:
            True if stored successfully
        """
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict_oldest(1)

        # Add timestamp and TTL
        entry = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl or self.default_ttl,
        }

        self._cache[key] = entry
        self._cache.move_to_end(key)

        log.debug(f"Stored cache entry: {key[:16]}...")
        return True

    def invalidate(self, key: str) -> bool:
        """Invalidate a cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was removed, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            log.debug(f"Invalidated cache entry: {key[:16]}...")
            return True
        return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern.

        Args:
            pattern: Substring to match in keys

        Returns:
            Number of entries invalidated
        """
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]

        log.info(f"Invalidated {len(keys_to_remove)} entries matching '{pattern}'")
        return len(keys_to_remove)

    def evict_stale(self) -> int:
        """Evict all stale entries.

        Returns:
            Number of entries evicted
        """
        stale_keys = [
            k for k, v in self._cache.items()
            if self._is_expired(v)
        ]

        for key in stale_keys:
            del self._cache[key]

        log.info(f"Evicted {len(stale_keys)} stale entries")
        return len(stale_keys)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "access_log_size": len(self._access_log),
        }

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        log.info(f"Cleared {count} cache entries")
        return count

    def _is_expired(self, entry: dict[str, Any]) -> bool:
        """Check if entry is expired."""
        age = time.time() - entry.get("timestamp", 0)
        return age > entry.get("ttl", self.default_ttl)

    def _evict_oldest(self, count: int) -> None:
        """Evict oldest entries."""
        keys = list(self._cache.keys())[:count]
        for key in keys:
            del self._cache[key]

    def _log_access(self, key: str, hit: bool, latency_ms: float) -> None:
        """Log cache access."""
        entry = AccessLogEntry(
            key=key,
            timestamp=time.time(),
            hit=hit,
            latency_ms=latency_ms,
        )

        self._access_log.append(entry)

        # Trim log if too large
        if len(self._access_log) > self._max_log_size:
            self._access_log = self._access_log[-self._max_log_size:]


# Global instance
_global_terminal: FastTerminal | None = None


def get_fast_terminal() -> FastTerminal:
    """Get or create the global fast terminal."""
    global _global_terminal
    if _global_terminal is None:
        _global_terminal = FastTerminal()
    return _global_terminal
