"""
RecursionMonitor - Production-Grade Monitoring for Forward-Rolling Recursion.

[PHASE 3] Implements comprehensive monitoring, alerting, and health checks
for Forward-Rolling Recursion pipelines in production environments.

OBSERVABILITY: Real-time metrics, alerting, and health status
RELIABILITY: Circuit breakers, degradation detection, auto-recovery

Author: Cascade
Date: February 2026
Phase: 3 - Production Readiness
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

Logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels for the recursion system."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data structure."""

    severity: AlertSeverity
    message: str
    timestamp: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class HealthCheck:
    """Health check result."""

    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecursionSnapshot:
    """Point-in-time snapshot of recursion state."""

    timestamp: str
    active_recursions: int
    total_spawns: int
    success_rate: float
    avg_depth: float
    memory_usage_bytes: int
    cache_hit_rate: float
    health_status: HealthStatus


class RecursionMonitor:
    """
    Production-grade monitoring for Forward-Rolling Recursion.

    Features:
    - Real-time metrics collection
    - Health checks with configurable thresholds
    - Alert generation and management
    - Circuit breaker integration
    - Performance degradation detection
    """

    def __init__(
        self,
        alert_callback: Callable[[Alert], None] | None = None,
        health_check_interval_sec: int = 30,
        metrics_retention_hours: int = 24,
    ):
        """
        Initialize recursion monitor.

        Args:
            alert_callback: Optional callback for alert notifications
            health_check_interval_sec: Interval between health checks
            metrics_retention_hours: Hours to retain metric history
        """
        self.alert_callback = alert_callback
        self.health_check_interval_sec = health_check_interval_sec
        self.metrics_retention_hours = metrics_retention_hours

        # Metrics storage
        self._metrics_history: list[RecursionSnapshot] = []
        self._alerts: list[Alert] = []
        self._health_checks: list[HealthCheck] = []

        # Thresholds
        self._thresholds = {
            "max_active_recursions": 100,
            "min_success_rate": 0.8,
            "max_avg_depth": 40,
            "max_memory_mb": 500,
            "min_cache_hit_rate": 0.5,
        }

        # Circuit breaker state
        self._circuit_open = False
        self._circuit_open_until: datetime | None = None
        self._consecutive_failures = 0
        self._failure_threshold = 5

        # Performance baseline
        self._baseline_response_time_ms: float | None = None
        self._response_times: list[float] = []

        Logger.info("[RecursionMonitor] Initialized with production settings")

    def record_spawn(
        self,
        success: bool,
        depth: int,
        duration_ms: float,
        memory_bytes: int,
        cache_hit: bool,
    ) -> None:
        """
        Record a spawn operation for monitoring.

        Args:
            success: Whether spawn was successful
            depth: Recursion depth at spawn
            duration_ms: Duration of spawn operation
            memory_bytes: Memory used by spawn
            cache_hit: Whether validation cache was hit
        """
        self._response_times.append(duration_ms)

        # Keep only recent response times
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-500:]

        # Update circuit breaker
        if not success:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._failure_threshold:
                self._open_circuit()
        else:
            self._consecutive_failures = 0

        # Check for performance degradation
        self._check_performance_degradation(duration_ms)

        # Check depth warning
        if depth > self._thresholds["max_avg_depth"]:
            self._create_alert(
                AlertSeverity.WARNING,
                f"High recursion depth detected: {depth}",
                "depth_monitor",
                {"depth": depth, "threshold": self._thresholds["max_avg_depth"]},
            )

    def record_snapshot(
        self,
        active_recursions: int,
        total_spawns: int,
        successful_spawns: int,
        depths: list[int],
        memory_bytes: int,
        cache_hits: int,
        cache_misses: int,
    ) -> RecursionSnapshot:
        """
        Record a point-in-time snapshot of recursion state.

        Args:
            active_recursions: Number of active recursive operations
            total_spawns: Total spawn operations
            successful_spawns: Number of successful spawns
            depths: List of current depths
            memory_bytes: Total memory usage
            cache_hits: Number of cache hits
            cache_misses: Number of cache misses

        Returns:
            RecursionSnapshot with current state
        """
        success_rate = successful_spawns / max(total_spawns, 1)
        avg_depth = sum(depths) / max(len(depths), 1) if depths else 0
        cache_hit_rate = cache_hits / max(cache_hits + cache_misses, 1)

        health_status = self._calculate_health_status(
            active_recursions, success_rate, avg_depth, memory_bytes, cache_hit_rate
        )

        snapshot = RecursionSnapshot(
            timestamp=datetime.now().isoformat(),
            active_recursions=active_recursions,
            total_spawns=total_spawns,
            success_rate=success_rate,
            avg_depth=avg_depth,
            memory_usage_bytes=memory_bytes,
            cache_hit_rate=cache_hit_rate,
            health_status=health_status,
        )

        self._metrics_history.append(snapshot)
        self._cleanup_old_metrics()

        return snapshot

    def _calculate_health_status(
        self,
        active_recursions: int,
        success_rate: float,
        avg_depth: float,
        memory_bytes: int,
        cache_hit_rate: float,
    ) -> HealthStatus:
        """Calculate overall health status based on metrics."""
        issues = 0

        if active_recursions > self._thresholds["max_active_recursions"]:
            issues += 2
        if success_rate < self._thresholds["min_success_rate"]:
            issues += 2
        if avg_depth > self._thresholds["max_avg_depth"]:
            issues += 1
        if memory_bytes > self._thresholds["max_memory_mb"] * 1024 * 1024:
            issues += 2
        if cache_hit_rate < self._thresholds["min_cache_hit_rate"]:
            issues += 1

        if self._circuit_open:
            return HealthStatus.CRITICAL
        elif issues >= 4:
            return HealthStatus.UNHEALTHY
        elif issues >= 2:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def run_health_checks(self) -> list[HealthCheck]:
        """
        Run all health checks and return results.

        Returns:
            List of HealthCheck results
        """
        checks = []

        # Check 1: Circuit breaker status
        start = time.time()
        circuit_status = HealthStatus.CRITICAL if self._circuit_open else HealthStatus.HEALTHY
        checks.append(
            HealthCheck(
                name="circuit_breaker",
                status=circuit_status,
                message="Circuit is open" if self._circuit_open else "Circuit is closed",
                duration_ms=(time.time() - start) * 1000,
                timestamp=datetime.now().isoformat(),
                metadata={"consecutive_failures": self._consecutive_failures},
            )
        )

        # Check 2: Memory usage
        start = time.time()
        if self._metrics_history:
            latest = self._metrics_history[-1]
            mem_mb = latest.memory_usage_bytes / (1024 * 1024)
            mem_status = (
                HealthStatus.HEALTHY
                if mem_mb < self._thresholds["max_memory_mb"]
                else HealthStatus.DEGRADED
            )
            checks.append(
                HealthCheck(
                    name="memory_usage",
                    status=mem_status,
                    message=f"Memory usage: {mem_mb:.1f}MB",
                    duration_ms=(time.time() - start) * 1000,
                    timestamp=datetime.now().isoformat(),
                    metadata={"memory_mb": mem_mb},
                )
            )

        # Check 3: Success rate
        start = time.time()
        if self._metrics_history:
            latest = self._metrics_history[-1]
            success_status = (
                HealthStatus.HEALTHY
                if latest.success_rate >= self._thresholds["min_success_rate"]
                else HealthStatus.DEGRADED
            )
            checks.append(
                HealthCheck(
                    name="success_rate",
                    status=success_status,
                    message=f"Success rate: {latest.success_rate:.1%}",
                    duration_ms=(time.time() - start) * 1000,
                    timestamp=datetime.now().isoformat(),
                    metadata={"success_rate": latest.success_rate},
                )
            )

        # Check 4: Response time
        start = time.time()
        if self._response_times:
            avg_response = sum(self._response_times) / len(self._response_times)
            response_status = HealthStatus.HEALTHY if avg_response < 1000 else HealthStatus.DEGRADED
            checks.append(
                HealthCheck(
                    name="response_time",
                    status=response_status,
                    message=f"Avg response time: {avg_response:.1f}ms",
                    duration_ms=(time.time() - start) * 1000,
                    timestamp=datetime.now().isoformat(),
                    metadata={"avg_response_ms": avg_response},
                )
            )

        self._health_checks = checks
        return checks

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health status."""
        if self._circuit_open:
            return HealthStatus.CRITICAL

        checks = self.run_health_checks()
        if not checks:
            return HealthStatus.HEALTHY

        # Aggregate health from all checks
        statuses = [c.status for c in checks]
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def _open_circuit(self) -> None:
        """Open the circuit breaker."""
        self._circuit_open = True
        self._circuit_open_until = datetime.now() + timedelta(seconds=60)

        self._create_alert(
            AlertSeverity.CRITICAL,
            "Circuit breaker opened due to consecutive failures",
            "circuit_breaker",
            {"consecutive_failures": self._consecutive_failures},
        )

        Logger.critical("[CIRCUIT_BREAKER] Circuit opened due to failures")

    def close_circuit(self) -> None:
        """Manually close the circuit breaker."""
        self._circuit_open = False
        self._circuit_open_until = None
        self._consecutive_failures = 0

        Logger.info("[CIRCUIT_BREAKER] Circuit manually closed")

    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self._circuit_open and self._circuit_open_until:
            if datetime.now() > self._circuit_open_until:
                # Auto-close after timeout
                self._circuit_open = False
                self._circuit_open_until = None
                Logger.info("[CIRCUIT_BREAKER] Circuit auto-closed after timeout")
                return False
        return self._circuit_open

    def _check_performance_degradation(self, duration_ms: float) -> None:
        """Check for performance degradation."""
        if self._baseline_response_time_ms is None:
            if len(self._response_times) >= 100:
                self._baseline_response_time_ms = sum(self._response_times[:100]) / 100
            return

        # Alert if response time is 3x baseline
        if duration_ms > self._baseline_response_time_ms * 3:
            self._create_alert(
                AlertSeverity.WARNING,
                f"Performance degradation: {duration_ms:.1f}ms "
                f"(baseline: {self._baseline_response_time_ms:.1f}ms)",
                "performance_monitor",
                {
                    "current_ms": duration_ms,
                    "baseline_ms": self._baseline_response_time_ms,
                },
            )

    def _create_alert(
        self,
        severity: AlertSeverity,
        message: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> Alert:
        """Create and store an alert."""
        alert = Alert(
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat(),
            source=source,
            metadata=metadata or {},
        )

        self._alerts.append(alert)

        # Invoke callback if configured
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                Logger.error(f"Alert callback failed: {e}")

        Logger.log(
            logging.CRITICAL if severity == AlertSeverity.CRITICAL else logging.WARNING,
            f"[ALERT] [{severity.value.upper()}] {message}",
        )

        return alert

    def get_alerts(
        self,
        severity: AlertSeverity | None = None,
        unacknowledged_only: bool = False,
    ) -> list[Alert]:
        """Get alerts with optional filtering."""
        alerts = self._alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if unacknowledged_only:
            alerts = [a for a in alerts if not a.acknowledged]

        return alerts

    def acknowledge_alert(self, index: int) -> bool:
        """Acknowledge an alert by index."""
        if 0 <= index < len(self._alerts):
            self._alerts[index].acknowledged = True
            return True
        return False

    def clear_alerts(self) -> int:
        """Clear all alerts and return count cleared."""
        count = len(self._alerts)
        self._alerts.clear()
        return count

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(hours=self.metrics_retention_hours)
        cutoff_str = cutoff.isoformat()

        self._metrics_history = [m for m in self._metrics_history if m.timestamp > cutoff_str]

    def set_threshold(self, name: str, value: float) -> bool:
        """Set a monitoring threshold."""
        if name in self._thresholds:
            self._thresholds[name] = value
            Logger.info(f"[Monitor] Threshold {name} set to {value}")
            return True
        return False

    def get_thresholds(self) -> dict[str, float]:
        """Get current monitoring thresholds."""
        return self._thresholds.copy()

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self._metrics_history:
            return {
                "total_snapshots": 0,
                "health_status": HealthStatus.HEALTHY.value,
            }

        latest = self._metrics_history[-1]

        # Calculate trends
        if len(self._metrics_history) >= 2:
            prev = self._metrics_history[-2]
            success_trend = latest.success_rate - prev.success_rate
            depth_trend = latest.avg_depth - prev.avg_depth
        else:
            success_trend = 0.0
            depth_trend = 0.0

        return {
            "total_snapshots": len(self._metrics_history),
            "latest_snapshot": {
                "timestamp": latest.timestamp,
                "active_recursions": latest.active_recursions,
                "total_spawns": latest.total_spawns,
                "success_rate": latest.success_rate,
                "avg_depth": latest.avg_depth,
                "memory_mb": latest.memory_usage_bytes / (1024 * 1024),
                "cache_hit_rate": latest.cache_hit_rate,
            },
            "trends": {
                "success_rate_change": success_trend,
                "depth_change": depth_trend,
            },
            "health_status": latest.health_status.value,
            "circuit_open": self._circuit_open,
            "alert_count": len(self._alerts),
            "unacknowledged_alerts": len([a for a in self._alerts if not a.acknowledged]),
        }

    def reset(self) -> None:
        """Reset all monitoring state."""
        self._metrics_history.clear()
        self._alerts.clear()
        self._health_checks.clear()
        self._circuit_open = False
        self._circuit_open_until = None
        self._consecutive_failures = 0
        self._response_times.clear()
        self._baseline_response_time_ms = None

        Logger.info("[RecursionMonitor] Reset complete")


__all__ = [
    "RecursionMonitor",
    "HealthStatus",
    "AlertSeverity",
    "Alert",
    "HealthCheck",
    "RecursionSnapshot",
]
