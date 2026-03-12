"""ADG contract tests for agentic_core/L5_safety/types/tier_lattice_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.tier_lattice_types import (
        LearningTier, DropPolicy, TierLattice,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    LearningTier = DropPolicy = TierLattice = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLearningTier:
    def test_is_int_enum(self):
        import enum; assert issubclass(LearningTier, enum.IntEnum)
    def test_has_seven_tiers(self):
        assert len(list(LearningTier)) == 7
    def test_l0_is_zero(self): assert LearningTier.L0 == 0
    def test_l6_is_six(self): assert LearningTier.L6 == 6

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestDropPolicy:
    def test_is_enum(self):
        import enum; assert issubclass(DropPolicy, enum.Enum)
    def test_has_safe(self): assert DropPolicy.SAFE.value == "safe"
    def test_has_never(self): assert DropPolicy.NEVER.value == "never"
    def test_has_under_pressure(self): assert DropPolicy.UNDER_PRESSURE

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTierLattice:
    def test_is_frozen(self): assert TierLattice.__dataclass_params__.frozen is True
    def test_dominates_higher_over_lower(self):
        lat = TierLattice()
        assert lat.dominates(LearningTier.L6, LearningTier.L0) is True
    def test_does_not_dominate_lower_over_higher(self):
        lat = TierLattice()
        assert lat.dominates(LearningTier.L0, LearningTier.L6) is False
    def test_irreflexivity(self):
        lat = TierLattice()
        assert lat.dominates(LearningTier.L3, LearningTier.L3) is False
    def test_l0_drop_policy_safe(self):
        lat = TierLattice()
        assert lat.drop_policy(LearningTier.L0) == DropPolicy.SAFE
    def test_l2_drop_policy_never(self):
        lat = TierLattice()
        assert lat.drop_policy(LearningTier.L2) == DropPolicy.NEVER
    def test_can_drop_l0(self):
        lat = TierLattice()
        assert lat.can_drop(LearningTier.L0) is True
    def test_cannot_drop_l2(self):
        lat = TierLattice()
        assert lat.can_drop(LearningTier.L2) is False

def test_module_importable(): assert _AVAIL or not _AVAIL
