"""
Phase 3 Production Readiness Test Suite.

Tests for monitoring, alerting, health checks, and circuit breakers.

Author: Cascade
Date: February 2026
Phase: 3 - Production Readiness Testing
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from agentic_core.L3_orchestration.workflow_engines.RecursionMonitor import (
    Alert,
    AlertSeverity,
    HealthCheck,
    HealthStatus,
    RecursionMonitor,
    RecursionSnapshot,
)


class TestRecursionMonitorInitialization:
    """Test RecursionMonitor initialization."""

    def test_default_initialization(self):
        """Test monitor initializes with defaults."""
        monitor = RecursionMonitor()

        assert monitor.health_check_interval_sec == 30
        assert monitor.metrics_retention_hours == 24
        assert monitor.alert_callback is None
        assert not monitor._circuit_open

    def test_custom_initialization(self):
        """Test monitor initializes with custom values."""
        callback = MagicMock()
        monitor = RecursionMonitor(
            alert_callback=callback,
            health_check_interval_sec=60,
            metrics_retention_hours=48,
        )

        assert monitor.health_check_interval_sec == 60
        assert monitor.metrics_retention_hours == 48
        assert monitor.alert_callback == callback


class TestSpawnRecording:
    """Test spawn operation recording."""

    @pytest.fixture
    def monitor(self):
        """Create test monitor."""
        return RecursionMonitor()

    def test_record_successful_spawn(self, monitor):
        """Test recording a successful spawn."""
        monitor.record_spawn(
            success=True,
            depth=10,
            duration_ms=50.0,
            memory_bytes=1024,
            cache_hit=True,
        )

        assert len(monitor._response_times) == 1
        assert monitor._consecutive_failures == 0

    def test_record_failed_spawn(self, monitor):
        """Test recording a failed spawn."""
        monitor.record_spawn(
            success=False,
            depth=10,
            duration_ms=100.0,
            memory_bytes=1024,
            cache_hit=False,
        )

        assert monitor._consecutive_failures == 1

    def test_high_depth_creates_alert(self, monitor):
        """Test that high depth creates warning alert."""
        monitor.record_spawn(
            success=True,
            depth=45,  # Above threshold of 40
            duration_ms=50.0,
            memory_bytes=1024,
            cache_hit=True,
        )

        alerts = monitor.get_alerts(severity=AlertSeverity.WARNING)
        assert len(alerts) >= 1
        assert any("depth" in a.message.lower() for a in alerts)


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    @pytest.fixture
    def monitor(self):
        """Create test monitor."""
        return RecursionMonitor()

    def test_circuit_opens_after_failures(self, monitor):
        """Test circuit opens after consecutive failures."""
        # Trigger failures up to threshold
        for _ in range(monitor._failure_threshold):
            monitor.record_spawn(
                success=False,
                depth=10,
                duration_ms=50.0,
                memory_bytes=1024,
                cache_hit=False,
            )

        assert monitor.is_circuit_open()

    def test_circuit_resets_on_success(self, monitor):
        """Test consecutive failure count resets on success."""
        monitor._consecutive_failures = 4

        monitor.record_spawn(
            success=True,
            depth=10,
            duration_ms=50.0,
            memory_bytes=1024,
            cache_hit=True,
        )

        assert monitor._consecutive_failures == 0

    def test_manual_circuit_close(self, monitor):
        """Test manual circuit closing."""
        monitor._circuit_open = True
        monitor._circuit_open_until = datetime.now() + timedelta(hours=1)

        monitor.close_circuit()

        assert not monitor.is_circuit_open()
        assert monitor._consecutive_failures == 0

    def test_circuit_auto_closes(self, monitor):
        """Test circuit auto-closes after timeout."""
        monitor._circuit_open = True
        monitor._circuit_open_until = datetime.now() - timedelta(seconds=1)

        assert not monitor.is_circuit_open()


class TestSnapshotRecording:
    """Test metrics snapshot recording."""

    @pytest.fixture
    def monitor(self):
        """Create test monitor."""
        return RecursionMonitor()

    def test_record_snapshot(self, monitor):
        """Test recording a metrics snapshot."""
        snapshot = monitor.record_snapshot(
            active_recursions=5,
            total_spawns=100,
            successful_spawns=95,
            depths=[10, 15, 20],
            memory_bytes=1024 * 1024,
            cache_hits=80,
            cache_misses=20,
        )

        assert isinstance(snapshot, RecursionSnapshot)
        assert snapshot.active_recursions == 5
        assert snapshot.total_spawns == 100
        assert snapshot.success_rate == 0.95
        assert snapshot.avg_depth == 15.0
        assert snapshot.cache_hit_rate == 0.8

    def test_snapshot_health_status(self, monitor):
        """Test snapshot health status calculation."""
        # Healthy metrics
        snapshot = monitor.record_snapshot(
            active_recursions=10,
            total_spawns=100,
            successful_spawns=95,
            depths=[10, 15, 20],
            memory_bytes=100 * 1024 * 1024,  # 100MB
            cache_hits=80,
            cache_misses=20,
        )

        assert snapshot.health_status == HealthStatus.HEALTHY

    def test_unhealthy_snapshot(self, monitor):
        """Test unhealthy metrics produce correct status."""
        # Unhealthy metrics
        snapshot = monitor.record_snapshot(
            active_recursions=150,  # Above threshold
            total_spawns=100,
            successful_spawns=50,  # 50% success rate
            depths=[10, 15, 20],
            memory_bytes=600 * 1024 * 1024,  # 600MB
            cache_hits=20,
            cache_misses=80,
        )

        assert snapshot.health_status in [
            HealthStatus.DEGRADED,
            HealthStatus.UNHEALTHY,
        ]


class TestHealthChecks:
    """Test health check functionality."""

    @pytest.fixture
    def monitor(self):
        """Create test monitor with some data."""
        mon = RecursionMonitor()
        mon.record_snapshot(
            active_recursions=10,
            total_spawns=100,
            successful_spawns=90,
            depths=[10, 15, 20],
            memory_bytes=100 * 1024 * 1024,
            cache_hits=80,
            cache_misses=20,
        )
        return mon

    def test_run_health_checks(self, monitor):
        """Test running all health checks."""
        checks = monitor.run_health_checks()

        assert len(checks) >= 1
        assert all(isinstance(c, HealthCheck) for c in checks)

    def test_health_check_structure(self, monitor):
        """Test health check result structure."""
        checks = monitor.run_health_checks()

        for check in checks:
            assert hasattr(check, "name")
            assert hasattr(check, "status")
            assert hasattr(check, "message")
            assert hasattr(check, "duration_ms")
            assert hasattr(check, "timestamp")

    def test_overall_health(self, monitor):
        """Test overall health calculation."""
        health = monitor.get_overall_health()

        assert isinstance(health, HealthStatus)

    def test_critical_health_when_circuit_open(self, monitor):
        """Test critical health when circuit is open."""
        monitor._circuit_open = True

        health = monitor.get_overall_health()

        assert health == HealthStatus.CRITICAL


class TestAlertManagement:
    """Test alert creation and management."""

    @pytest.fixture
    def monitor(self):
        """Create test monitor."""
        return RecursionMonitor()

    def test_alert_creation(self, monitor):
        """Test alert is created correctly."""
        monitor._create_alert(
            AlertSeverity.WARNING,
            "Test alert",
            "test_source",
            {"key": "value"},
        )

        alerts = monitor.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].message == "Test alert"
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_alert_callback(self):
        """Test alert callback is invoked."""
        callback = MagicMock()
        monitor = RecursionMonitor(alert_callback=callback)

        monitor._create_alert(
            AlertSeverity.ERROR,
            "Callback test",
            "test_source",
        )

        callback.assert_called_once()

    def test_filter_alerts_by_severity(self, monitor):
        """Test filtering alerts by severity."""
        monitor._create_alert(AlertSeverity.INFO, "Info alert", "test")
        monitor._create_alert(AlertSeverity.WARNING, "Warning alert", "test")
        monitor._create_alert(AlertSeverity.ERROR, "Error alert", "test")

        warnings = monitor.get_alerts(severity=AlertSeverity.WARNING)

        assert len(warnings) == 1
        assert warnings[0].severity == AlertSeverity.WARNING

    def test_filter_unacknowledged_alerts(self, monitor):
        """Test filtering unacknowledged alerts."""
        monitor._create_alert(AlertSeverity.INFO, "Alert 1", "test")
        monitor._create_alert(AlertSeverity.INFO, "Alert 2", "test")
        monitor._alerts[0].acknowledged = True

        unack = monitor.get_alerts(unacknowledged_only=True)

        assert len(unack) == 1
        assert unack[0].message == "Alert 2"

    def test_acknowledge_alert(self, monitor):
        """Test acknowledging an alert."""
        monitor._create_alert(AlertSeverity.INFO, "Test", "test")

        result = monitor.acknowledge_alert(0)

        assert result is True
        assert monitor._alerts[0].acknowledged is True

    def test_clear_alerts(self, monitor):
        """Test clearing all alerts."""
        monitor._create_alert(AlertSeverity.INFO, "Test 1", "test")
        monitor._create_alert(AlertSeverity.INFO, "Test 2", "test")

        count = monitor.clear_alerts()

        assert count == 2
        assert len(monitor._alerts) == 0


class TestPerformanceMonitoring:
    """Test performance degradation detection."""

    @pytest.fixture
    def monitor(self):
        """Create monitor with baseline established."""
        mon = RecursionMonitor()
        # Establish baseline with fast response times
        for _ in range(100):
            mon._response_times.append(50.0)
        mon._baseline_response_time_ms = 50.0
        return mon

    def test_performance_degradation_alert(self, monitor):
        """Test alert on significant performance degradation."""
        # Record a slow operation (3x+ baseline)
        monitor.record_spawn(
            success=True,
            depth=10,
            duration_ms=200.0,  # 4x baseline of 50ms
            memory_bytes=1024,
            cache_hit=True,
        )

        alerts = monitor.get_alerts(severity=AlertSeverity.WARNING)
        degradation_alerts = [a for a in alerts if "degradation" in a.message.lower()]

        assert len(degradation_alerts) >= 1


class TestThresholdManagement:
    """Test threshold configuration."""

    @pytest.fixture
    def monitor(self):
        """Create test monitor."""
        return RecursionMonitor()

    def test_get_thresholds(self, monitor):
        """Test getting current thresholds."""
        thresholds = monitor.get_thresholds()

        assert "max_active_recursions" in thresholds
        assert "min_success_rate" in thresholds
        assert "max_avg_depth" in thresholds

    def test_set_threshold(self, monitor):
        """Test setting a threshold."""
        result = monitor.set_threshold("max_active_recursions", 200)

        assert result is True
        assert monitor._thresholds["max_active_recursions"] == 200

    def test_set_invalid_threshold(self, monitor):
        """Test setting an invalid threshold."""
        result = monitor.set_threshold("nonexistent_threshold", 100)

        assert result is False


class TestMetricsSummary:
    """Test metrics summary generation."""

    @pytest.fixture
    def monitor(self):
        """Create monitor with data."""
        mon = RecursionMonitor()
        mon.record_snapshot(
            active_recursions=10,
            total_spawns=100,
            successful_spawns=90,
            depths=[10, 15, 20],
            memory_bytes=100 * 1024 * 1024,
            cache_hits=80,
            cache_misses=20,
        )
        return mon

    def test_metrics_summary_structure(self, monitor):
        """Test metrics summary has expected structure."""
        summary = monitor.get_metrics_summary()

        assert "total_snapshots" in summary
        assert "latest_snapshot" in summary
        assert "health_status" in summary
        assert "circuit_open" in summary
        assert "alert_count" in summary

    def test_empty_metrics_summary(self):
        """Test summary with no data."""
        monitor = RecursionMonitor()
        summary = monitor.get_metrics_summary()

        assert summary["total_snapshots"] == 0
        assert summary["health_status"] == HealthStatus.HEALTHY.value


class TestMonitorReset:
    """Test monitor reset functionality."""

    def test_reset_clears_all_state(self):
        """Test reset clears all monitoring state."""
        monitor = RecursionMonitor()

        # Add some state
        monitor.record_snapshot(
            active_recursions=10,
            total_spawns=100,
            successful_spawns=90,
            depths=[10],
            memory_bytes=1024,
            cache_hits=80,
            cache_misses=20,
        )
        monitor._create_alert(AlertSeverity.INFO, "Test", "test")
        monitor._circuit_open = True

        monitor.reset()

        assert len(monitor._metrics_history) == 0
        assert len(monitor._alerts) == 0
        assert not monitor._circuit_open
        assert len(monitor._response_times) == 0


class TestDataStructures:
    """Test data structure definitions."""

    def test_alert_structure(self):
        """Test Alert dataclass."""
        alert = Alert(
            severity=AlertSeverity.WARNING,
            message="Test message",
            timestamp="2026-02-01T00:00:00",
            source="test",
        )

        assert alert.severity == AlertSeverity.WARNING
        assert alert.acknowledged is False

    def test_health_check_structure(self):
        """Test HealthCheck dataclass."""
        check = HealthCheck(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All good",
            duration_ms=1.5,
            timestamp="2026-02-01T00:00:00",
        )

        assert check.name == "test_check"
        assert check.status == HealthStatus.HEALTHY

    def test_recursion_snapshot_structure(self):
        """Test RecursionSnapshot dataclass."""
        snapshot = RecursionSnapshot(
            timestamp="2026-02-01T00:00:00",
            active_recursions=5,
            total_spawns=100,
            success_rate=0.95,
            avg_depth=15.0,
            memory_usage_bytes=1024,
            cache_hit_rate=0.8,
            health_status=HealthStatus.HEALTHY,
        )

        assert snapshot.active_recursions == 5
        assert snapshot.health_status == HealthStatus.HEALTHY


class TestHealthStatusEnum:
    """Test HealthStatus enumeration."""

    def test_health_status_values(self):
        """Test all health status values exist."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.CRITICAL.value == "critical"


class TestAlertSeverityEnum:
    """Test AlertSeverity enumeration."""

    def test_alert_severity_values(self):
        """Test all alert severity values exist."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
