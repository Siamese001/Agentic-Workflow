"""Healing Outcome Intake Types - Immutable contract for meta-learning intake."""

from dataclasses import dataclass

from system_learning.types.healing_outcome_types import HealingOutcomeProposal, HealingOutcomeStats


@dataclass(frozen=True, slots=True)
class HealingOutcomeIntakeRecord:
    """Immutable record for healing outcome intake into meta-learning pipeline.

    This is a persist-only artifact - no configuration or routing mutations.
    The snapshot is stored deterministically as a sorted tuple.
    """

    schema_version: int
    created_utc: int  # Explicit timestamp, no wall-clock reads in core logic
    window_size: int
    snapshot: tuple[HealingOutcomeStats, ...]  # Sorted deterministically
    proposal: HealingOutcomeProposal
    source: str  # e.g., "L2.3-healing"
    run_id: str | None = None
    trace_id: str | None = None

    def __post_init__(self) -> None:
        """Validate invariants."""
        if self.schema_version < 1:
            raise ValueError("schema_version must be >= 1")
        if self.window_size <= 0:
            raise ValueError("window_size must be positive")
        if not self.snapshot:
            raise ValueError("snapshot cannot be empty")
        # Ensure snapshot is deterministically sorted
        if list(self.snapshot) != sorted(self.snapshot, key=lambda s: (s.healer_id, s.tier, s.failure_type)):
            raise ValueError("snapshot must be sorted by (healer_id, tier, failure_type)")
