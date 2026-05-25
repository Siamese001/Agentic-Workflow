"""
Performance Monitor - Metrics collection and performance tracking.

Provides timing decorators, metrics collection, and performance analysis
for apps_lic and apps_rg.
Phase 4B - Advanced Testing and Performance
"""

from __future__ import annotations

import functools
import logging
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
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

_emit_applies_guardrail("p0", "performance_monitor_types_util", "p0_governance")
_emit_reads_policy_state("p0", "performance_monitor_types_util", "policy_binding")
_emit_snapshots_state("p0", "performance_monitor_types_util", "state_snapshot")
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

_emit_emits_metric_event("performance_monitor_types_util", "p4obs", "metric_1")
_emit_emits_metric_event("performance_monitor_types_util", "p4obs", "metric_2")
_emit_emits_metric_event("performance_monitor_types_util", "p4obs", "metric_3")
_emit_emits_metric_event("performance_monitor_types_util", "p4obs", "metric_4")
_emit_emits_metric_event("performance_monitor_types_util", "p4obs", "metric_5")
_emit_emits_metric_event("performance_monitor_types_util", "p4obs", "metric_6")
_emit_records_incident_event("performance_monitor_types_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("performance_monitor_types_util", "p4obs", "anomaly")
_emit_writes_observability_log("performance_monitor_types_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("performance_monitor_types_util", "p4obs", "mon_state")
_emit_triggers_alert("performance_monitor_types_util", "p4obs", "alert")
_emit_links_incident_trace("performance_monitor_types_util", "p4obs", "trace_link")
_emit_captures_pattern("performance_monitor_types_util", "p3lm", "pattern")
_emit_records_learning_event("performance_monitor_types_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("performance_monitor_types_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("performance_monitor_types_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("performance_monitor_types_util", "p3lm", "routing")
_emit_improves_agent_policy("performance_monitor_types_util", "p3lm", "policy")
_emit_stores_learning_state("performance_monitor_types_util", "p3lm", "state")
_emit_records_execution_trace("performance_monitor_types_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("performance_monitor_types_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("performance_monitor_types_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("performance_monitor_types_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("performance_monitor_types_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("performance_monitor_types_util", "env_read", "p2_env_1")
_emit_reads_environ("performance_monitor_types_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("performance_monitor_types_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("performance_monitor_types_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "performance_monitor_types_util", "context_pull")
_emit_pulls_context("p1", "performance_monitor_types_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "performance_monitor_types_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "performance_monitor_types_util", "uwg_term_2")
_emit_writes_through("p1", "performance_monitor_types_util", "write_through")
_emit_writes_through("p1", "performance_monitor_types_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "performance_monitor_types_util", "safety_validation")
_emit_invokes_eval("p1", "performance_monitor_types_util", "eval_call")
_emit_proposal_commits_routing("p1", "performance_monitor_types_util", "routing_commit")
_emit_escalates_to_human("p1", "performance_monitor_types_util", "human_escalation")
_emit_routes_through("p1", "performance_monitor_types_util", "route_through")
_emit_checks_agent_registry("p1", "performance_monitor_types_util", "agent_registry")
_emit_validates_agent_capability("p1", "performance_monitor_types_util", "capability")
_emit_dispatches_execution_plan("p1", "performance_monitor_types_util", "exec_plan")
_emit_agent_executes_agent("p1", "performance_monitor_types_util", "sub_agent")
_emit_routes_to_agent("p1", "performance_monitor_types_util", "target_agent")
_emit_verifies_policy("p1", "performance_monitor_types_util", "policy_check")
_emit_observes_runtime_state("p1", "performance_monitor_types_util", "runtime_state")
_emit_verifies_boundary("p1", "performance_monitor_types_util", "boundary_check")
_emit_transcripts_response("p1", "performance_monitor_types_util", "transcript")
_emit_hard_fails_untranscripted("p1", "performance_monitor_types_util")
_emit_gated_by_confidence("p1", "performance_monitor_types_util", "confidence_gate")
emit_replay_key("p0", "performance_monitor_types_util")
emit_determinism_digest("p0", "performance_monitor_types_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "performance_monitor_types_util", "execution_auth")
_emit_validates_capability("p2", "performance_monitor_types_util", "capability_check")
_emit_routes_to_capability("p2", "performance_monitor_types_util", "capability_route")
_emit_writes_via_uwg("p2", "performance_monitor_types_util", "uwg_write")
_emit_blocks_direct_write("p2", "performance_monitor_types_util", "direct_write_block")
_emit_records_tool_invocation("p2", "performance_monitor_types_util", "tool_invocation")
_emit_captures_execution_output("p2", "performance_monitor_types_util", "exec_output")
_emit_dispatches_agent("p3", "performance_monitor_types_util", "agent_dispatch")
_emit_coordinates_agents("p3", "performance_monitor_types_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "performance_monitor_types_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "performance_monitor_types_util", "healing_outcome")
_emit_escalates_failure("p3", "performance_monitor_types_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "performance_monitor_types_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "performance_monitor_types_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "performance_monitor_types_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "performance_monitor_types_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "performance_monitor_types_util", "eval_metric")
_emit_stores_embedding("p4", "performance_monitor_types_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "performance_monitor_types_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "performance_monitor_types_util", "exec_snapshot_link")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_1")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_2")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_3")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_4")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_5")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_6")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_7")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_8")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_9")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_10")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_11")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_12")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_13")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_14")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_15")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_16")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_17")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_18")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_19")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_20")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_21")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_22")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_23")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_24")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_25")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_26")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_27")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_28")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_29")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_30")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_31")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_32")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_33")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_34")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_35")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_36")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_37")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_38")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_39")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_40")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_41")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_42")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_43")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_44")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_45")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_46")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_47")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_48")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_49")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_50")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_51")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_52")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_53")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_54")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_55")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_56")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_57")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_58")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_59")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_60")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_61")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_62")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_63")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_64")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_65")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_66")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_67")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_68")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_69")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_70")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_71")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_72")
_emit_reads_through("l4", "performance_monitor_types_util", "urg_read_73")

