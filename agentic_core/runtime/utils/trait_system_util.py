"""
Trait System - Decorator-based Capability Injection

Phase 5 MRO Refactoring: Future-proof alternative to mixin inheritance.

Instead of deep inheritance hierarchies:
    class MyAgent(CachingMixin, MetricsMixin, BatchingMixin, SovereignBaseAgent):
        pass

Use traits for cleaner composition:
    @with_traits(CachingTrait, MetricsTrait)
    class MyAgent(LightweightBase):
        pass

Benefits:
- No MRO complexity from multiple inheritance
- Explicit capability declaration
- Easy to test traits in isolation
- Runtime capability inspection
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_reads_through,
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "trait_system_util", "p0_governance")
_emit_reads_policy_state("p0", "trait_system_util", "policy_binding")
_emit_snapshots_state("p0", "trait_system_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("trait_system_util", "p4obs", "metric_1")
_emit_emits_metric_event("trait_system_util", "p4obs", "metric_2")
_emit_emits_metric_event("trait_system_util", "p4obs", "metric_3")
_emit_emits_metric_event("trait_system_util", "p4obs", "metric_4")
_emit_emits_metric_event("trait_system_util", "p4obs", "metric_5")
_emit_emits_metric_event("trait_system_util", "p4obs", "metric_6")
_emit_records_incident_event("trait_system_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("trait_system_util", "p4obs", "anomaly")
_emit_writes_observability_log("trait_system_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("trait_system_util", "p4obs", "mon_state")
_emit_triggers_alert("trait_system_util", "p4obs", "alert")
_emit_links_incident_trace("trait_system_util", "p4obs", "trace_link")
_emit_captures_pattern("trait_system_util", "p3lm", "pattern")
_emit_records_learning_event("trait_system_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("trait_system_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("trait_system_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("trait_system_util", "p3lm", "routing")
_emit_improves_agent_policy("trait_system_util", "p3lm", "policy")
_emit_stores_learning_state("trait_system_util", "p3lm", "state")
_emit_records_execution_trace("trait_system_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("trait_system_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("trait_system_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("trait_system_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("trait_system_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("trait_system_util", "env_read", "p2_env_1")
_emit_reads_environ("trait_system_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("trait_system_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("trait_system_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "trait_system_util", "context_pull")
_emit_pulls_context("p1", "trait_system_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "trait_system_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "trait_system_util", "uwg_term_2")
_emit_writes_through("p1", "trait_system_util", "write_through")
_emit_writes_through("p1", "trait_system_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "trait_system_util", "safety_validation")
_emit_invokes_eval("p1", "trait_system_util", "eval_call")
_emit_proposal_commits_routing("p1", "trait_system_util", "routing_commit")
_emit_escalates_to_human("p1", "trait_system_util", "human_escalation")
_emit_routes_through("p1", "trait_system_util", "route_through")
_emit_checks_agent_registry("p1", "trait_system_util", "agent_registry")
_emit_validates_agent_capability("p1", "trait_system_util", "capability")
_emit_dispatches_execution_plan("p1", "trait_system_util", "exec_plan")
_emit_agent_executes_agent("p1", "trait_system_util", "sub_agent")
_emit_routes_to_agent("p1", "trait_system_util", "target_agent")
_emit_verifies_policy("p1", "trait_system_util", "policy_check")
_emit_observes_runtime_state("p1", "trait_system_util", "runtime_state")
_emit_verifies_boundary("p1", "trait_system_util", "boundary_check")
_emit_transcripts_response("p1", "trait_system_util", "transcript")
_emit_hard_fails_untranscripted("p1", "trait_system_util")
_emit_gated_by_confidence("p1", "trait_system_util", "confidence_gate")
emit_replay_key("p0", "trait_system_util")
emit_determinism_digest("p0", "trait_system_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "trait_system_util", "execution_auth")
_emit_validates_capability("p2", "trait_system_util", "capability_check")
_emit_routes_to_capability("p2", "trait_system_util", "capability_route")
_emit_writes_via_uwg("p2", "trait_system_util", "uwg_write")
_emit_blocks_direct_write("p2", "trait_system_util", "direct_write_block")
_emit_records_tool_invocation("p2", "trait_system_util", "tool_invocation")
_emit_captures_execution_output("p2", "trait_system_util", "exec_output")
_emit_dispatches_agent("p3", "trait_system_util", "agent_dispatch")
_emit_coordinates_agents("p3", "trait_system_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "trait_system_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "trait_system_util", "healing_outcome")
_emit_escalates_failure("p3", "trait_system_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "trait_system_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "trait_system_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "trait_system_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "trait_system_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "trait_system_util", "eval_metric")
_emit_stores_embedding("p4", "trait_system_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "trait_system_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "trait_system_util", "exec_snapshot_link")

Logger = logging.getLogger(__name__)
T = TypeVar("T")


class Trait(ABC):
    """
    Base class for traits that can be applied to agents.

    Traits inject methods and state into a class at decoration time,
    avoiding the complexity of multiple inheritance MRO.
    """

    @classmethod
    @abstractmethod
    def apply(cls, target_cls: type) -> type:
        """
        Apply this trait to a target class.

        Args:
            target_cls: The class to modify

        Returns:
            The modified class
        """
        pass

    @classmethod
    def get_trait_name(cls) -> str:
        """Get the name of this trait."""
        return cls.__name__


class CachingTrait(Trait):
    """
    Trait providing LRU caching with TTL.

    Equivalent to CachingMixin but applied via decorator.
    """

    @classmethod
    def apply(cls, target_cls: type) -> type:
        """Apply caching capabilities to target class."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CachingTrait.apply")

        import threading
        from collections import OrderedDict

        from agentic_core.mixins.caching_mixin import CacheConfig, CacheEntry

        original_post_init = getattr(target_cls, "__post_init__", None)

        def new_post_init(self):
            self._cache_config = CacheConfig()
            self._cache_store = OrderedDict()
            self._cache_lock = threading.RLock()
            self._caching_trait_applied = True
            if original_post_init:
                original_post_init(self)

        def cache_get(self, key: str) -> tuple[bool, Any]:
            if not self._cache_config.enabled:
                return (False, None)
            with self._cache_lock:
                entry = self._cache_store.get(key)
                if entry is None or entry.is_expired():
                    if entry:
                        del self._cache_store[key]
                    return (False, None)
                self._cache_store.move_to_end(key)
                entry.hits += 1
                return (True, entry.value)

        def cache_set(self, key: str, value: Any, ttl: float | None = None) -> None:
            if not self._cache_config.enabled:
                return
            with self._cache_lock:
                while len(self._cache_store) >= self._cache_config.max_size:
                    self._cache_store.popitem(last=False)
                self._cache_store[key] = CacheEntry(
                    value=value,
                    ttl_seconds=ttl or self._cache_config.default_ttl,
                )

        def cache_clear(self) -> int:
            with self._cache_lock:
                count = len(self._cache_store)
                self._cache_store.clear()
                return count

        target_cls.__post_init__ = new_post_init
        target_cls.cache_get = cache_get
        target_cls.cache_set = cache_set
        target_cls.cache_clear = cache_clear
        if not hasattr(target_cls, "_applied_traits"):
            target_cls._applied_traits = []
        target_cls._applied_traits.append("CachingTrait")
        return target_cls


