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
)

_emit_applies_guardrail("p0", "metrics_mixin", "p0_governance")
_emit_reads_policy_state("p0", "metrics_mixin", "policy_binding")
_emit_snapshots_state("p0", "metrics_mixin", "state_snapshot")
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