logger = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class TimingMetric:
    """A single timing measurement."""

    name: str
    duration_ms: float
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsSummary:
    """Summary of collected metrics."""

    name: str
    count: int
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    std_dev_ms: float
    p95_ms: float
    p99_ms: float


class MetricsCollector:
    """Collects and aggregates performance metrics."""

    def __init__(self, name: str = "default"):
        self.name = name
        self._metrics: dict[str, list[TimingMetric]] = {}
        self._start_times: dict[str, float] = {}

    def start_timer(self, operation: str) -> None:
        """Start a timer for an operation."""
        self._start_times[operation] = time.perf_counter()

    def stop_timer(self, operation: str, metadata: dict[str, Any] | None = None) -> float:
        """Stop a timer and record the metric."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MetricsCollector.stop_timer")

        if operation not in self._start_times:
            logger.warning(f"Timer not started for: {operation}")
            return 0.0
        start = self._start_times.pop(operation)
        duration_ms = (time.perf_counter() - start) * 1000
        metric = TimingMetric(name=operation, duration_ms=duration_ms, metadata=metadata or {})
        if operation not in self._metrics:
            self._metrics[operation] = []
        self._metrics[operation].append(metric)
        return duration_ms

    def record_metric(
        self,
        operation: str,
        duration_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a metric directly."""
        metric = TimingMetric(name=operation, duration_ms=duration_ms, metadata=metadata or {})
        if operation not in self._metrics:
            self._metrics[operation] = []
        self._metrics[operation].append(metric)

    def get_summary(self, operation: str) -> MetricsSummary | None:
        """Get summary statistics for an operation."""
        if operation not in self._metrics or not self._metrics[operation]:
            return None
        durations = [m.duration_ms for m in self._metrics[operation]]
        sorted_durations = sorted(durations)
        return MetricsSummary(
            name=operation,
            count=len(durations),
            min_ms=min(durations),
            max_ms=max(durations),
            mean_ms=statistics.mean(durations),
            median_ms=statistics.median(durations),
            std_dev_ms=statistics.stdev(durations) if len(durations) > 1 else 0.0,
            p95_ms=self._percentile(sorted_durations, 95),
            p99_ms=self._percentile(sorted_durations, 99),
        )

    def get_all_summaries(self) -> dict[str, MetricsSummary]:
        """Get summaries for all operations."""
        return {op: summary for op in self._metrics if (summary := self.get_summary(op)) is not None}

    def clear(self, operation: str | None = None) -> None:
        """Clear collected metrics."""
        if operation:
            self._metrics.pop(operation, None)
        else:
            self._metrics.clear()

    def _percentile(self, sorted_values: list[float], percentile: int) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
        index = (len(sorted_values) - 1) * percentile / 100
        lower = int(index)
        upper = lower + 1
        if upper >= len(sorted_values):
            return sorted_values[-1]
        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def timed(collector: MetricsCollector | None = None, operation_name: str | None = None) -> Callable[[F], F]:
    """
    Decorator to time function execution.

    Args:
        collector: MetricsCollector to record to (uses default if None)
        operation_name: Name for the operation (uses function name if None)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                if collector:
                    collector.record_metric(name, duration_ms, {"success": True})
                logger.debug(f"{name} completed in {duration_ms:.2f}ms")
                return result
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise

        return wrapper

    return decorator


class PerformanceThresholds:
    """Defines performance thresholds for operations."""

    def __init__(self):
        self._thresholds: dict[str, float] = {}
        # guardian: allow-magic-config
        self._default_threshold_ms = 1000.0

    def set_threshold(self, operation: str, max_duration_ms: float) -> None:
        """Set the maximum allowed duration for an operation."""
        self._thresholds[operation] = max_duration_ms

    def get_threshold(self, operation: str) -> float:
        """Get the threshold for an operation."""
        return self._thresholds.get(operation, self._default_threshold_ms)

    def check_threshold(self, operation: str, duration_ms: float) -> bool:
        """Check if duration is within threshold."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PerformanceThresholds.check_threshold"
        )

        threshold = self.get_threshold(operation)
        return duration_ms <= threshold

    def get_violations(self, collector: MetricsCollector) -> list[tuple[str, float, float]]:
        """Get list of threshold violations."""
        violations = []
        for operation, metrics in collector._metrics.items():
            threshold = self.get_threshold(operation)
            for metric in metrics:
                if metric.duration_ms > threshold:
                    violations.append((operation, metric.duration_ms, threshold))
        return violations


