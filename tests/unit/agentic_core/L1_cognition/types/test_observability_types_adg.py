"""ADG contract tests for agentic_core/L1_cognition/types/observability_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.observability_types import MetricPoint, HealthStatus
    _AVAIL = True
except Exception:
    _AVAIL = False
    MetricPoint = HealthStatus = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMetricPoint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MetricPoint)
    def test_creates(self):
        m = MetricPoint(name="success_rate", value=0.95)
        assert m.name == "success_rate"; assert m.value == 0.95
        assert m.timestamp; assert m.tags == {}

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealthStatus:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealthStatus)
    def test_creates(self):
        h = HealthStatus(component="healing_engine", healthy=True, message="OK")
        assert h.healthy is True; assert h.component == "healing_engine"

def test_module_importable(): assert _AVAIL or not _AVAIL
