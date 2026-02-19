"""H7 governance tests: Formal tier lattice with property-based tests.

Validates the 4 lattice invariants exhaustively over all (a, b) pairs:
1. Irreflexivity: no tier strictly dominates itself
2. Antisymmetry: if a dominates b, b does not dominate a
3. Transitivity: if a > b and b > c then a > c
4. Escalation monotonicity: tier can only increase in rollout

Also validates backpressure drop policy and BackpressurePolicy.
"""

import itertools

import pytest

from agentic_core.L5_safety.types.tier_lattice import (
    BackpressurePolicy,
    DropPolicy,
    LearningTier,
    TierLattice,
    validate_escalation_sequence,
)

pytestmark = pytest.mark.governance

ALL_TIERS = list(LearningTier)
ALL_PAIRS = list(itertools.permutations(ALL_TIERS, 2))
ALL_TRIPLES = list(itertools.permutations(ALL_TIERS, 3))

LATTICE = TierLattice()


class TestIrreflexivity:
    """No tier strictly dominates itself."""

    @pytest.mark.parametrize("t", ALL_TIERS, ids=str)
    def test_no_self_dominance(self, t):
        assert not LATTICE.dominates(t, t)


class TestAntisymmetry:
    """If a dominates b, b does not dominate a."""

    @pytest.mark.parametrize(
        "a,b",
        ALL_PAIRS,
        ids=[f"{a.name}-{b.name}" for a, b in ALL_PAIRS],
    )
    def test_antisymmetry(self, a, b):
        if LATTICE.dominates(a, b):
            assert not LATTICE.dominates(b, a)


class TestTransitivity:
    """If a > b and b > c then a > c."""

    @pytest.mark.parametrize(
        "a,b,c",
        ALL_TRIPLES,
        ids=[f"{a.name}-{b.name}-{c.name}" for a, b, c in ALL_TRIPLES],
    )
    def test_transitivity(self, a, b, c):
        if LATTICE.dominates(a, b) and LATTICE.dominates(b, c):
            assert LATTICE.dominates(a, c)


class TestEscalationMonotonicity:
    """Tier can only increase within a rollout sequence."""

    def test_valid_ascending_sequence(self):
        seq = [
            LearningTier.L0,
            LearningTier.L1,
            LearningTier.L2,
            LearningTier.L5,
        ]
        assert validate_escalation_sequence(seq) is True

    def test_valid_flat_sequence(self):
        seq = [
            LearningTier.L2,
            LearningTier.L2,
            LearningTier.L2,
        ]
        assert validate_escalation_sequence(seq) is True

    def test_invalid_descending_sequence(self):
        seq = [
            LearningTier.L3,
            LearningTier.L1,
        ]
        assert validate_escalation_sequence(seq) is False

    def test_empty_sequence_valid(self):
        assert validate_escalation_sequence([]) is True

    def test_single_element_valid(self):
        assert validate_escalation_sequence([LearningTier.L4]) is True


class TestDropPolicy:
    """Backpressure drop policy per tier."""

    def test_l0_safe_to_drop(self):
        assert LATTICE.drop_policy(LearningTier.L0) is DropPolicy.SAFE

    def test_l1_under_pressure_only(self):
        assert LATTICE.drop_policy(LearningTier.L1) is DropPolicy.UNDER_PRESSURE

    @pytest.mark.parametrize(
        "tier",
        [
            LearningTier.L2,
            LearningTier.L3,
            LearningTier.L4,
            LearningTier.L5,
            LearningTier.L6,
        ],
        ids=str,
    )
    def test_l2_plus_never_drop(self, tier):
        assert LATTICE.drop_policy(tier) is DropPolicy.NEVER


class TestCanDrop:
    """can_drop respects policy and pressure flag."""

    def test_l0_always_droppable(self):
        assert LATTICE.can_drop(LearningTier.L0) is True

    def test_l1_not_droppable_without_pressure(self):
        assert LATTICE.can_drop(LearningTier.L1, False) is False

    def test_l1_droppable_under_pressure(self):
        assert LATTICE.can_drop(LearningTier.L1, True) is True

    def test_l2_never_droppable(self):
        assert LATTICE.can_drop(LearningTier.L2, True) is False


class TestBackpressurePolicy:
    """BackpressurePolicy delegates to lattice."""

    def test_should_drop_l0(self):
        bp = BackpressurePolicy(lattice=LATTICE)
        assert bp.should_drop(LearningTier.L0) is True

    def test_should_not_drop_l2(self):
        bp = BackpressurePolicy(lattice=LATTICE)
        assert bp.should_drop(LearningTier.L2) is False

    def test_should_drop_l1_under_pressure(self):
        bp = BackpressurePolicy(lattice=LATTICE)
        assert bp.should_drop(LearningTier.L1, under_pressure=True) is True


class TestLatticeCompleteness:
    """All 21 distinct pairs are covered."""

    def test_21_distinct_pairs(self):
        assert len(ALL_PAIRS) == 42
        distinct = {(min(a, b), max(a, b)) for a, b in ALL_PAIRS}
        assert len(distinct) == 21
