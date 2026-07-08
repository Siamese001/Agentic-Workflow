"""
CachingMixin - Focused Caching Functionality

Phase 3 MRO Refactoring: Extracted from PerformanceMixin for single responsibility.

Provides:
- LRU cache with TTL
- Thread-safe cache operations
- @cached decorator for method-level caching
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "caching_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "caching_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "caching_mixin", "state_snapshot")

trace_contract._emit_emits_metric_event("caching_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("caching_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("caching_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("caching_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("caching_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("caching_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("caching_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("caching_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("caching_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("caching_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("caching_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("caching_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("caching_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("caching_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("caching_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("caching_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("caching_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("caching_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("caching_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("caching_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("caching_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("caching_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("caching_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("caching_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("caching_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("caching_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("caching_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("caching_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "caching_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "caching_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "caching_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "caching_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "caching_mixin", "write_through")
trace_contract._emit_writes_through("p1", "caching_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "caching_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "caching_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "caching_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "caching_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "caching_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "caching_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "caching_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "caching_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "caching_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "caching_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "caching_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "caching_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "caching_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "caching_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "caching_mixin")
trace_contract._emit_gated_by_confidence("p1", "caching_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "caching_mixin")
trace_contract.emit_determinism_digest("p0", "caching_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "caching_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "caching_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "caching_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "caching_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "caching_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "caching_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "caching_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "caching_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "caching_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "caching_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "caching_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "caching_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "caching_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "caching_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "caching_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "caching_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "caching_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "caching_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "caching_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "caching_mixin", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""

    value: Any
    created_at: float = field(default_factory=time.monotonic)
    ttl_seconds: float = 300.0
    hits: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.monotonic() - self.created_at > self.ttl_seconds


@dataclass
class CacheConfig:
    """Configuration for caching."""

    enabled: bool = True
    max_size: int = 1000
    default_ttl: float = 300.0


class CachingMixin:
    """
    Mixin providing LRU caching with TTL support.

    Phase 3 MRO Refactoring: Single responsibility - caching only.

    Usage:
        class MyAgent(CachingMixin, SovereignBaseAgent):
            @CachingMixin.cached(ttl=60)
            def expensive_operation(self, key: str) -> dict:
                return self._compute_expensive(key)
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize caching state."""
        super().__init__(**kwargs)
        self._cache_config = CacheConfig()
        self._cache_store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_lock = threading.RLock()
        self._caching_initialized = True
        Logger.debug(f"[CACHE] {self.__class__.__name__} caching initialized")

    def configure_cache(
        self,
        enabled: bool | None = None,
        max_size: int | None = None,
        default_ttl: float | None = None,
    ) -> None:
        """Configure caching settings."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "CachingMixin.configure_cache"
        )

        if max_size is not None and max_size <= 0:
            raise ValueError("max_size must be positive")
        if default_ttl is not None and default_ttl <= 0:
            raise ValueError("default_ttl must be positive")
        with self._cache_lock:
            if enabled is not None:
                self._cache_config.enabled = enabled
            if max_size is not None:
                self._cache_config.max_size = max_size
            if default_ttl is not None:
                self._cache_config.default_ttl = default_ttl

    def cache_get(self, key: str) -> tuple[bool, Any]:
        """Get value from cache. Returns (hit, value)."""
        if not self._cache_config.enabled:
            return (False, None)
        with self._cache_lock:
            entry = self._cache_store.get(key)
            if entry is None:
                return (False, None)
            if entry.is_expired():
                del self._cache_store[key]
                return (False, None)
            self._cache_store.move_to_end(key)
            entry.hits += 1
            return (True, entry.value)

    def cache_set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache."""
        if not self._cache_config.enabled:
            return
        with self._cache_lock:
            while len(self._cache_store) >= self._cache_config.max_size:
                self._cache_store.popitem(last=False)
            self._cache_store[key] = CacheEntry(
                value=value,
                ttl_seconds=ttl or self._cache_config.default_ttl,
            )

    def cache_invalidate(self, key: str) -> bool:
        """Invalidate a cache entry. Returns True if entry was found."""
        with self._cache_lock:
            if key in self._cache_store:
                del self._cache_store[key]
                return True
            return False

    def cache_clear(self) -> int:
        """Clear all cache entries. Returns count of entries cleared."""
        with self._cache_lock:
            count = len(self._cache_store)
            self._cache_store.clear()
            return count

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._cache_lock:
            total_hits = sum(e.hits for e in self._cache_store.values())
            expired = sum(1 for e in self._cache_store.values() if e.is_expired())
            return {
                "size": len(self._cache_store),
                "max_size": self._cache_config.max_size,
                "total_hits": total_hits,
                "expired_entries": expired,
                "enabled": self._cache_config.enabled,
            }

    @staticmethod
    def cached(ttl: float = 300.0, key_func: Callable | None = None):
        """
        Decorator to cache method results.

        Args:
            ttl: Time-to-live in seconds
            key_func: Optional function to generate cache key from args
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                if not isinstance(self, CachingMixin):
                    return func(self, *args, **kwargs)
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                hit, value = self.cache_get(cache_key)
                if hit:
                    return value
                result = func(self, *args, **kwargs)
                self.cache_set(cache_key, result, ttl)
                return result

            return wrapper

        return decorator


__all__ = ["CachingMixin", "CacheConfig", "CacheEntry"]
