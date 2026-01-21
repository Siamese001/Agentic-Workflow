#!/usr/bin/env python3
"""
Cache metrics module for L6 observability.

Provides cache performance metrics collection and reporting.
"""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Global cache metrics storage
_cache_metrics: dict[str, Any] = {
    "hits": 0,
    "misses": 0,
    "total_requests": 0,
    "last_reset": time.time(),
}


def get_cache_metrics() -> dict[str, Any]:
    """
    Get current cache metrics.

    Returns:
        Dict containing cache hit/miss statistics
    """
    total = _cache_metrics["total_requests"]
    hit_rate = (_cache_metrics["hits"] / total * 100) if total > 0 else 0.0

    return {
        "hits": _cache_metrics["hits"],
        "misses": _cache_metrics["misses"],
        "total_requests": total,
        "hit_rate_percent": round(hit_rate, 2),
        "last_reset": _cache_metrics["last_reset"],
    }


def record_cache_hit() -> None:
    """Record a cache hit."""
    _cache_metrics["hits"] += 1
    _cache_metrics["total_requests"] += 1


def record_cache_miss() -> None:
    """Record a cache miss."""
    _cache_metrics["misses"] += 1
    _cache_metrics["total_requests"] += 1


def reset_cache_metrics() -> None:
    """Reset all cache metrics."""
    global _cache_metrics
    _cache_metrics = {
        "hits": 0,
        "misses": 0,
        "total_requests": 0,
        "last_reset": time.time(),
    }
    logger.info("Cache metrics reset")


class CacheMetricsCollector:
    """Collector for cache performance metrics."""

    def __init__(self, cache_name: str = "default"):
        self.cache_name = cache_name
        self._local_metrics: dict[str, int] = {
            "hits": 0,
            "misses": 0,
        }

    def hit(self) -> None:
        """Record a cache hit."""
        self._local_metrics["hits"] += 1
        record_cache_hit()

    def miss(self) -> None:
        """Record a cache miss."""
        self._local_metrics["misses"] += 1
        record_cache_miss()

    def get_local_metrics(self) -> dict[str, Any]:
        """Get metrics for this specific cache."""
        total = self._local_metrics["hits"] + self._local_metrics["misses"]
        hit_rate = (self._local_metrics["hits"] / total * 100) if total > 0 else 0.0

        return {
            "cache_name": self.cache_name,
            "hits": self._local_metrics["hits"],
            "misses": self._local_metrics["misses"],
            "total": total,
            "hit_rate_percent": round(hit_rate, 2),
        }