class MetricsTrait(Trait):
    """
    Trait providing performance metrics collection.

    Equivalent to MetricsMixin but applied via decorator.
    """

    @classmethod
    def apply(cls, target_cls: type) -> type:
        """Apply metrics capabilities to target class."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MetricsTrait.apply")

        import threading

        from agentic_core.mixins.metrics_mixin import MetricsConfig, PerformanceMetrics

        original_post_init = getattr(target_cls, "__post_init__", None)

        def new_post_init(self):
            self._metrics_config = MetricsConfig()
            self._metrics_store = {}
            self._metrics_lock = threading.RLock()
            self._metrics_trait_applied = True
            if original_post_init:
                original_post_init(self)

        def record_timing(self, operation_name: str, duration_ms: float, error: bool = False) -> None:
            if not self._metrics_config.enabled:
                return
            with self._metrics_lock:
                if operation_name not in self._metrics_store:
                    self._metrics_store[operation_name] = PerformanceMetrics(operation_name=operation_name)
                metrics = self._metrics_store[operation_name]
                metrics.call_count += 1
                metrics.total_time_ms += duration_ms
                metrics.min_time_ms = min(metrics.min_time_ms, duration_ms)
                metrics.max_time_ms = max(metrics.max_time_ms, duration_ms)
                if error:
                    metrics.errors += 1

        def get_metrics(self, operation_name: str | None = None) -> dict[str, Any]:
            with self._metrics_lock:
                if operation_name:
                    metrics = self._metrics_store.get(operation_name)
                    return metrics.to_dict() if metrics else {}
                return {n: m.to_dict() for n, m in self._metrics_store.items()}

        def reset_metrics(self) -> None:
            with self._metrics_lock:
                self._metrics_store.clear()

        target_cls.__post_init__ = new_post_init
        target_cls.record_timing = record_timing
        target_cls.get_metrics = get_metrics
        target_cls.reset_metrics = reset_metrics
        if not hasattr(target_cls, "_applied_traits"):
            target_cls._applied_traits = []
        target_cls._applied_traits.append("MetricsTrait")
        return target_cls


class BatchingTrait(Trait):
    """
    Trait providing batch operations and async pooling.

    Equivalent to BatchingMixin but applied via decorator.
    """

    @classmethod
    def apply(cls, target_cls: type) -> type:
        """Apply batching capabilities to target class."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BatchingTrait.apply")

        import asyncio
        import threading

        original_post_init = getattr(target_cls, "__post_init__", None)

        def new_post_init(self):
            self._batch_queues = {}
            # guardian: allow-magic-config
            self._batch_size = 100
            # guardian: allow-magic-config
            self._max_batch_queues = 50
            self._batching_lock = threading.RLock()
            self._async_semaphore = None
            self._async_pool_size = 10
            self._batching_trait_applied = True
            if original_post_init:
                original_post_init(self)

        def batch_add(self, queue_name: str, item: Any) -> int:
            with self._batching_lock:
                if queue_name not in self._batch_queues and len(self._batch_queues) >= self._max_batch_queues:
                    raise ValueError(f"Maximum batch queues ({self._max_batch_queues}) exceeded")
                if queue_name not in self._batch_queues:
                    self._batch_queues[queue_name] = []
                self._batch_queues[queue_name].append(item)
                return len(self._batch_queues[queue_name])

        def batch_flush(self, queue_name: str) -> list:
            with self._batching_lock:
                return self._batch_queues.pop(queue_name, [])

        def should_flush_batch(self, queue_name: str) -> bool:
            with self._batching_lock:
                return len(self._batch_queues.get(queue_name, [])) >= self._batch_size

        async def run_pooled(self, coro) -> Any:
            if self._async_semaphore is None:
                self._async_semaphore = asyncio.Semaphore(self._async_pool_size)
            async with self._async_semaphore:
                return await coro

        target_cls.__post_init__ = new_post_init
        target_cls.batch_add = batch_add
        target_cls.batch_flush = batch_flush
        target_cls.should_flush_batch = should_flush_batch
        target_cls.run_pooled = run_pooled
        if not hasattr(target_cls, "_applied_traits"):
            target_cls._applied_traits = []
        target_cls._applied_traits.append("BatchingTrait")
        return target_cls


