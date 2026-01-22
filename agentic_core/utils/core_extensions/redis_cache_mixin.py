from __future__ import annotations

"""
ULTRA-HARDENED Redis Cache Mixin

Features:
- Feature flag control (USE_REDIS_CACHE)
- Local dict fallback for graceful degradation
- Metrics collection for dashboard visibility
- Hash-based keys for security
- TTL-based expiration
- Manual invalidation support
"""


import hashlib
import logging
import time
from typing import Any

from agentic_core.config.feature_flags import (
    CACHE_METRICS_ENABLED,
    GRACEFUL_DEGRADATION,
    USE_REDIS_CACHE,
)
from agentic_core.observability.cache_metrics import get_cache_metrics

log = logging.getLogger(__name__)


class RedisCacheMixin:
    """
    ULTRA-HARDENED Redis Cache Mixin

    Provides automatic caching with graceful degradation to local dict.
    All operations are safe - failures never crash the agent.

    Usage:
        class MyAgent(HealerMixin, MCPHardenedMixin, RedisCacheMixin):
            _cache_prefix = "my_agent"
            _default_ttl = 3600

            async def expensive_operation(self, key):
                cached = await self.cache_get(key)
                if cached:
                    return cached
                result = await self._compute(key)
                await self.cache_set(key, result)
                return result
    """

    _redis_client = None
    _cache_prefix: str = "agent_cache"
    _default_ttl: int = 3600  # 1 hour
    _local_cache: dict = {}

    KEY_NAMESPACE_SALT = "agentic-v1"
    MAX_KEY_LENGTH = 200

    @property
    def redis_enabled(self) -> bool:
        """Check if Redis is enabled via feature flag."""
        return USE_REDIS_CACHE

    @property
    def redis(self):
        """Lazy-load Redis client with graceful failure."""
        if not self.redis_enabled:
            return None
        if self._redis_client is None:
            try:
                from agentic_core.L2_execution.mcp.caching_redis_mcp_client import get_redis_client

                self._redis_client = get_redis_client()
            except Exception as e:
                if not GRACEFUL_DEGRADATION:
                    raise
                log.warning(f"Redis client init failed ({e}) - using local cache fallback")
                self._redis_client = None
        return self._redis_client

    def _make_key(self, key: str) -> str:
        """Generate secure hash-based cache key."""
        if len(key) > self.MAX_KEY_LENGTH:
            key = key[: self.MAX_KEY_LENGTH - 32] + hashlib.sha256(key.encode()).hexdigest()[:32]
        salted = f"{self.KEY_NAMESPACE_SALT}:{self._cache_prefix}:{key}"
        key_hash = hashlib.sha256(salted.encode()).hexdigest()[:40]
        return f"{self._cache_prefix}:{key_hash}"

    async def cache_get(self, key: str) -> Any | None:
        """
        Get cached value with automatic fallback.

        Returns None on miss or error (never raises).
        """
        full_key = self._make_key(key)
        start = time.time()
        metrics = get_cache_metrics()

        # Try Redis first
        if self.redis:
            try:
                value = await self.redis.get(full_key)
                latency = (time.time() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_get", hit=value is not None, latency_ms=latency)
                if value is not None:
                    log.debug(f"Cache HIT (Redis): {key[:50]}...")
                    return value
            except Exception as e:
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("redis_get")
                log.debug(f"Redis get failed ({e}) - checking local fallback")

        # Local fallback
        value = self._local_cache.get(full_key)
        if isinstance(value, dict) and "value" in value and "expire_at" in value:
            if time.time() >= value["expire_at"]:
                self._local_cache.pop(full_key, None)
                value = None
            else:
                value = value["value"]
        latency = (time.time() - start) * 1000
        if CACHE_METRICS_ENABLED:
            metrics.record("local_get", hit=value is not None, latency_ms=latency)

        if value is not None:
            log.debug(f"Cache HIT (local): {key[:50]}...")
        else:
            log.debug(f"Cache MISS: {key[:50]}...")

        return value

    async def cache_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set cached value with automatic fallback.

        Always stores locally. Attempts Redis if available.
        Never raises on failure.
        """
        full_key = self._make_key(key)
        ttl = ttl or self._default_ttl
        start = time.time()
        metrics = get_cache_metrics()

        # Always store locally first
        self._local_cache[full_key] = {
            "value": value,
            "expire_at": time.time() + ttl,
        }

        # Try Redis
        if self.redis:
            try:
                await self.redis.set(full_key, value, ex=ttl)
                latency = (time.time() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_set", hit=True, latency_ms=latency)
                log.debug(f"Cache SET (Redis): {key[:50]}... TTL={ttl}s")
                return
            except Exception as e:
                log.debug(f"Redis set suppressed error (local fallback used): {str(e)[:80]}")
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("redis_set")
                # Local already contains TTL-enforced entry.

        latency = (time.time() - start) * 1000
        if CACHE_METRICS_ENABLED:
            metrics.record("local_set", hit=True, latency_ms=latency)
        log.debug(f"Cache SET (local): {key[:50]}...")

    async def cache_delete(self, key: str) -> None:
        """Delete a specific cached key."""
        full_key = self._make_key(key)

        # Delete from local
        self._local_cache.pop(full_key, None)

        # Delete from Redis
        if self.redis:
            try:
                await self.redis.delete(full_key)
            except Exception:
                pass

    async def cache_invalidate(self, key_pattern: str = "") -> int:
        """
        Invalidate keys matching pattern (best effort).

        Returns count of keys deleted from local cache.
        """
        deleted = 0

        # Try Redis pattern delete
        if self.redis:
            try:
                pattern = f"{self._cache_prefix}:{key_pattern}*"
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
                    deleted += len(keys)
            except Exception:
                pass

        # Clear local matches
        prefix = f"{self._cache_prefix}:"
        if key_pattern:
            # Pattern match (simplified - prefix match)
            pattern_hash = hashlib.sha256(key_pattern.encode()).hexdigest()[:16]
            to_delete = [k for k in self._local_cache if pattern_hash in k]
        else:
            # Clear all for this prefix
            to_delete = [k for k in self._local_cache if k.startswith(prefix)]

        for k in to_delete:
            del self._local_cache[k]
            deleted += 1

        log.info(f"Cache invalidated {deleted} keys matching '{key_pattern}'")
        return deleted

    def cache_stats(self) -> dict:
        """Get cache statistics for this mixin instance."""
        return {
            "prefix": self._cache_prefix,
            "local_cache_size": len(self._local_cache),
            "redis_enabled": self.redis_enabled,
            "redis_connected": self._redis_client is not None,
        }
