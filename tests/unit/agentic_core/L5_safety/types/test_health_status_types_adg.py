"""ADG contract tests for L5_safety/types/health_status_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.health_status_types import HealthStatus, AlertSeverity, health_metrics

class TestHealthStatus:
    def test_is_enum(self):
        import enum; assert issubclass(HealthStatus, enum.Enum)
    def test_has_healthy(self): assert HealthStatus.HEALTHY.value == "healthy"
    def test_has_critical(self): assert HealthStatus.CRITICAL.value == "critical"

class TestAlertSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(AlertSeverity, enum.Enum)
    def test_has_warning(self): assert AlertSeverity.WARNING.value == "warning"

class TestHealthMetrics:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(health_metrics)
    def test_creates(self):
        m = health_metrics(agent_id="a1", success_rate=0.99, avg_response_time_ms=50.0,
                           error_rate=0.01, circuit_breaker_trips=0, total_requests=100)
        assert m.agent_id == "a1"
    def test_to_dict(self):
        m = health_metrics(agent_id="a1", success_rate=1.0, avg_response_time_ms=10.0,
                           error_rate=0.0, circuit_breaker_trips=0, total_requests=10)
        d = m.to_dict()
        assert d["agent_id"] == "a1"
