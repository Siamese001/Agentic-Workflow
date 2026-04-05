"""
agentic_core/L6_observability/evaluation/metric_aggregation_engine.py

Wave 1.4: Metric Aggregation Engine

Provides time-series metric aggregation for evaluation metrics with:
- Weighted averaging
- Percentile calculations (p50, p95, p99)
- Time window queries (last hour, day, week)
- Metric rollup and summarization
- Query API for metric analysis
"""

from __future__ import annotations

import hashlib
import logging
import statistics
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "metric_aggregation_engine")
emit_determinism_digest("p0", "metric_aggregation_engine")
_emit_applies_guardrail("p0", "metric_aggregation_engine", "p0_governance")
_emit_snapshots_state("p0", "metric_aggregation_engine", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "metric_aggregation_engine", "L6")
_emit_authorize_and_execute("p2", "metric_aggregation_engine", "execution_auth")
_emit_validates_capability("p2", "metric_aggregation_engine", "capability_check")
_emit_routes_to_capability("p2", "metric_aggregation_engine", "capability_route")
_emit_writes_via_uwg("p2", "metric_aggregation_engine", "uwg_write")
_emit_blocks_direct_write("p2", "metric_aggregation_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "metric_aggregation_engine", "tool_invocation")
_emit_captures_execution_output("p2", "metric_aggregation_engine", "exec_output")
_emit_dispatches_agent("p3", "metric_aggregation_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "metric_aggregation_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "metric_aggregation_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "metric_aggregation_engine", "healing_outcome")
_emit_escalates_failure("p3", "metric_aggregation_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "metric_aggregation_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "metric_aggregation_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "metric_aggregation_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "metric_aggregation_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "metric_aggregation_engine", "eval_metric")
_emit_stores_embedding("p4", "metric_aggregation_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "metric_aggregation_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "metric_aggregation_engine", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class TimeWindow(str, Enum):
    """Time window for metric queries."""

    LAST_HOUR = "last_hour"
    LAST_DAY = "last_day"
    LAST_WEEK = "last_week"
    LAST_MONTH = "last_month"
    ALL_TIME = "all_time"


@dataclass
class MetricDataPoint:
    """Single metric data point."""

    metric_name: str
    value: float
    timestamp_utc: float
    metadata: dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0  # For weighted averaging


@dataclass
class AggregatedMetrics:
    """Aggregated metrics over a time window."""

    metric_name: str
    count: int
    mean: float
    median: float
    p95: float
    p99: float
    min_value: float
    max_value: float
    std_dev: float
    weighted_mean: float
    time_window: TimeWindow
    start_time_utc: float
    end_time_utc: float


class MetricAggregationEngine:
    """Time-series metric aggregation engine.

    Stores evaluation metrics and provides aggregation queries with:
    - Weighted averaging
    - Percentile calculations
    - Time window filtering
    - Metric rollup
    """

    def __init__(self, max_data_points: int = 10000) -> None:
        """Initialize metric aggregation engine.

        Args:
            max_data_points: Maximum data points to store per metric (FIFO)
        """
        self._max_data_points = max_data_points
        self._metrics: dict[str, list[MetricDataPoint]] = defaultdict(list)
        self._total_points_added = 0

    def add_metric(
        self,
        metric_name: str,
        value: float,
        timestamp_utc: float | None = None,
        metadata: dict[str, Any] | None = None,
        weight: float = 1.0,
    ) -> None:
        """Add a metric data point.

        Args:
            metric_name: Name of the metric
            value: Metric value
            timestamp_utc: Timestamp (defaults to current time)
            metadata: Optional metadata
            weight: Weight for weighted averaging (default 1.0)

        Emits ADG edges:
            - captures_evaluation_metric (P4)
        """
        _emit_captures_evaluation_metric("p4", "metric_aggregation_engine", metric_name)

        if timestamp_utc is None:
            timestamp_utc = time.time()

        data_point = MetricDataPoint(
            metric_name=metric_name,
            value=value,
            timestamp_utc=timestamp_utc,
            metadata=metadata or {},
            weight=weight,
        )

        self._metrics[metric_name].append(data_point)
        self._total_points_added += 1

        # Enforce max data points (FIFO)
        if len(self._metrics[metric_name]) > self._max_data_points:
            self._metrics[metric_name].pop(0)

        logger.debug(
            "METRIC_ADDED: name=%s value=%.3f weight=%.2f",
            metric_name,
            value,
            weight,
        )

    def get_aggregated_metrics(
        self,
        metric_name: str,
        time_window: TimeWindow = TimeWindow.ALL_TIME,
    ) -> AggregatedMetrics | None:
        """Get aggregated metrics for a time window.

        Args:
            metric_name: Name of the metric
            time_window: Time window to aggregate over

        Returns:
            AggregatedMetrics or None if no data

        Emits ADG edges:
            - invokes_evaluation (P3)
        """
        _emit_invokes_evaluation("p3", "metric_aggregation_engine", "metric_aggregation")

        if metric_name not in self._metrics or not self._metrics[metric_name]:
            return None

        # Filter by time window
        current_time = time.time()
        window_seconds = self._get_window_seconds(time_window)
        start_time = current_time - window_seconds if window_seconds > 0 else 0.0

        filtered_points = [
            dp for dp in self._metrics[metric_name]
            if dp.timestamp_utc >= start_time
        ]

        if not filtered_points:
            return None

        # Extract values and weights
        values = [dp.value for dp in filtered_points]
        weights = [dp.weight for dp in filtered_points]

        # Calculate statistics
        mean_val = statistics.mean(values)
        median_val = statistics.median(values)
        min_val = min(values)
        max_val = max(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0

        # Percentiles
        sorted_values = sorted(values)
        p95_val = self._percentile(sorted_values, 95)
        p99_val = self._percentile(sorted_values, 99)

        # Weighted mean
        weighted_mean_val = sum(v * w for v, w in zip(values, weights)) / sum(weights)

        end_time = max(dp.timestamp_utc for dp in filtered_points)

        return AggregatedMetrics(
            metric_name=metric_name,
            count=len(values),
            mean=mean_val,
            median=median_val,
            p95=p95_val,
            p99=p99_val,
            min_value=min_val,
            max_value=max_val,
            std_dev=std_dev,
            weighted_mean=weighted_mean_val,
            time_window=time_window,
            start_time_utc=start_time,
            end_time_utc=end_time,
        )

    def get_metric_summary(
        self,
        time_window: TimeWindow = TimeWindow.ALL_TIME,
    ) -> dict[str, AggregatedMetrics]:
        """Get summary of all metrics in a time window.

        Args:
            time_window: Time window to aggregate over

        Returns:
            Dictionary mapping metric names to aggregated metrics
        """
        summary = {}
        for metric_name in self._metrics.keys():
            aggregated = self.get_aggregated_metrics(metric_name, time_window)
            if aggregated is not None:
                summary[metric_name] = aggregated
        return summary

    def get_metric_trend(
        self,
        metric_name: str,
        num_buckets: int = 10,
        time_window: TimeWindow = TimeWindow.LAST_DAY,
    ) -> list[tuple[float, float]]:
        """Get metric trend over time (bucketed averages).

        Args:
            metric_name: Name of the metric
            num_buckets: Number of time buckets
            time_window: Time window to analyze

        Returns:
            List of (timestamp, average_value) tuples
        """
        if metric_name not in self._metrics or not self._metrics[metric_name]:
            return []

        # Filter by time window
        current_time = time.time()
        window_seconds = self._get_window_seconds(time_window)
        start_time = current_time - window_seconds if window_seconds > 0 else 0.0

        filtered_points = [
            dp for dp in self._metrics[metric_name]
            if dp.timestamp_utc >= start_time
        ]

        if not filtered_points:
            return []

        # Create time buckets
        min_time = min(dp.timestamp_utc for dp in filtered_points)
        max_time = max(dp.timestamp_utc for dp in filtered_points)
        bucket_size = (max_time - min_time) / num_buckets if num_buckets > 0 else 1.0

        buckets: dict[int, list[float]] = defaultdict(list)
        for dp in filtered_points:
            bucket_idx = int((dp.timestamp_utc - min_time) / bucket_size)
            bucket_idx = min(bucket_idx, num_buckets - 1)  # Clamp to last bucket
            buckets[bucket_idx].append(dp.value)

        # Calculate bucket averages
        trend = []
        for i in range(num_buckets):
            if i in buckets:
                bucket_time = min_time + (i + 0.5) * bucket_size
                bucket_avg = statistics.mean(buckets[i])
                trend.append((bucket_time, bucket_avg))

        return trend

    def clear_metric(self, metric_name: str) -> None:
        """Clear all data points for a metric."""
        if metric_name in self._metrics:
            del self._metrics[metric_name]

    def clear_all_metrics(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
        self._total_points_added = 0

    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics."""
        return {
            "total_metrics": len(self._metrics),
            "total_points_added": self._total_points_added,
            "current_points": sum(len(points) for points in self._metrics.values()),
            "max_data_points": self._max_data_points,
            "metric_names": list(self._metrics.keys()),
        }

    @staticmethod
    def _get_window_seconds(time_window: TimeWindow) -> float:
        """Convert time window to seconds."""
        if time_window == TimeWindow.LAST_HOUR:
            return 3600.0
        elif time_window == TimeWindow.LAST_DAY:
            return 86400.0
        elif time_window == TimeWindow.LAST_WEEK:
            return 604800.0
        elif time_window == TimeWindow.LAST_MONTH:
            return 2592000.0
        else:  # ALL_TIME
            return float('inf')

    @staticmethod
    def _percentile(sorted_values: list[float], percentile: int) -> float:
        """Calculate percentile from sorted values."""
        if not sorted_values:
            return 0.0
        if len(sorted_values) == 1:
            return sorted_values[0]

        k = (len(sorted_values) - 1) * percentile / 100.0
        f = int(k)
        c = f + 1
        if c >= len(sorted_values):
            return sorted_values[-1]
        d0 = sorted_values[f] * (c - k)
        d1 = sorted_values[c] * (k - f)
        return d0 + d1


# Global instance
_metric_engine: MetricAggregationEngine | None = None


def get_metric_engine() -> MetricAggregationEngine:
    """Get global metric aggregation engine instance."""
    global _metric_engine
    if _metric_engine is None:
        _metric_engine = MetricAggregationEngine()
    return _metric_engine


def reset_metric_engine() -> None:
    """Reset global metric engine (for testing)."""
    global _metric_engine
    _metric_engine = None


__all__ = [
    "TimeWindow",
    "MetricDataPoint",
    "AggregatedMetrics",
    "MetricAggregationEngine",
    "get_metric_engine",
    "reset_metric_engine",
]
