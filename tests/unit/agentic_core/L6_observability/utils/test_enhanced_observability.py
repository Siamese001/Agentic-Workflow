"""Tests for Enhanced Observability System."""

import pytest

from agentic_core.L6_observability.utils.enhanced_observability import (
    Alert,
    AlertSeverity,
    EnhancedObservability,
    HealthCheck,
    HealthStatus,
    SystemHealth,
    SystemMetric,
)


class TestSystemMetric:
    """Test SystemMetric dataclass."""

    def test_system_metric_creation(self) -> None:
        """Test creating a system metric."""
        metric = SystemMetric(
            name="test_metric",
            value=42.0,
            unit="count",
            timestamp=1234567890.0,
            tags={"source": "test"},
        )
        assert metric.name == "test_metric"
        assert metric.value == 42.0
        assert metric.unit == "count"
        assert metric.timestamp == 1234567890.0
        assert metric.tags == {"source": "test"}


class TestAlert:
    """Test Alert dataclass."""

    def test_alert_creation(self) -> None:
        """Test creating an alert."""
        alert = Alert(
            id="test_alert_1",
            name="Test Alert",
            description="This is a test alert",
            severity=AlertSeverity.HIGH,
            status="active",
            timestamp=1234567890.0,
        )
        assert alert.id == "test_alert_1"
        assert alert.name == "Test Alert"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.status == "active"
        assert alert.resolved_timestamp is None


class TestHealthCheck:
    """Test HealthCheck dataclass."""

    def test_health_check_creation(self) -> None:
        """Test creating a health check."""
        check = HealthCheck(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All systems operational",
            timestamp=1234567890.0,
            duration_ms=10.5,
        )
        assert check.name == "test_check"
        assert check.status == HealthStatus.HEALTHY
        assert check.message == "All systems operational"
        assert check.duration_ms == 10.5


class TestEnhancedObservability:
    """Test EnhancedObservability system."""

    def test_observability_initialization(self) -> None:
        """Test initializing the observability system."""
        obs = EnhancedObservability()
        assert obs._monitoring_active is False
        assert obs._shutdown_requested is False
        assert len(obs._current_metrics) == 0

    def test_get_system_health_before_monitoring(self) -> None:
        """Test getting system health before monitoring starts."""
        obs = EnhancedObservability()
        health = obs.get_system_health()
        assert health is None

    def test_get_active_alerts_before_monitoring(self) -> None:
        """Test getting active alerts before monitoring starts."""
        obs = EnhancedObservability()
        alerts = obs.get_active_alerts()
        assert alerts == []

    def test_get_alert_history_before_monitoring(self) -> None:
        """Test getting alert history before monitoring starts."""
        obs = EnhancedObservability()
        history = obs.get_alert_history(limit=10)
        assert history == []

    def test_get_metrics_history_before_monitoring(self) -> None:
        """Test getting metrics history before monitoring starts."""
        obs = EnhancedObservability()
        history = obs.get_metrics_history("test_metric", limit=10)
        assert history == []

    def test_get_performance_trends_before_monitoring(self) -> None:
        """Test getting performance trends before monitoring starts."""
        obs = EnhancedObservability()
        trends = obs.get_performance_trends()
        assert trends == {}
