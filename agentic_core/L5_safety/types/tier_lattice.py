"""
H7: Formal tier lattice definition with partial order.

Defines the canonical partial order over learning tiers (L0–L6)
and the backpressure drop policy.

Lattice invariants:
  1. Irreflexivity: no tier strictly dominates itself
  2. Antisymmetry: if a dominates b, b does not dominate a
  3. Transitivity: if a > b and b > c then a > c
  4. Escalation monotonicity: tier can only increase within
     a rollout sequence

Preservation policy:
  drop(L0) = safe
  drop(L1) = under pressure only
  never drop(L2+)
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class LearningTier(enum.IntEnum):
    """Canonical learning tier enumeration."""

    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6


class DropPolicy(enum.Enum):
    """Backpressure drop policy per tier."""

    SAFE = "safe"
    UNDER_PRESSURE = "under_pressure"
    NEVER = "never"


# Tier → drop policy mapping
_DROP_POLICY: dict[LearningTier, DropPolicy] = {
    LearningTier.L0: DropPolicy.SAFE,
    LearningTier.L1: DropPolicy.UNDER_PRESSURE,
    LearningTier.L2: DropPolicy.NEVER,
    LearningTier.L3: DropPolicy.NEVER,
    LearningTier.L4: DropPolicy.NEVER,
    LearningTier.L5: DropPolicy.NEVER,
    LearningTier.L6: DropPolicy.NEVER,
}


@dataclass(frozen=True)
class TierLattice:
    """Formal partial order over LearningTier.

    Uses the natural integer ordering of IntEnum values.
    ``dominates(a, b)`` means ``a`` is strictly higher than
    ``b`` in the lattice (a > b).
    """

    def dominates(self, a: LearningTier, b: LearningTier) -> bool:
        """Return True if ``a`` strictly dominates ``b``.

        Strict dominance: a.value > b.value.
        """
        return a.value > b.value

    def drop_policy(self, tier: LearningTier) -> DropPolicy:
        """Return the backpressure drop policy for a tier."""
        return _DROP_POLICY[tier]

    def can_drop(
        self,
        tier: LearningTier,
        under_pressure: bool = False,
    ) -> bool:
        """Whether a signal at this tier may be dropped."""
        policy = self.drop_policy(tier)
        if policy is DropPolicy.SAFE:
            return True
        if policy is DropPolicy.UNDER_PRESSURE:
            return under_pressure
        return False


@dataclass
class BackpressurePolicy:
    """Policy engine that references TierLattice for drops."""

    lattice: TierLattice

    def should_drop(
        self,
        tier: LearningTier,
        under_pressure: bool = False,
    ) -> bool:
        """Decide whether to drop a signal at this tier."""
        return self.lattice.can_drop(tier, under_pressure=under_pressure)


def validate_escalation_sequence(
    sequence: list[LearningTier],
) -> bool:
    """Validate that a rollout sequence is monotonically
    non-decreasing (escalation monotonicity).

    Returns True if valid, False if any tier decreases.
    """
    for i in range(1, len(sequence)):
        if sequence[i].value < sequence[i - 1].value:
            return False
    return True
