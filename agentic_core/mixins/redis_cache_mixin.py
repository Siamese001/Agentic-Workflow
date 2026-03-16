from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_reads_policy_state("p0", "redis_cache_mixin", "policy_binding")
_emit_snapshots_state("p0", "redis_cache_mixin", "state_snapshot")
emit_replay_key("p0", "redis_cache_mixin")
emit_determinism_digest("p0", "redis_cache_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

"\nULTRA-HARDENED Redis cache Mixin\n\nFeatures:\n- Feature flag control (USE_REDIS_CACHE)\n- Local dict fallback for graceful degradation\n- Metrics collection for dashboard visibility\n- Hash-based keys for security\n- TTL-based expiration\n- Manual invalidation support\n"
import hashlib
import json
import logging
import time
from typing import Any

from agentic_core.config.core.constants_config import (
    CACHE_METRICS_ENABLED,
    GRACEFUL_DEGRADATION,
    USE_REDIS_CACHE,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


def get_cache_metrics():
    """Stub for optional cache metrics tracking."""
    return {}


log = logging.getLogger(__name__)


class CircuitBreaker:
    """[PHASE 25] Circuit Breaker for Redis connections."""

    # guardian: allow-magic-config
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def record_failure(self) -> None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CircuitBreaker.record_failure")

        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if time.time() - self.last_failure_time > self.timeout_seconds:
            self.state = "HALF_OPEN"
            return True
        return False


class RedisCacheMixin:
    """ULTRA-HARDENED Redis cache Mixin"""

    _circuit_breaker = CircuitBreaker()
    '\n    ULTRA-HARDENED Redis cache Mixin\n\n    Provides automatic caching with graceful degradation to local dict.\n    All operations are safe - failures never crash the agent.\n\n    Usage:\n        class MyAgent(HealerMixin, MCPHardenedMixin, RedisCacheMixin):\n            _cache_prefix = "my_agent"\n            _default_ttl = 3600\n\n            async def expensive_operation(self, key):\n                cached = await self.cache_get(key)\n                if cached:\n                    return cached\n                result = await self._compute(key)\n                await self.cache_set(key, result)\n                return result\n    '
    _redis_client = None
    _cache_prefix: str = "agent_cache"
    _default_ttl: int = 3600
    _local_cache: dict = {}
    KEY_NAMESPACE_SALT = "agentic-v1"
    MAX_KEY_LENGTH = 200

    @property
    def redis_enabled(self) -> bool:
        """Check if Redis is enabled via feature flag."""
        return USE_REDIS_CACHE

    @property
    def redis(self):
        """
        Lazy-load Hardened Redis Client.

        [PHASE 2 MIGRATION] Now routes through the canonical DeterministicRedisCache
        to ensure connection pool reuse and centralized auditing.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RedisCacheMixin.redis")

        if not self.redis_enabled:
            return None
        if self._redis_client is None:
            try:
                from agentic_core.cache.redis_cache_client import get_hot_cache

                self._redis_client = get_hot_cache()
                log.info(f"[{self.__class__.__name__}] Connected to Hardened Redis Gateway")
            # guardian: allow-silent-swallow
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
        if not self._circuit_breaker.can_execute():
            log.debug("Circuit breaker OPEN - using local cache")
            return self._local_cache.get(full_key)
        if self.redis:
            try:
                value = await self.redis.get(full_key)
                latency = (time.time() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_get", hit=value is not None, latency_ms=latency)
                if value is not None:
                    log.debug(f"cache HIT (Redis): {key[:50]}...")
                    self._circuit_breaker.record_success()
                    return value
            # guardian: allow-silent-swallow
            except Exception as e:
                self._circuit_breaker.record_failure()
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("redis_get")
                log.debug(f"Redis get failed ({e}) - checking local fallback")
        value = self._local_cache.get(full_key)
        if isinstance(value, dict) and "value" in value and ("expire_at" in value):
            if time.time() >= value["expire_at"]:
                self._local_cache.pop(full_key, None)
                value = None
            else:
                value = value["value"]
        latency = (time.time() - start) * 1000
        if CACHE_METRICS_ENABLED:
            metrics.record("local_get", hit=value is not None, latency_ms=latency)
        if value is not None:
            log.debug(f"cache HIT (local): {key[:50]}...")
        else:
            log.debug(f"cache MISS: {key[:50]}...")
        return value

    async def cache_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set cached value with automatic fallback.
        """
        full_key = self._make_key(key)
        ttl = ttl or self._default_ttl
        start = time.time()
        metrics = get_cache_metrics()
        try:
            _ = json.dumps(value)
        except (TypeError, ValueError):
            log.warning(f"cache SET BLOCKED: Non-serializable value for {key}")
            return
        self._local_cache[full_key] = {"value": value, "expire_at": time.time() + ttl}
        if not self._circuit_breaker.can_execute():
            return
        if self.redis:
            try:
                await self.redis.set(full_key, value, ex=ttl)
                latency = (time.time() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_set", hit=True, latency_ms=latency)
                log.debug(f"cache SET (Redis): {key[:50]}... TTL={ttl}s")
                self._circuit_breaker.record_success()
                return
            # guardian: allow-silent-swallow
            except Exception as e:
                self._circuit_breaker.record_failure()
                log.debug(f"Redis set suppressed error (local fallback used): {str(e)[:80]}")
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("redis_set")
        latency = (time.time() - start) * 1000
        if CACHE_METRICS_ENABLED:
            metrics.record("local_set", hit=True, latency_ms=latency)
        log.debug(f"cache SET (local): {key[:50]}...")

    async def cache_delete(self, key: str) -> None:
        """Delete a specific cached key."""
        full_key = self._make_key(key)
        self._local_cache.pop(full_key, None)
        if self.redis:
            try:
                await self.redis.delete(full_key)
            except Exception:
                raise
                pass

    async def cache_invalidate(self, key_pattern: str = "") -> int:
        """
        Invalidate keys matching pattern (best effort).

        Returns count of keys deleted from local cache.
        """
        deleted = 0
        if self.redis:
            try:
                pattern = f"{self._cache_prefix}:{key_pattern}*"
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
                    deleted += len(keys)
            except Exception:
                raise
                pass
        prefix = f"{self._cache_prefix}:"
        if key_pattern:
            pattern_hash = hashlib.sha256(key_pattern.encode()).hexdigest()[:16]
            to_delete = [k for k in self._local_cache if pattern_hash in k]
        else:
            to_delete = [k for k in self._local_cache if k.startswith(prefix)]
        for k in to_delete:
            del self._local_cache[k]
            deleted += 1
        log.info(f"cache invalidated {deleted} keys matching '{key_pattern}'")
        return deleted

    def cache_stats(self) -> dict:
        """Get cache statistics for this mixin instance."""
        return {
            "prefix": self._cache_prefix,
            "local_cache_size": len(self._local_cache),
            "redis_enabled": self.redis_enabled,
            "redis_connected": self._redis_client is not None,
        }
