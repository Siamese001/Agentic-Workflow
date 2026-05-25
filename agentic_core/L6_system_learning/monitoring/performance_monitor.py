"""Performance monitoring for system learning signal enhancement.

Tracks signal processing performance, latency, and health metrics.
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from agentic_core.L6_system_learning.config.feature_flags import get_feature_flags

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PerformanceMetric:
    """A single performance metric measurement."""

    metric_name: str
    value: float
    timestamp_utc: int
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp_utc": self.timestamp_utc,
            "tags": self.tags,
        }


@dataclass(frozen=True, slots=True)
class SignalHealthMetrics:
    """Health metrics for signal processing."""

    total_signals_processed: int
    successful_signals: int
    failed_signals: int
    average_latency_ms: float
    p95_latency_ms: float
    error_rate: float
    timestamp_utc: int

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_signals_processed == 0:
            return 0.0
        return self.successful_signals / self.total_signals_processed


class PerformanceMonitor:
    """Monitors performance and health of system learning signals."""

    def __init__(self, max_history_size: int = 10000):
        """Initialize performance monitor.

        Args:
            max_history_size: Maximum number of metrics to keep in memory
        """
        self._max_history_size = max_history_size
        self._metrics_lock = Lock()
        self._metrics_history: deque[PerformanceMetric] = deque(maxlen=max_history_size)
        self._signal_counters: dict[str, dict[str, int]] = defaultdict(
            lambda: {
                "total": 0,
                "success": 0,
                "failure": 0,
            }
        )
        self._latency_samples: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=1000))
        self._last_health_check = 0
        self._health_cache: SignalHealthMetrics | None = None
        self._health_cache_ttl = 30000  # 30 seconds cache TTL

    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for categorization
        """
        flags = get_feature_flags()
        if not flags.enable_performance_monitoring:
            return

        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            timestamp_utc=int(time.time() * 1000),
            tags=tags or {},
        )

        with self._metrics_lock:
            self._metrics_history.append(metric)

        # Log significant metrics
        if metric_name.endswith("_latency_ms") and value > 1000:
            logger.warning(f"High latency detected: {metric_name}={value}ms")
        elif metric_name.endswith("_error_rate") and value > 0.1:
            logger.warning(f"High error rate detected: {metric_name}={value:.2%}")

    def record_signal_processing(
        self,
        signal_type: str,
        success: bool,
        latency_ms: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record signal processing metrics.

        Args:
            signal_type: Type of signal processed
            success: Whether processing was successful
            latency_ms: Processing latency in milliseconds
            tags: Optional tags for categorization
        """
        flags = get_feature_flags()
        if not flags.enable_performance_monitoring:
            return

        # Update counters
        with self._metrics_lock:
            counters = self._signal_counters[signal_type]
            counters["total"] += 1
            if success:
                counters["success"] += 1
            else:
                counters["failure"] += 1

            # Store latency sample
            self._latency_samples[signal_type].append(latency_ms)

        # Record individual metrics
        self.record_metric(
            metric_name=f"{signal_type}_processing_latency_ms",
            value=latency_ms,
            tags=tags,
        )

        # Record success/failure
        status = "success" if success else "failure"
        self.record_metric(
            metric_name=f"{signal_type}_processing_{status}",
            value=1.0,
            tags=tags,
        )

    def get_signal_health(self, signal_type: str | None = None) -> SignalHealthMetrics:
        """Get health metrics for signal processing.

        Args:
            signal_type: Optional signal type to filter by

        Returns:
            Signal health metrics
        """
        flags = get_feature_flags()
        if not flags.enable_performance_monitoring:
            return SignalHealthMetrics(
                total_signals_processed=0,
                successful_signals=0,
                failed_signals=0,
                average_latency_ms=0.0,
                p95_latency_ms=0.0,
                error_rate=0.0,
                timestamp_utc=int(time.time() * 1000),
            )

        now = int(time.time() * 1000)

        # Check cache
        with self._metrics_lock:
            if (
                self._health_cache
                and signal_type is None
                and now - self._health_cache.timestamp_utc < self._health_cache_ttl
            ):
                return self._health_cache

        # Calculate metrics
        total_signals = 0
        successful_signals = 0
        failed_signals = 0
        all_latencies = []

        with self._metrics_lock:
            if signal_type:
                # Single signal type
                if signal_type in self._signal_counters:
                    counters = self._signal_counters[signal_type]
                    total_signals = counters["total"]
                    successful_signals = counters["success"]
                    failed_signals = counters["failure"]
                    all_latencies = list(self._latency_samples[signal_type])
            else:
                # All signal types
                for sig_type, counters in self._signal_counters.items():
                    total_signals += counters["total"]
                    successful_signals += counters["success"]
                    failed_signals += counters["failure"]
                    all_latencies.extend(self._latency_samples[sig_type])

        # Calculate latency metrics
        if all_latencies:
            average_latency = sum(all_latencies) / len(all_latencies)
            sorted_latencies = sorted(all_latencies)
            p95_index = int(len(sorted_latencies) * 0.95)
            p95_latency = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]
        else:
            average_latency = 0.0
            p95_latency = 0.0

        # Calculate error rate
        error_rate = failed_signals / total_signals if total_signals > 0 else 0.0

        health_metrics = SignalHealthMetrics(
            total_signals_processed=total_signals,
            successful_signals=successful_signals,
            failed_signals=failed_signals,
            average_latency_ms=average_latency,
            p95_latency_ms=p95_latency,
            error_rate=error_rate,
            timestamp_utc=now,
        )

        # Cache for all signals
        if signal_type is None:
            with self._metrics_lock:
                self._health_cache = health_metrics
                self._last_health_check = now

        return health_metrics

    def get_metrics_summary(
        self,
        metric_name: str | None = None,
        since_utc: int | None = None,
    ) -> dict[str, Any]:
        """Get summary of performance metrics.

        Args:
            metric_name: Optional metric name to filter by
            since_utc: Optional timestamp to filter from

        Returns:
            Metrics summary
        """
        flags = get_feature_flags()
        if not flags.enable_performance_monitoring:
            return {"status": "disabled"}

        with self._metrics_lock:
            metrics = list(self._metrics_history)

        # Apply filters
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        if since_utc:
            metrics = [m for m in metrics if m.timestamp_utc >= since_utc]

        if not metrics:
            return {"status": "no_data"}

        # Calculate summary statistics
        values = [m.value for m in metrics]
        summary = {
            "metric_name": metric_name or "all",
            "count": len(metrics),
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": sum(values) / len(values),
            "latest_timestamp": max(m.timestamp_utc for m in metrics),
            "earliest_timestamp": min(m.timestamp_utc for m in metrics),
        }

        # Add percentiles
        sorted_values = sorted(values)
        summary["p50"] = sorted_values[int(len(sorted_values) * 0.5)]
        summary["p95"] = sorted_values[int(len(sorted_values) * 0.95)]
        summary["p99"] = sorted_values[int(len(sorted_values) * 0.99)]

        return summary

    def check_alert_conditions(self) -> list[dict[str, Any]]:
        """Check for alert conditions.

        Returns:
            List of alert conditions
        """
        flags = get_feature_flags()
        if not flags.enable_performance_monitoring:
            return []

        alerts = []

        # Check overall health
        health = self.get_signal_health()

        # High error rate alert
        if health.error_rate > 0.1:
            alerts.append(
                {
                    "alert_type": "high_error_rate",
                    "severity": "high" if health.error_rate > 0.2 else "medium",
                    "message": f"High error rate: {health.error_rate:.2%}",
                    "timestamp_utc": health.timestamp_utc,
                    "metrics": {
                        "error_rate": health.error_rate,
                        "total_signals": health.total_signals_processed,
                    },
                }
            )

        # High latency alert
        if health.p95_latency_ms > 5000:
            alerts.append(
                {
                    "alert_type": "high_latency",
                    "severity": "high" if health.p95_latency_ms > 10000 else "medium",
                    "message": f"High P95 latency: {health.p95_latency_ms}ms",
                    "timestamp_utc": health.timestamp_utc,
                    "metrics": {
                        "p95_latency_ms": health.p95_latency_ms,
                        "avg_latency_ms": health.average_latency_ms,
                    },
                }
            )

        # Low success rate alert
        if health.success_rate < 0.9 and health.total_signals_processed > 10:
            alerts.append(
                {
                    "alert_type": "low_success_rate",
                    "severity": "high" if health.success_rate < 0.8 else "medium",
                    "message": f"Low success rate: {health.success_rate:.2%}",
                    "timestamp_utc": health.timestamp_utc,
                    "metrics": {
                        "success_rate": health.success_rate,
                        "total_signals": health.total_signals_processed,
                    },
                }
            )

        return alerts

    def reset_metrics(self) -> None:
        """Reset all metrics (for testing or maintenance)."""
        with self._metrics_lock:
            self._metrics_history.clear()
            self._signal_counters.clear()
            self._latency_samples.clear()
            self._health_cache = None
            self._last_health_check = 0

    def export_metrics(self, format_type: str = "json") -> str:
        """Export metrics in specified format.

        Args:
            format_type: Export format ('json' or 'csv')

        Returns:
            Exported metrics as string
        """
        with self._metrics_lock:
            metrics = list(self._metrics_history)

        if format_type == "json":
            return json.dumps([m.to_dict() for m in metrics], indent=2)
        elif format_type == "csv":
            if not metrics:
                return ""

            headers = ["metric_name", "value", "timestamp_utc", "tags"]
            rows = []
            for metric in metrics:
                tags_str = json.dumps(metric.tags) if metric.tags else ""
                rows.append(
                    [
                        metric.metric_name,
                        str(metric.value),
                        str(metric.timestamp_utc),
                        tags_str,
                    ]
                )

            return "\n".join([",".join(headers)] + [",".join(row) for row in rows])
        else:
            raise ValueError(f"Unsupported format: {format_type}")


# Global performance monitor instance
_performance_monitor: PerformanceMonitor | None = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.

    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def record_signal_latency(signal_type: str, latency_ms: float, success: bool = True) -> None:
    """Convenience function to record signal processing latency.

    Args:
        signal_type: Type of signal processed
        latency_ms: Processing latency in milliseconds
        success: Whether processing was successful
    """
    monitor = get_performance_monitor()
    monitor.record_signal_processing(signal_type, success, latency_ms)


def check_system_health() -> dict[str, Any]:
    """Check overall system health.

    Returns:
        System health summary
    """
    monitor = get_performance_monitor()
    health = monitor.get_signal_health()
    alerts = monitor.check_alert_conditions()

    return {
        "health": {
            "total_signals": health.total_signals_processed,
            "success_rate": health.success_rate,
            "error_rate": health.error_rate,
            "avg_latency_ms": health.average_latency_ms,
            "p95_latency_ms": health.p95_latency_ms,
            "timestamp_utc": health.timestamp_utc,
        },
        "alerts": alerts,
        "status": "healthy" if not alerts else "degraded",
    }