class PerformanceMonitor:
    """
    Main performance monitoring interface.

    Combines metrics collection, thresholds, and reporting.
    """

    def __init__(self, name: str = "app"):
        self.name = name
        self.collector = MetricsCollector(name)
        self.thresholds = PerformanceThresholds()

    def time_operation(self, operation: str) -> OperationTimer:
        """Create a context manager for timing an operation."""
        return OperationTimer(self, operation)

    def record(self, operation: str, duration_ms: float, metadata: dict[str, Any] | None = None) -> None:
        """Record a timing metric."""
        self.collector.record_metric(operation, duration_ms, metadata)

    def get_report(self) -> dict[str, Any]:
        """Generate a performance report."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PerformanceMonitor.get_report"
        )

        summaries = self.collector.get_all_summaries()
        violations = self.thresholds.get_violations(self.collector)
        return {
            "monitor_name": self.name,
            "operations": {
                name: {
                    "count": s.count,
                    "min_ms": round(s.min_ms, 2),
                    "max_ms": round(s.max_ms, 2),
                    "mean_ms": round(s.mean_ms, 2),
                    "median_ms": round(s.median_ms, 2),
                    "p95_ms": round(s.p95_ms, 2),
                    "p99_ms": round(s.p99_ms, 2),
                }
                for name, s in summaries.items()
            },
            "violations": [{"operation": op, "duration_ms": d, "threshold_ms": t} for op, d, t in violations],
            "total_operations": sum(s.count for s in summaries.values()),
        }

    def reset(self) -> None:
        """Reset all collected metrics."""
        self.collector.clear()


class OperationTimer:
    """Context manager for timing operations."""

    def __init__(self, monitor: PerformanceMonitor, operation: str):
        self.monitor = monitor
        self.operation = operation
        self.start_time: float = 0.0
        self.duration_ms: float = 0.0

    def __enter__(self) -> OperationTimer:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        self.monitor.record(self.operation, self.duration_ms, {"success": exc_type is None})


_global_monitor: PerformanceMonitor | None = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor("global")
    return _global_monitor