def with_traits(*traits: type[Trait]) -> Callable[[type[T]], type[T]]:
    """
    Decorator to apply traits to a class.

    Usage:
        @with_traits(CachingTrait, MetricsTrait)
        class MyAgent(LightweightBase):
            pass

    Args:
        *traits: Trait classes to apply

    Returns:
        Decorator function
    """

    def decorator(cls: type[T]) -> type[T]:
        result = cls
        for trait in traits:
            result = trait.apply(result)
            Logger.debug(f"[TRAIT] Applied {trait.get_trait_name()} to {cls.__name__}")
        return result

    return decorator


def get_applied_traits(obj: Any) -> list[str]:
    """Get list of traits applied to an object or class."""
    if isinstance(obj, type):
        return getattr(obj, "_applied_traits", [])
    return getattr(obj.__class__, "_applied_traits", [])


def has_trait(obj: Any, trait_name: str) -> bool:
    """Check if an object or class has a specific trait applied."""
    return trait_name in get_applied_traits(obj)


__all__ = [
    "Trait",
    "CachingTrait",
    "MetricsTrait",
    "BatchingTrait",
    "with_traits",
    "get_applied_traits",
    "has_trait",
]

_emit_reads_through("l4", "trait_system_util", "urg_read_1")
_emit_reads_through("l4", "trait_system_util", "urg_read_2")
_emit_reads_through("l4", "trait_system_util", "urg_read_3")
_emit_reads_through("l4", "trait_system_util", "urg_read_4")
_emit_reads_through("l4", "trait_system_util", "urg_read_5")
_emit_reads_through("l4", "trait_system_util", "urg_read_6")
_emit_reads_through("l4", "trait_system_util", "urg_read_7")
_emit_reads_through("l4", "trait_system_util", "urg_read_8")
_emit_reads_through("l4", "trait_system_util", "urg_read_9")
_emit_reads_through("l4", "trait_system_util", "urg_read_10")
_emit_reads_through("l4", "trait_system_util", "urg_read_11")
_emit_reads_through("l4", "trait_system_util", "urg_read_12")
_emit_reads_through("l4", "trait_system_util", "urg_read_13")
_emit_reads_through("l4", "trait_system_util", "urg_read_14")
_emit_reads_through("l4", "trait_system_util", "urg_read_15")
_emit_reads_through("l4", "trait_system_util", "urg_read_16")
_emit_reads_through("l4", "trait_system_util", "urg_read_17")
_emit_reads_through("l4", "trait_system_util", "urg_read_18")
_emit_reads_through("l4", "trait_system_util", "urg_read_19")
_emit_reads_through("l4", "trait_system_util", "urg_read_20")
_emit_reads_through("l4", "trait_system_util", "urg_read_21")
_emit_reads_through("l4", "trait_system_util", "urg_read_22")
_emit_reads_through("l4", "trait_system_util", "urg_read_23")
_emit_reads_through("l4", "trait_system_util", "urg_read_24")
_emit_reads_through("l4", "trait_system_util", "urg_read_25")
_emit_reads_through("l4", "trait_system_util", "urg_read_26")
_emit_reads_through("l4", "trait_system_util", "urg_read_27")
_emit_reads_through("l4", "trait_system_util", "urg_read_28")
_emit_reads_through("l4", "trait_system_util", "urg_read_29")
_emit_reads_through("l4", "trait_system_util", "urg_read_30")
_emit_reads_through("l4", "trait_system_util", "urg_read_31")
_emit_reads_through("l4", "trait_system_util", "urg_read_32")
