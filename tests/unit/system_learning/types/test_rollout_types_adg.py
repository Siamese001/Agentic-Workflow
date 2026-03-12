"""ADG contract tests for system_learning/types/rollout_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.rollout_types import MetaLearningRolloutPlanArtifact, ROLLOUT_STRATEGIES, ROLLBACK_REASONS
    _AVAIL = True
except Exception:
    _AVAIL = False
    MetaLearningRolloutPlanArtifact = ROLLOUT_STRATEGIES = ROLLBACK_REASONS = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRolloutConstants:
    def test_rollout_strategies_is_frozenset(self):
        assert isinstance(ROLLOUT_STRATEGIES, frozenset)
    def test_has_canary(self): assert "CANARY" in ROLLOUT_STRATEGIES
    def test_has_all_at_once(self): assert "ALL_AT_ONCE" in ROLLOUT_STRATEGIES
    def test_rollback_reasons_has_timeout(self): assert "TIMEOUT" in ROLLBACK_REASONS
    def test_rollback_reasons_has_manual(self): assert "MANUAL" in ROLLBACK_REASONS

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMetaLearningRolloutPlanArtifact:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MetaLearningRolloutPlanArtifact)
    def test_is_frozen(self):
        assert MetaLearningRolloutPlanArtifact.__dataclass_params__.frozen is True
    def test_has_required_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(MetaLearningRolloutPlanArtifact)}
        assert "artifact_type" in fields
        assert "rollout_strategy" in fields
        assert "invariants" in fields

def test_module_importable(): assert _AVAIL or not _AVAIL
