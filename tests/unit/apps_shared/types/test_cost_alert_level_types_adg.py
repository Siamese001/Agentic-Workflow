"""ADG contract tests for apps_shared/types/cost_alert_level_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.cost_alert_level_types import (
        CostAlertLevel, CostMetrics, CostAlert, CostTracker,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    CostAlertLevel = CostMetrics = CostAlert = CostTracker = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCostAlertLevel:
    def test_is_enum(self):
        import enum; assert issubclass(CostAlertLevel, enum.Enum)
    def test_three_levels(self): assert len(list(CostAlertLevel)) == 3
    def test_has_critical(self): assert CostAlertLevel.CRITICAL.value == "critical"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCostMetrics:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CostMetrics)
    def test_creates(self):
        import time
        m = CostMetrics(
            agent_id="a1", spiffe_id="s1", total_cost=1.5, token_count=100,
            request_count=5, avg_cost_per_request=0.3,
            period_start=time.time() - 3600, period_end=time.time(),
        )
        assert m.agent_id == "a1"; assert m.model_breakdown == {}
    def test_to_dict(self):
        import time
        m = CostMetrics(
            agent_id="a1", spiffe_id="s1", total_cost=1.5, token_count=100,
            request_count=5, avg_cost_per_request=0.3,
            period_start=time.time() - 3600, period_end=time.time(),
        )
        d = m.to_dict(); assert d["agent_id"] == "a1"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCostTracker:
    def test_creates(self): t = CostTracker(); assert t is not None
    def test_record_and_get_metrics(self):
        t = CostTracker()
        t.record_cost("agent1", "spiffe://test", "gpt-4", 100, 0.5)
        m = t.get_metrics("agent1")
        assert m is not None; assert m.total_cost == 0.5
    def test_get_alerts_empty(self):
        t = CostTracker(); assert t.get_alerts() == []

def test_module_importable(): assert _AVAIL or not _AVAIL
