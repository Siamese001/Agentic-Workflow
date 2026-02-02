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
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

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

    def stop_timer(
        self,
        operation: str,
        metadata: dict[str, Any] | None = None,
    ) -> float:
        """Stop a timer and record the metric."""
        if operation not in self._start_times:
            logger.warning(f"Timer not started for: {operation}")
            return 0.0

        start = self._start_times.pop(operation)
        duration_ms = (time.perf_counter() - start) * 1000

        metric = TimingMetric(
            name=operation,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

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
        metric = TimingMetric(
            name=operation,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )

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
        return {
            op: summary for op in self._metrics if (summary := self.get_summary(op)) is not None
        }

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


def timed(
    collector: MetricsCollector | None = None,
    operation_name: str | None = None,
) -> Callable[[F], F]:
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

            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000

                if collector:
                    collector.record_metric(name, duration_ms, {"success": False, "error": str(e)})

                raise

        return wrapper  # type: ignore

    return decorator


class PerformanceThresholds:
    """Defines performance thresholds for operations."""

    def __init__(self):
        self._thresholds: dict[str, float] = {}
        self._default_threshold_ms = 1000.0

    def set_threshold(self, operation: str, max_duration_ms: float) -> None:
        """Set the maximum allowed duration for an operation."""
        self._thresholds[operation] = max_duration_ms

    def get_threshold(self, operation: str) -> float:
        """Get the threshold for an operation."""
        return self._thresholds.get(operation, self._default_threshold_ms)

    def check_threshold(self, operation: str, duration_ms: float) -> bool:
        """Check if duration is within threshold."""
        threshold = self.get_threshold(operation)
        return duration_ms <= threshold

    def get_violations(
        self,
        collector: MetricsCollector,
    ) -> list[tuple[str, float, float]]:
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

    def time_operation(self, operation: str) -> "OperationTimer":
        """Create a context manager for timing an operation."""
        return OperationTimer(self, operation)

    def record(
        self,
        operation: str,
        duration_ms: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a timing metric."""
        self.collector.record_metric(operation, duration_ms, metadata)

    def get_report(self) -> dict[str, Any]:
        """Generate a performance report."""
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
            "violations": [
                {"operation": op, "duration_ms": d, "threshold_ms": t} for op, d, t in violations
            ],
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

    def __enter__(self) -> "OperationTimer":
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        self.monitor.record(
            self.operation,
            self.duration_ms,
            {"success": exc_type is None},
        )


# Global monitor instance
_global_monitor: PerformanceMonitor | None = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor("global")
    return _global_monitor
