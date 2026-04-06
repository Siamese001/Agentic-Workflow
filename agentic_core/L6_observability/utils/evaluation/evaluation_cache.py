"""
agentic_core/L6_observability/evaluation/evaluation_cache.py

Wave 3.1: Evaluation Caching

Implements evaluation result caching with:
- Cache key generation from inputs
- TTL-based expiration
- Cache invalidation
- Hit rate tracking
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "evaluation_cache")
emit_determinism_digest("p0", "evaluation_cache")
_emit_applies_guardrail("p0", "evaluation_cache", "p0_governance")
_emit_snapshots_state("p0", "evaluation_cache", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

logger = logging.getLogger(__name__)


@dataclass
class CachedEvaluation:
    """Cached evaluation result."""

    cache_key: str
    result: Any
    timestamp: float
    ttl_sec: float


class EvaluationCache:
    """Cache for evaluation results with TTL and invalidation.

    Features:
    - Automatic cache key generation
    - TTL-based expiration
    - Manual invalidation
    - Hit rate tracking
    """

    def __init__(self, default_ttl_sec: float = 3600.0) -> None:
        """Initialize evaluation cache.

        Args:
            default_ttl_sec: Default TTL in seconds (default 1 hour)
        """
        self._default_ttl_sec = default_ttl_sec
        self._cache: dict[str, CachedEvaluation] = {}
        self._hits = 0
        self._misses = 0

    def get(self, cache_key: str) -> Any | None:
        """Get cached evaluation result.

        Args:
            cache_key: Cache key

        Returns:
            Cached result or None if not found/expired
        """
        if cache_key not in self._cache:
            self._misses += 1
            return None

        cached = self._cache[cache_key]

        # Check expiration
        if time.time() - cached.timestamp > cached.ttl_sec:
            del self._cache[cache_key]
            self._misses += 1
            logger.debug("CACHE_EXPIRED: key=%s", cache_key[:12])
            return None

        self._hits += 1
        logger.debug("CACHE_HIT: key=%s", cache_key[:12])
        return cached.result

    def put(
        self,
        cache_key: str,
        result: Any,
        ttl_sec: float | None = None,
    ) -> None:
        """Put evaluation result in cache.

        Args:
            cache_key: Cache key
            result: Evaluation result
            ttl_sec: TTL in seconds (defaults to default_ttl_sec)
        """
        if ttl_sec is None:
            ttl_sec = self._default_ttl_sec

        cached = CachedEvaluation(
            cache_key=cache_key,
            result=result,
            timestamp=time.time(),
            ttl_sec=ttl_sec,
        )

        self._cache[cache_key] = cached
        logger.debug("CACHE_PUT: key=%s ttl=%.0fs", cache_key[:12], ttl_sec)

    def invalidate(self, cache_key: str) -> bool:
        """Invalidate cache entry.

        Args:
            cache_key: Cache key to invalidate

        Returns:
            True if entry was found and removed
        """
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug("CACHE_INVALIDATED: key=%s", cache_key[:12])
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("CACHE_CLEARED")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }

    @staticmethod
    def generate_key(eval_type: str, inputs: dict[str, Any]) -> str:
        """Generate cache key from evaluation type and inputs.

        Args:
            eval_type: Type of evaluation
            inputs: Evaluation inputs

        Returns:
            Cache key (SHA256 hash)
        """
        # Create deterministic string from inputs
        input_str = f"{eval_type}:{str(sorted(inputs.items()))}"
        return hashlib.sha256(input_str.encode()).hexdigest()


# Global instance
_eval_cache: EvaluationCache | None = None


def get_eval_cache() -> EvaluationCache:
    """Get global evaluation cache instance."""
    global _eval_cache
    if _eval_cache is None:
        _eval_cache = EvaluationCache()
    return _eval_cache


def reset_eval_cache() -> None:
    """Reset global evaluation cache (for testing)."""
    global _eval_cache
    _eval_cache = None


__all__ = [
    "CachedEvaluation",
    "EvaluationCache",
    "get_eval_cache",
    "reset_eval_cache",
]
