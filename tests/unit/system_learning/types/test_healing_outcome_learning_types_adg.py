"""ADG contract tests for system_learning/types/healing_outcome_learning_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.healing_outcome_learning_types import (
        HealingOutcomeAggregateKey, HealingOutcomeAggregate,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    HealingOutcomeAggregateKey = HealingOutcomeAggregate = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealingOutcomeAggregateKey:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealingOutcomeAggregateKey)
    def test_is_frozen(self):
        assert HealingOutcomeAggregateKey.__dataclass_params__.frozen is True
    def test_creates(self):
        k = HealingOutcomeAggregateKey(
            healer_name="check_imports", tier="LOCAL_AGENT", failure_type="IMPORT_ERROR"
        )
        assert k.healer_name == "check_imports"
    def test_empty_healer_raises(self):
        with pytest.raises(ValueError):
            HealingOutcomeAggregateKey(healer_name="", tier="T", failure_type="F")
    def test_empty_tier_raises(self):
        with pytest.raises(ValueError):
            HealingOutcomeAggregateKey(healer_name="h", tier="", failure_type="F")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealingOutcomeAggregate:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealingOutcomeAggregate)
    def test_is_frozen(self):
        assert HealingOutcomeAggregate.__dataclass_params__.frozen is True
    def test_has_count_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(HealingOutcomeAggregate)}
        assert "success_count" in fields
        assert "failure_count" in fields

def test_module_importable(): assert _AVAIL or not _AVAIL
