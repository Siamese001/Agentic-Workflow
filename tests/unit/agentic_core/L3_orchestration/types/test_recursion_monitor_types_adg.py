"""ADG contract tests for L3_orchestration/types/recursion_monitor_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.recursion_monitor_types import (
    HealthStatus, AlertSeverity, Alert, RecursionMonitor,
)

class TestHealthStatus:
    def test_is_str_enum(self):
        import enum; assert issubclass(HealthStatus, str); assert issubclass(HealthStatus, enum.Enum)
    def test_has_healthy(self): assert HealthStatus.HEALTHY == "healthy"
    def test_has_critical(self): assert HealthStatus.CRITICAL == "critical"

class TestAlertSeverity:
    def test_is_str_enum(self):
        import enum; assert issubclass(AlertSeverity, str)
    def test_has_warning(self): assert AlertSeverity.WARNING == "warning"

class TestAlert:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(Alert)
    def test_creates(self):
        a = Alert(severity=AlertSeverity.INFO, message="ok", timestamp="2026-01-01", source="test")
        assert a.severity == AlertSeverity.INFO
        assert a.acknowledged is False

class TestRecursionMonitor:
    def test_creates(self):
        m = RecursionMonitor()
        assert m is not None
    def test_initial_circuit_closed(self):
        m = RecursionMonitor()
        assert m._circuit_open is False
    def test_record_spawn_success(self):
        m = RecursionMonitor()
        m.record_spawn(success=True, depth=2, duration_ms=10.0, memory_bytes=1024, cache_hit=True)
        assert m._consecutive_failures == 0
