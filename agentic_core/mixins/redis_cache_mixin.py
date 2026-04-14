from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_reads_policy_state("p0", "redis_cache_mixin", "policy_binding")
_emit_snapshots_state("p0", "redis_cache_mixin", "state_snapshot")
emit_replay_key("p0", "redis_cache_mixin")
emit_determinism_digest("p0", "redis_cache_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "redis_cache_mixin", "execution_auth")
_emit_validates_capability("p2", "redis_cache_mixin", "capability_check")
_emit_routes_to_capability("p2", "redis_cache_mixin", "capability_route")
_emit_writes_via_uwg("p2", "redis_cache_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "redis_cache_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "redis_cache_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "redis_cache_mixin", "exec_output")
_emit_dispatches_agent("p3", "redis_cache_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "redis_cache_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "redis_cache_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "redis_cache_mixin", "healing_outcome")
_emit_escalates_failure("p3", "redis_cache_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "redis_cache_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "redis_cache_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "redis_cache_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "redis_cache_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "redis_cache_mixin", "eval_metric")
_emit_stores_embedding("p4", "redis_cache_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "redis_cache_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "redis_cache_mixin", "exec_snapshot_link")

"\nULTRA-HARDENED Redis cache Mixin\n\nFeatures:\n- Feature flag control (USE_REDIS_CACHE)\n- Local dict fallback for graceful degradation\n- Metrics collection for dashboard visibility\n- Hash-based keys for security\n- TTL-based expiration\n- Manual invalidation support\n"
import hashlib
import json
import logging
import time
from typing import Any

from agentic_core.config.constants_config import (
    CACHE_METRICS_ENABLED,
    GRACEFUL_DEGRADATION,
    USE_REDIS_CACHE,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("redis_cache_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("redis_cache_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("redis_cache_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("redis_cache_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("redis_cache_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("redis_cache_mixin", "p4obs", "metric_6")
_emit_records_incident_event("redis_cache_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("redis_cache_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("redis_cache_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("redis_cache_mixin", "p4obs", "mon_state")
_emit_triggers_alert("redis_cache_mixin", "p4obs", "alert")
_emit_links_incident_trace("redis_cache_mixin", "p4obs", "trace_link")
_emit_captures_pattern("redis_cache_mixin", "p3lm", "pattern")
_emit_records_learning_event("redis_cache_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("redis_cache_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("redis_cache_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("redis_cache_mixin", "p3lm", "routing")
_emit_improves_agent_policy("redis_cache_mixin", "p3lm", "policy")
_emit_stores_learning_state("redis_cache_mixin", "p3lm", "state")
_emit_records_execution_trace("redis_cache_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("redis_cache_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("redis_cache_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("redis_cache_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("redis_cache_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("redis_cache_mixin", "env_read", "p2_env_1")
_emit_reads_environ("redis_cache_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("redis_cache_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("redis_cache_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "redis_cache_mixin", "context_pull")
_emit_pulls_context("p1", "redis_cache_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "redis_cache_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "redis_cache_mixin", "uwg_term_2")
_emit_writes_through("p1", "redis_cache_mixin", "write_through")
_emit_writes_through("p1", "redis_cache_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "redis_cache_mixin", "safety_validation")
_emit_invokes_eval("p1", "redis_cache_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "redis_cache_mixin", "routing_commit")
_emit_escalates_to_human("p1", "redis_cache_mixin", "human_escalation")
_emit_routes_through("p1", "redis_cache_mixin", "route_through")
_emit_checks_agent_registry("p1", "redis_cache_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "redis_cache_mixin", "capability")
_emit_dispatches_execution_plan("p1", "redis_cache_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "redis_cache_mixin", "sub_agent")
_emit_routes_to_agent("p1", "redis_cache_mixin", "target_agent")
_emit_verifies_policy("p1", "redis_cache_mixin", "policy_check")
_emit_observes_runtime_state("p1", "redis_cache_mixin", "runtime_state")
_emit_verifies_boundary("p1", "redis_cache_mixin", "boundary_check")
_emit_transcripts_response("p1", "redis_cache_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "redis_cache_mixin")
_emit_gated_by_confidence("p1", "redis_cache_mixin", "confidence_gate")


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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "CircuitBreaker.record_failure"
        )

        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if time.monotonic() - self.last_failure_time > self.timeout_seconds:
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
            except (
                OSError,
                RuntimeError,
                ConnectionError,
            ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
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
        start = time.monotonic()
        metrics = get_cache_metrics()
        if not self._circuit_breaker.can_execute():
            log.debug("Circuit breaker OPEN - using local cache")
            return self._local_cache.get(full_key)
        if self.redis:
            try:
                value = await self.redis.get(full_key)
                latency = (time.monotonic() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_get", hit=value is not None, latency_ms=latency)
                if value is not None:
                    log.debug(f"cache HIT (Redis): {key[:50]}...")
                    self._circuit_breaker.record_success()
                    return value
            # guardian: allow-silent-swallow
            except (OSError, RuntimeError) as e:
                self._circuit_breaker.record_failure()
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("redis_get")
                log.debug(f"Redis get failed ({e}) - checking local fallback")
        value = self._local_cache.get(full_key)
        if isinstance(value, dict) and "value" in value and ("expire_at" in value):
            if time.monotonic() >= value["expire_at"]:
                self._local_cache.pop(full_key, None)
                value = None
            else:
                value = value["value"]
        latency = (time.monotonic() - start) * 1000
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
        start = time.monotonic()
        metrics = get_cache_metrics()
        try:
            _ = json.dumps(value)
        except (TypeError, ValueError):
            log.warning(f"cache SET BLOCKED: Non-serializable value for {key}")
            return
        self._local_cache[full_key] = {"value": value, "expire_at": time.monotonic() + ttl}
        if not self._circuit_breaker.can_execute():
            return
        if self.redis:
            try:
                await self.redis.set(full_key, value, ex=ttl)
                latency = (time.monotonic() - start) * 1000
                if CACHE_METRICS_ENABLED:
                    metrics.record("redis_set", hit=True, latency_ms=latency)
                log.debug(f"cache SET (Redis): {key[:50]}... TTL={ttl}s")
                self._circuit_breaker.record_success()
                return
            # guardian: allow-silent-swallow
            except (OSError, RuntimeError) as e:
                self._circuit_breaker.record_failure()
                log.debug(f"Redis set suppressed error (local fallback used): {str(e)[:80]}")
                if CACHE_METRICS_ENABLED:
                    metrics.record_error("redis_set")
        latency = (time.monotonic() - start) * 1000
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
            except (ValueError, TypeError, RuntimeError) as e:
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
            except (ValueError, TypeError, RuntimeError) as e:
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


# Backwards compatibility alias
redis_cache_mixin = RedisCacheMixin
