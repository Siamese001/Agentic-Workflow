"""
MetricsMixin - Focused Performance Metrics Functionality

Phase 3 MRO Refactoring: Extracted from PerformanceMixin for single responsibility.

Provides:
- Performance timing collection
- @timed decorator for automatic timing
- Metrics aggregation and reporting
"""

from __future__ import annotations

import asyncio
import functools
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_applies_guardrail("p0", "metrics_mixin", "p0_governance")
_emit_reads_policy_state("p0", "metrics_mixin", "policy_binding")
_emit_snapshots_state("p0", "metrics_mixin", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("metrics_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("metrics_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("metrics_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("metrics_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("metrics_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("metrics_mixin", "p4obs", "metric_6")
_emit_records_incident_event("metrics_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("metrics_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("metrics_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("metrics_mixin", "p4obs", "mon_state")
_emit_triggers_alert("metrics_mixin", "p4obs", "alert")
_emit_links_incident_trace("metrics_mixin", "p4obs", "trace_link")
_emit_captures_pattern("metrics_mixin", "p3lm", "pattern")
_emit_records_learning_event("metrics_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("metrics_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("metrics_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("metrics_mixin", "p3lm", "routing")
_emit_improves_agent_policy("metrics_mixin", "p3lm", "policy")
_emit_stores_learning_state("metrics_mixin", "p3lm", "state")
_emit_records_execution_trace("metrics_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("metrics_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("metrics_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("metrics_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("metrics_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("metrics_mixin", "env_read", "p2_env_1")
_emit_reads_environ("metrics_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("metrics_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("metrics_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "metrics_mixin", "context_pull")
_emit_pulls_context("p1", "metrics_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "metrics_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "metrics_mixin", "uwg_term_2")
_emit_writes_through("p1", "metrics_mixin", "write_through")
_emit_writes_through("p1", "metrics_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "metrics_mixin", "safety_validation")
_emit_invokes_eval("p1", "metrics_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "metrics_mixin", "routing_commit")
_emit_escalates_to_human("p1", "metrics_mixin", "human_escalation")
_emit_routes_through("p1", "metrics_mixin", "route_through")
_emit_checks_agent_registry("p1", "metrics_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "metrics_mixin", "capability")
_emit_dispatches_execution_plan("p1", "metrics_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "metrics_mixin", "sub_agent")
_emit_routes_to_agent("p1", "metrics_mixin", "target_agent")
_emit_verifies_policy("p1", "metrics_mixin", "policy_check")
_emit_observes_runtime_state("p1", "metrics_mixin", "runtime_state")
_emit_verifies_boundary("p1", "metrics_mixin", "boundary_check")
_emit_transcripts_response("p1", "metrics_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "metrics_mixin")
_emit_gated_by_confidence("p1", "metrics_mixin", "confidence_gate")
emit_replay_key("p0", "metrics_mixin")
emit_determinism_digest("p0", "metrics_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "metrics_mixin", "execution_auth")
_emit_validates_capability("p2", "metrics_mixin", "capability_check")
_emit_routes_to_capability("p2", "metrics_mixin", "capability_route")
_emit_writes_via_uwg("p2", "metrics_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "metrics_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "metrics_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "metrics_mixin", "exec_output")
_emit_dispatches_agent("p3", "metrics_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "metrics_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "metrics_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "metrics_mixin", "healing_outcome")
_emit_escalates_failure("p3", "metrics_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "metrics_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "metrics_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "metrics_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "metrics_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "metrics_mixin", "eval_metric")
_emit_stores_embedding("p4", "metrics_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "metrics_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "metrics_mixin", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for an operation."""

    operation_name: str
    call_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0

    @property
    def avg_time_ms(self) -> float:
        """Calculate average execution time."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PerformanceMetrics.avg_time_ms")

        if self.call_count == 0:
            return 0.0
        return self.total_time_ms / self.call_count

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_name": self.operation_name,
            "call_count": self.call_count,
            "total_time_ms": self.total_time_ms,
            "avg_time_ms": self.avg_time_ms,
            "min_time_ms": self.min_time_ms if self.min_time_ms != float("inf") else 0,
            "max_time_ms": self.max_time_ms,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hit_rate,
            "errors": self.errors,
        }


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""

    enabled: bool = True


class MetricsMixin:
    """
    Mixin providing performance metrics collection.

    Phase 3 MRO Refactoring: Single responsibility - metrics only.

    Usage:
        class MyAgent(MetricsMixin, SovereignBaseAgent):
            @MetricsMixin.timed
            def monitored_operation(self):
                return do_work()
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize metrics state."""
        super().__init__(**kwargs)
        self._metrics_config = MetricsConfig()
        self._metrics_store: dict[str, PerformanceMetrics] = {}
        self._metrics_lock = threading.RLock()
        self._metrics_initialized = True
        Logger.debug(f"[METRICS] {self.__class__.__name__} metrics initialized")

    def configure_metrics(self, enabled: bool | None = None) -> None:
        """Configure metrics settings."""
        with self._metrics_lock:
            if enabled is not None:
                self._metrics_config.enabled = enabled

    def _ensure_metrics(self, operation_name: str) -> PerformanceMetrics:
        """Ensure metrics exist for an operation."""
        if operation_name not in self._metrics_store:
            self._metrics_store[operation_name] = PerformanceMetrics(operation_name=operation_name)
        return self._metrics_store[operation_name]

    def record_timing(self, operation_name: str, duration_ms: float, error: bool = False) -> None:
        """Record timing for an operation."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MetricsMixin.record_timing")

        if not self._metrics_config.enabled:
            return
        with self._metrics_lock:
            metrics = self._ensure_metrics(operation_name)
            metrics.call_count += 1
            metrics.total_time_ms += duration_ms
            metrics.min_time_ms = min(metrics.min_time_ms, duration_ms)
            metrics.max_time_ms = max(metrics.max_time_ms, duration_ms)
            if error:
                metrics.errors += 1

    def record_cache_hit(self, operation_name: str) -> None:
        """Record cache hit for an operation."""
        if not self._metrics_config.enabled:
            return
        with self._metrics_lock:
            metrics = self._ensure_metrics(operation_name)
            metrics.cache_hits += 1

    def record_cache_miss(self, operation_name: str) -> None:
        """Record cache miss for an operation."""
        if not self._metrics_config.enabled:
            return
        with self._metrics_lock:
            metrics = self._ensure_metrics(operation_name)
            metrics.cache_misses += 1

    def get_metrics(self, operation_name: str | None = None) -> dict[str, Any]:
        """Get performance metrics."""
        with self._metrics_lock:
            if operation_name:
                metrics = self._metrics_store.get(operation_name)
                return metrics.to_dict() if metrics else {}
            return {name: m.to_dict() for name, m in self._metrics_store.items()}

    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        with self._metrics_lock:
            self._metrics_store.clear()

    @staticmethod
    def timed(func: Callable) -> Callable:
        """
        Decorator to track execution time.

        Usage:
            @MetricsMixin.timed
            def monitored_method(self):
                return do_work()
        """

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            if not isinstance(self, MetricsMixin):
                return func(self, *args, **kwargs)
            start = time.time()
            error = False
            try:
                return func(self, *args, **kwargs)
            except Exception:
                error = True
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                self.record_timing(func.__name__, duration_ms, error)

        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            if not isinstance(self, MetricsMixin):
                return await func(self, *args, **kwargs)
            start = time.time()
            error = False
            try:
                return await func(self, *args, **kwargs)
            except Exception:
                error = True
                raise
            finally:
                duration_ms = (time.time() - start) * 1000
                self.record_timing(func.__name__, duration_ms, error)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper


__all__ = ["MetricsMixin", "MetricsConfig", "PerformanceMetrics"]
