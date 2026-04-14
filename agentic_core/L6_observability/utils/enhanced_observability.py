"""Enhanced Observability System - Advanced monitoring and alerting.

Provides comprehensive monitoring, alerting, and observability features
for the tracing and Runtime ADG system with real-time metrics and health checks.

FEATURES:
- Real-time system health monitoring
- Advanced metrics collection and aggregation
- Intelligent alerting with thresholds
- Performance trend analysis
- System capacity planning
- Automated health checks
- Comprehensive dashboard data

USAGE:
    monitor = EnhancedObservability()
    monitor.start_monitoring()

    health = monitor.get_system_health()
    alerts = monitor.get_active_alerts()
"""

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import psutil

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from tqdm import tqdm

emit_determinism_digest("enhanced_observability", "enhanced_observability_digest")
record_execution_trace("enhanced_observability", "enhanced_observability_trace")

Logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class HealthStatus(Enum):
    """System health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class SystemMetric:
    """System metric data point."""

    name: str
    value: float
    unit: str
    timestamp: float
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """System alert."""

    id: str
    name: str
    description: str
    severity: AlertSeverity
    status: str
    timestamp: float
    resolved_timestamp: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Health check result."""

    name: str
    status: HealthStatus
    message: str
    timestamp: float
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health."""

    status: HealthStatus
    score: float  # 0-100
    checks: list[HealthCheck]
    metrics: dict[str, SystemMetric]
    alerts: list[Alert]
    timestamp: float


class EnhancedObservability:
    """
    Enhanced observability system with comprehensive monitoring.

    Provides real-time metrics, health checks, alerting, and
    performance monitoring for the tracing system.
    """

    def __init__(self) -> None:
        """Initialize enhanced observability system."""
        self._lock = threading.RLock()
        self._interval_seconds: float = 10.0
        self._stop_event = threading.Event()
        # Metrics storage
        self._metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._current_metrics: dict[str, SystemMetric] = {}

        # Health monitoring
        self._health_checks: dict[str, callable] = {}
        self._health_history: deque = deque(maxlen=100)

        # Alerting system
        self._active_alerts: dict[str, Alert] = {}
        self._alert_history: deque = deque(maxlen=1000)
        self._alert_thresholds: dict[str, dict[str, Any]] = {}

        # Monitoring state
        self._monitoring_active: bool = False
        self._monitoring_thread: threading.Thread | None = None
        self._shutdown_requested: bool = False

        # Performance tracking
        self._performance_trends: dict[str, list[float]] = defaultdict(list)

        # Initialize default health checks and alert thresholds
        self._initialize_health_checks()
        self._initialize_alert_thresholds()

    def _initialize_health_checks(self) -> None:
        """Initialize default health checks."""
        self._health_checks = {
            "memory_usage": self._check_memory_usage,
            "cpu_usage": self._check_cpu_usage,
            "disk_usage": self._check_disk_usage,
            "tracing_system": self._check_tracing_system,
            "runtime_adg": self._check_runtime_adg,
            "span_collection": self._check_span_collection,
            "performance_metrics": self._check_performance_metrics,
        }

    def _initialize_alert_thresholds(self) -> None:
        """Initialize default alert thresholds."""
        self._alert_thresholds = {
            "memory_usage": {
                "warning": 70.0,
                "critical": 90.0,
                "unit": "percent",
            },
            "cpu_usage": {
                "warning": 70.0,
                "critical": 90.0,
                "unit": "percent",
            },
            "disk_usage": {
                "warning": 80.0,
                "critical": 95.0,
                "unit": "percent",
            },
            "error_rate": {
                "warning": 0.05,
                "critical": 0.10,
                "unit": "rate",
            },
            "response_time": {
                "warning": 1000.0,
                "critical": 5000.0,
                "unit": "ms",
            },
            "span_processing_rate": {
                "warning": 100.0,
                "critical": 50.0,
                "unit": "spans_per_second",
            },
        }

    def start_monitoring(self, interval_seconds: float = 10.0) -> None:
        """Start enhanced monitoring."""
        if self._monitoring_active:
            Logger.warning("[OBSERVABILITY] Monitoring already active")
            return

        self._monitoring_active = True
        self._shutdown_requested = False
        self._interval_seconds = max(1.0, interval_seconds)
        self._stop_event.clear()

        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="EnhancedObservability",
        )
        self._monitoring_thread.start()

        Logger.info(f"[OBSERVABILITY] Started enhanced monitoring with {self._interval_seconds}s interval")

    def stop_monitoring(self) -> None:
        """Stop enhanced monitoring."""
        if not self._monitoring_active:
            return

        self._shutdown_requested = True
        self._monitoring_active = False
        self._stop_event.set()

        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5.0)

        Logger.info("[OBSERVABILITY] Stopped enhanced monitoring")

    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring_active and not self._shutdown_requested:
            try:
                start_time = time.time()

                # Collect system metrics
                self._collect_system_metrics()

                # Run health checks
                self._run_health_checks()

                # Check for alerts
                self._check_alerts()

                # Update performance trends
                self._update_performance_trends()

                # Cleanup old data
                self._cleanup_old_data()

                # Sleep until next iteration
                elapsed = time.time() - start_time
                sleep_time = max(0.1, self._interval_seconds - elapsed)
                if self._stop_event.wait(timeout=sleep_time):
                    break

            except Exception as e:  # guardian: allow-broad-exception -- monitoring loop must not die on transient collection errors; all errors are logged
                Logger.error(f"[OBSERVABILITY] Monitoring loop error: {e}")
                if self._stop_event.wait(timeout=min(5.0, self._interval_seconds)):
                    break

    def _collect_system_metrics(self) -> None:
        """Collect comprehensive system metrics."""
        timestamp = time.time()

        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()

            # Store metrics
            metrics = {
                "system_cpu_percent": SystemMetric("system_cpu_percent", cpu_percent, "percent", timestamp),
                "system_memory_percent": SystemMetric(
                    "system_memory_percent", memory.percent, "percent", timestamp
                ),
                "system_memory_used_gb": SystemMetric(
                    "system_memory_used_gb", memory.used / 1024**3, "GB", timestamp
                ),
                "system_disk_percent": SystemMetric(
                    "system_disk_percent", disk.percent, "percent", timestamp
                ),
                "process_memory_mb": SystemMetric(
                    "process_memory_mb", process_memory.rss / 1024**2, "MB", timestamp
                ),
                "process_cpu_percent": SystemMetric("process_cpu_percent", process_cpu, "percent", timestamp),
                "process_threads": SystemMetric("process_threads", process.num_threads(), "count", timestamp),
            }

            # Update current metrics
            with self._lock:
                self._current_metrics.update(metrics)
                for name, metric in metrics.items():
                    self._metrics_history[name].append(metric)

            # Collect tracing-specific metrics
            self._collect_tracing_metrics(timestamp)

        except Exception as e:
            Logger.error(f"[OBSERVABILITY] Failed to collect system metrics: {e}")

    def _collect_tracing_metrics(self, timestamp: float) -> None:
        """Collect tracing-specific metrics."""
        try:
            # Try to get tracing system metrics
            from agentic_core.mixins.auto_span_collector import get_global_collector

            collector = get_global_collector()
            stats = collector.get_collection_stats()

            tracing_metrics = {
                "tracing_spans_collected": SystemMetric(
                    "tracing_spans_collected", stats.get("total_spans_collected", 0), "count", timestamp
                ),
                "tracing_agents_registered": SystemMetric(
                    "tracing_agents_registered", stats.get("agents_registered", 0), "count", timestamp
                ),
                "tracing_buffer_size": SystemMetric(
                    "tracing_buffer_size", stats.get("buffer_size", 0), "count", timestamp
                ),
                "tracing_collection_errors": SystemMetric(
                    "tracing_collection_errors", stats.get("collection_errors", 0), "count", timestamp
                ),
                "tracing_runtime_adg_enabled": SystemMetric(
                    "tracing_runtime_adg_enabled",
                    1.0 if stats.get("runtime_adg_enabled") else 0.0,
                    "boolean",
                    timestamp,
                ),
            }

            with self._lock:
                self._current_metrics.update(tracing_metrics)
                for name, metric in tracing_metrics.items():
                    self._metrics_history[name].append(metric)

        except Exception as e:  # guardian: allow-broad-exception -- tracing metrics collection is best-effort; import and attribute errors are expected
            Logger.debug(f"[OBSERVABILITY] Failed to collect tracing metrics: {e}")

        try:
            # Try to get performance optimized collector metrics
            from agentic_core.mixins.performance_optimized_collector import get_global_optimized_collector

            perf_collector = get_global_optimized_collector()
            perf_stats = perf_collector.get_performance_stats()

            perf_metrics = perf_stats.get("performance_metrics", {})

            optimized_metrics = {
                "optimized_spans_per_second": SystemMetric(
                    "optimized_spans_per_second", perf_metrics.get("spans_per_second", 0), "rate", timestamp
                ),
                "optimized_avg_processing_time_ms": SystemMetric(
                    "optimized_avg_processing_time_ms",
                    perf_metrics.get("avg_processing_time_ms", 0),
                    "ms",
                    timestamp,
                ),
                "optimized_memory_usage_mb": SystemMetric(
                    "optimized_memory_usage_mb", perf_metrics.get("memory_usage_mb", 0), "MB", timestamp
                ),
                "optimized_cpu_usage_percent": SystemMetric(
                    "optimized_cpu_usage_percent",
                    perf_metrics.get("cpu_usage_percent", 0),
                    "percent",
                    timestamp,
                ),
                "optimized_buffer_utilization": SystemMetric(
                    "optimized_buffer_utilization",
                    perf_metrics.get("buffer_utilization", 0),
                    "ratio",
                    timestamp,
                ),
                "optimized_compression_ratio": SystemMetric(
                    "optimized_compression_ratio",
                    perf_metrics.get("compression_ratio", 0),
                    "ratio",
                    timestamp,
                ),
            }

            with self._lock:
                self._current_metrics.update(optimized_metrics)
                for name, metric in optimized_metrics.items():
                    self._metrics_history[name].append(metric)

        except Exception as e:  # guardian: allow-broad-exception -- performance collector metrics are best-effort; import and attribute errors are expected
            Logger.debug(f"[OBSERVABILITY] Failed to collect optimized collector metrics: {e}")

    def _run_health_checks(self) -> None:
        """Run all health checks."""
        health_results = []

        for check_name, check_func in tqdm(self._health_checks.items(), desc="Processing", unit="item"):
            try:
                start_time = time.time()
                result = check_func()
                duration_ms = (time.time() - start_time) * 1000

                health_check = HealthCheck(
                    name=check_name,
                    status=result["status"],
                    message=result["message"],
                    timestamp=time.time(),
                    duration_ms=duration_ms,
                    metadata=result.get("metadata", {}),
                )

                health_results.append(health_check)

            except Exception as e:
                health_check = HealthCheck(
                    name=check_name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check failed: {e}",
                    timestamp=time.time(),
                    duration_ms=0,
                )
                health_results.append(health_check)

        # Calculate overall health
        overall_status = self._calculate_overall_health(health_results)
        health_score = self._calculate_health_score(health_results)

        with self._lock:
            system_health = SystemHealth(
                status=overall_status,
                score=health_score,
                checks=health_results,
                metrics=self._current_metrics.copy(),
                alerts=list(self._active_alerts.values()),
                timestamp=time.time(),
            )
            self._health_history.append(system_health)

    def _check_memory_usage(self) -> dict[str, Any]:
        """Check memory usage health."""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {usage_percent:.1f}%"
            elif usage_percent > 80:
                status = HealthStatus.WARNING
                message = f"High memory usage: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {usage_percent:.1f}%"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / 1024**3,
                    "used_gb": memory.used / 1024**3,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check memory: {e}",
            }

    def _check_cpu_usage(self) -> dict[str, Any]:
        """Check CPU usage health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.WARNING
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "usage_percent": cpu_percent,
                    "core_count": psutil.cpu_count(),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check CPU: {e}",
            }

    def _check_disk_usage(self) -> dict[str, Any]:
        """Check disk usage health."""
        try:
            disk = psutil.disk_usage("/")
            usage_percent = (disk.used / disk.total) * 100

            if usage_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {usage_percent:.1f}%"
            elif usage_percent > 85:
                status = HealthStatus.WARNING
                message = f"High disk usage: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {usage_percent:.1f}%"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "usage_percent": usage_percent,
                    "free_gb": disk.free / 1024**3,
                    "used_gb": disk.used / 1024**3,
                    "total_gb": disk.total / 1024**3,
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check disk: {e}",
            }

    def _check_tracing_system(self) -> dict[str, Any]:
        """Check tracing system health."""
        try:
            from agentic_core.mixins.auto_span_collector import get_global_collector

            collector = get_global_collector()
            stats = collector.get_collection_stats()

            collection_active = stats.get("collection_active", False)
            error_count = stats.get("collection_errors", 0)
            buffer_size = stats.get("buffer_size", 0)

            if not collection_active:
                status = HealthStatus.WARNING
                message = "Tracing collection not active"
            elif error_count > 10:
                status = HealthStatus.WARNING
                message = f"High error count: {error_count}"
            elif buffer_size > stats.get("buffer_capacity", 1000) * 0.9:
                status = HealthStatus.WARNING
                message = f"Buffer nearly full: {buffer_size}"
            else:
                status = HealthStatus.HEALTHY
                message = "Tracing system healthy"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "collection_active": collection_active,
                    "error_count": error_count,
                    "buffer_size": buffer_size,
                    "runtime_adg_enabled": stats.get("runtime_adg_enabled", False),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check tracing system: {e}",
            }

    def _check_runtime_adg(self) -> dict[str, Any]:
        """Check Runtime ADG health."""
        try:
            from system_learning.runtime_adg.auto_persistence import get_auto_persistence_tracer

            tracer = get_auto_persistence_tracer()
            status_info = tracer.get_auto_persistence_status()

            enabled = status_info.get("enabled", False)
            persistence_count = status_info.get("persistence_count", 0)

            if not enabled:
                status = HealthStatus.WARNING
                message = "Runtime ADG auto-persistence not enabled"
            else:
                status = HealthStatus.HEALTHY
                message = f"Runtime ADG healthy, {persistence_count} persistences"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "enabled": enabled,
                    "persistence_count": persistence_count,
                    "last_persistence": status_info.get("last_persistence"),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check Runtime ADG: {e}",
            }

    def _check_span_collection(self) -> dict[str, Any]:
        """Check span collection health."""
        try:
            from agentic_core.mixins.performance_optimized_collector import get_global_optimized_collector

            collector = get_global_optimized_collector()
            stats = collector.get_performance_stats()

            spans_per_second = stats.get("performance_metrics", {}).get("spans_per_second", 0)
            memory_usage = stats.get("performance_metrics", {}).get("memory_usage_mb", 0)

            if spans_per_second < 10 and spans_per_second > 0:
                status = HealthStatus.WARNING
                message = f"Low collection rate: {spans_per_second:.1f} spans/sec"
            elif memory_usage > 500:
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory_usage:.1f} MB"
            else:
                status = HealthStatus.HEALTHY
                message = f"Span collection healthy: {spans_per_second:.1f} spans/sec"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "spans_per_second": spans_per_second,
                    "memory_usage_mb": memory_usage,
                    "collection_active": stats.get("collection_active", False),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check span collection: {e}",
            }

    def _check_performance_metrics(self) -> dict[str, Any]:
        """Check performance metrics health."""
        try:
            # Check recent performance trends
            recent_health = list(self._health_history)[-5:] if self._health_history else []

            if len(recent_health) < 3:
                return {
                    "status": HealthStatus.UNKNOWN,
                    "message": "Insufficient performance data",
                }

            # Calculate performance trend
            scores = [h.score for h in recent_health]
            if len(scores) >= 3:
                recent_avg = sum(scores[-3:]) / 3
                older_avg = sum(scores[-6:-3]) / 3 if len(scores) >= 6 else scores[0]

                if recent_avg < older_avg - 10:
                    status = HealthStatus.WARNING
                    message = f"Performance degrading: {recent_avg:.1f} vs {older_avg:.1f}"
                elif recent_avg > older_avg + 10:
                    status = HealthStatus.HEALTHY
                    message = f"Performance improving: {recent_avg:.1f} vs {older_avg:.1f}"
                else:
                    status = HealthStatus.HEALTHY
                    message = f"Performance stable: {recent_avg:.1f}"
            else:
                status = HealthStatus.HEALTHY
                message = "Performance metrics healthy"

            return {
                "status": status,
                "message": message,
                "metadata": {
                    "recent_score": recent_avg if "recent_avg" in locals() else 0,
                    "trend_samples": len(scores),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": f"Failed to check performance metrics: {e}",
            }

    def _calculate_overall_health(self, health_results: list[HealthCheck]) -> HealthStatus:
        """Calculate overall system health status."""
        if not health_results:
            return HealthStatus.UNKNOWN

        status_counts = dict.fromkeys(HealthStatus, 0)

        for check in health_results:
            status_counts[check.status] += 1

        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            return HealthStatus.CRITICAL
        elif status_counts[HealthStatus.WARNING] > len(health_results) * 0.3:
            return HealthStatus.WARNING
        elif status_counts[HealthStatus.DEGRADED] > 0:
            return HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] == len(health_results):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.WARNING

    def _calculate_health_score(self, health_results: list[HealthCheck]) -> float:
        """Calculate overall health score (0-100)."""
        if not health_results:
            return 50.0

        score = 100.0

        for check in health_results:
            if check.status == HealthStatus.CRITICAL:
                score -= 30
            elif check.status == HealthStatus.WARNING:
                score -= 15
            elif check.status == HealthStatus.DEGRADED:
                score -= 10
            elif check.status == HealthStatus.UNKNOWN:
                score -= 5

        return max(0.0, min(100.0, score))

    def _check_alerts(self) -> None:
        """Check for alert conditions."""
        for metric_name, metric in self._current_metrics.items():
            if metric_name in self._alert_thresholds:
                threshold = self._alert_thresholds[metric_name]
                self._check_metric_alert(metric_name, metric, threshold)

    def _check_metric_alert(self, metric_name: str, metric: SystemMetric, threshold: dict[str, Any]) -> None:
        """Check if metric triggers alert."""
        alert_id = f"{metric_name}_alert"

        try:
            value = metric.value
            warning_threshold = threshold.get("warning")
            critical_threshold = threshold.get("critical")

            # Check for critical alert
            if critical_threshold and value >= critical_threshold:
                if (
                    alert_id not in self._active_alerts
                    or self._active_alerts[alert_id].severity != AlertSeverity.CRITICAL
                ):
                    alert = Alert(
                        id=alert_id,
                        name=f"Critical {metric_name}",
                        description=f"{metric_name} is critical: {value}{threshold.get('unit', '')}",
                        severity=AlertSeverity.CRITICAL,
                        status="active",
                        timestamp=time.time(),
                        metadata={
                            "metric_name": metric_name,
                            "value": value,
                            "threshold": critical_threshold,
                            "unit": threshold.get("unit", ""),
                        },
                    )
                    self._active_alerts[alert_id] = alert
                    self._alert_history.append(alert)
                    Logger.warning(f"[OBSERVABILITY] CRITICAL ALERT: {alert.description}")

            # Check for warning alert (only if not critical)
            elif warning_threshold and value >= warning_threshold:
                if alert_id not in self._active_alerts:
                    alert = Alert(
                        id=alert_id,
                        name=f"Warning {metric_name}",
                        description=f"{metric_name} is high: {value}{threshold.get('unit', '')}",
                        severity=AlertSeverity.HIGH,
                        status="active",
                        timestamp=time.time(),
                        metadata={
                            "metric_name": metric_name,
                            "value": value,
                            "threshold": warning_threshold,
                            "unit": threshold.get("unit", ""),
                        },
                    )
                    self._active_alerts[alert_id] = alert
                    self._alert_history.append(alert)
                    Logger.warning(f"[OBSERVABILITY] WARNING ALERT: {alert.description}")

            # Resolve alert if value is back to normal
            else:
                if alert_id in self._active_alerts:
                    alert = self._active_alerts[alert_id]
                    alert.status = "resolved"
                    alert.resolved_timestamp = time.time()
                    del self._active_alerts[alert_id]
                    Logger.info(f"[OBSERVABILITY] RESOLVED ALERT: {alert.name}")

        except Exception as e:
            Logger.error(f"[OBSERVABILITY] Failed to check alert for {metric_name}: {e}")

    def _update_performance_trends(self) -> None:
        """Update performance trend data."""
        with self._lock:
            for metric_name, metric in self._current_metrics.items():
                self._performance_trends[metric_name].append(metric.value)
                if len(self._performance_trends[metric_name]) > 100:
                    self._performance_trends[metric_name] = self._performance_trends[metric_name][-100:]

    def _cleanup_old_data(self) -> None:
        """Clean up old monitoring data."""
        # Clean up old metrics (handled by deque maxlen)
        # Clean up old alerts (handled by deque maxlen)
        # Clean up old health data (handled by deque maxlen)
        pass

    def get_system_health(self) -> SystemHealth | None:
        """Get current system health."""
        with self._lock:
            if self._health_history:
                return self._health_history[-1]
            return None

    def get_active_alerts(self) -> list[Alert]:
        """Get active alerts."""
        with self._lock:
            return list(self._active_alerts.values())

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """Get alert history."""
        with self._lock:
            return list(self._alert_history)[-limit:]

    def get_metrics_history(self, metric_name: str, limit: int = 100) -> list[SystemMetric]:
        """Get metrics history for a specific metric."""
        with self._lock:
            if metric_name in self._metrics_history:
                return list(self._metrics_history[metric_name])[-limit:]
            return []

    def get_performance_trends(self) -> dict[str, dict[str, Any]]:
        """Get performance trend analysis."""
        trends = {}

        for metric_name, values in tqdm(self._performance_trends.items(), desc="Processing", unit="item"):
            if len(values) >= 2:
                # Calculate trend
                recent_avg = sum(values[-10:]) / min(10, len(values))
                older_avg = (
                    sum(values[-20:-10]) / min(10, len(values) - 10) if len(values) > 10 else values[0]
                )

                trend = "stable"
                if recent_avg > older_avg * 1.1:
                    trend = "increasing"
                elif recent_avg < older_avg * 0.9:
                    trend = "decreasing"

                trends[metric_name] = {
                    "current_value": values[-1],
                    "recent_average": recent_avg,
                    "trend": trend,
                    "sample_count": len(values),
                }

        return trends

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get comprehensive dashboard data."""
        current_health = self.get_system_health()

        return {
            "system_health": {
                "status": current_health.status.value if current_health else HealthStatus.UNKNOWN.value,
                "score": current_health.score if current_health else 0,
                "timestamp": current_health.timestamp if current_health else time.time(),
            },
            "active_alerts": [
                {
                    "id": alert.id,
                    "name": alert.name,
                    "description": alert.description,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp,
                }
                for alert in self.get_active_alerts()
            ],
            "current_metrics": {
                name: {
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp,
                }
                for name, metric in self._current_metrics.items()
            },
            "performance_trends": self.get_performance_trends(),
            "health_checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "duration_ms": check.duration_ms,
                }
                for check in (current_health.checks if current_health else [])
            ],
            "monitoring_active": self._monitoring_active,
        }


# Global observability instance
_global_observability: EnhancedObservability | None = None


def get_global_observability() -> EnhancedObservability:
    """Get the global enhanced observability instance."""
    global _global_observability
    if _global_observability is None:
        _global_observability = EnhancedObservability()
    return _global_observability


def start_enhanced_monitoring() -> None:
    """Start global enhanced monitoring."""
    observability = get_global_observability()
    observability.start_monitoring()


def stop_enhanced_monitoring() -> None:
    """Stop global enhanced monitoring."""
    observability = get_global_observability()
    observability.stop_monitoring()


def get_system_health() -> SystemHealth | None:
    """Get current system health."""
    observability = get_global_observability()
    return observability.get_system_health()


def get_active_alerts() -> list[Alert]:
    """Get active alerts."""
    observability = get_global_observability()
    return observability.get_active_alerts()


def get_dashboard_data() -> dict[str, Any]:
    """Get comprehensive dashboard data."""
    observability = get_global_observability()
    return observability.get_dashboard_data()
