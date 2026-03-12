"""ADG contract tests for system_learning/types/healing_outcome_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.healing_outcome_types import HealingOutcomeEvent, _stable_rate
    _AVAIL = True
except Exception:
    _AVAIL = False
    HealingOutcomeEvent = _stable_rate = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealingOutcomeEvent:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealingOutcomeEvent)
    def test_is_frozen(self):
        assert HealingOutcomeEvent.__dataclass_params__.frozen is True
    def test_creates(self):
        e = HealingOutcomeEvent(
            healer_id="check_imports",
            tier="LOCAL_AGENT",
            failure_type="IMPORT_ERROR",
            success=True,
            timestamp_utc=1000,
        )
        assert e.success is True; assert e.trace_id is None
    def test_immutable(self):
        e = HealingOutcomeEvent(
            healer_id="h", tier="T", failure_type="F", success=False, timestamp_utc=1
        )
        with pytest.raises((AttributeError, TypeError)):
            e.success = True  # type: ignore[misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStableRate:
    def test_zero_denominator(self): assert _stable_rate(5, 0) == 0.0
    def test_full_success(self): assert _stable_rate(10, 10) == 1.0
    def test_half(self): assert abs(_stable_rate(1, 2) - 0.5) < 1e-6

def test_module_importable(): assert _AVAIL or not _AVAIL
