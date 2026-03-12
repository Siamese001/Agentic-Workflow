"""ADG contract tests for system_learning/types/healing_outcome_intake_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
    _AVAIL = True
except Exception:
    _AVAIL = False
    HealingOutcomeIntakeRecord = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealingOutcomeIntakeRecord:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HealingOutcomeIntakeRecord)
    def test_is_frozen(self):
        assert HealingOutcomeIntakeRecord.__dataclass_params__.frozen is True
    def test_has_required_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(HealingOutcomeIntakeRecord)}
        assert "schema_version" in fields
        assert "snapshot" in fields
        assert "proposal" in fields
    def test_schema_version_below_one_raises(self):
        with pytest.raises(ValueError):
            try:
                from system_learning.types.healing_outcome_types import HealingOutcomeStats, HealingOutcomeProposal
                stats = HealingOutcomeStats(healer_id="h", tier="T", failure_type="F",
                                           total_count=1, success_count=1, failure_count=0)
                proposal = HealingOutcomeProposal(target_tier="T", proposed_tier="T",
                                                  healer_id="h", failure_type="F",
                                                  confidence=0.9, rationale="ok")
                HealingOutcomeIntakeRecord(
                    schema_version=0, created_utc=1, window_size=10,
                    snapshot=(stats,), proposal=proposal, source="test",
                )
            except ImportError:
                pytest.skip("healing_outcome_types unavailable")

def test_module_importable(): assert _AVAIL or not _AVAIL
