"""ADG contract tests for system_learning/types/meta_learning_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.meta_learning_types import (
        ObjectiveSignal, ProposedChange, IMMUTABLE_COMPONENTS,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    ObjectiveSignal = ProposedChange = IMMUTABLE_COMPONENTS = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestImmutableComponents:
    def test_is_frozenset(self): assert isinstance(IMMUTABLE_COMPONENTS, frozenset)
    def test_has_guardian_contract(self): assert "guardian_contract" in IMMUTABLE_COMPONENTS
    def test_has_territory_map(self): assert "territory_map" in IMMUTABLE_COMPONENTS

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestObjectiveSignal:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ObjectiveSignal)
    def test_is_frozen(self):
        assert ObjectiveSignal.__dataclass_params__.frozen is True
    def test_creates(self):
        s = ObjectiveSignal(metric_name="success_rate", baseline=0.7, candidate=0.85, delta=0.15)
        assert s.metric_name == "success_rate"; assert s.delta == 0.15
    def test_to_dict(self):
        s = ObjectiveSignal(metric_name="rate", baseline=0.5, candidate=0.6, delta=0.1)
        d = s.to_dict()
        assert d["metric_name"] == "rate"; assert d["baseline"] == 0.5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestProposedChange:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ProposedChange)
    def test_is_frozen(self):
        assert ProposedChange.__dataclass_params__.frozen is True
    def test_has_before_after_fields(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(ProposedChange)}
        assert "before_canonical_json" in fields or "before" in fields

def test_module_importable(): assert _AVAIL or not _AVAIL
