"""Deterministic count-windowed aggregator for L2.3 healing outcomes.

Consumes HealingOutcomeEvent instances and produces deterministic
snapshots and proposals.

Invariants:
  - No wall-clock reads; timestamp comes from event only
  - Count-based window only (drop oldest beyond window_size)
  - Stable rounding via _stable_rate (round-half-up to 4 decimals)
  - Stable sort key: (healer_id, tier, failure_type)
  - build_proposal() is proposal-only; no file/config/routing writes
"""

from __future__ import annotations

from collections import deque

from system_learning.types.healing_outcome_types import (
    HealingOutcomeEvent,
    HealingOutcomeProposal,
    HealingOutcomeStats,
)


class HealingOutcomeAggregator:
    """Count-windowed aggregator producing deterministic snapshots.

    Parameters
    ----------
    window_size : int
        Maximum number of events retained.  When exceeded, the oldest
        event is dropped (FIFO).  Must be >= 1.
    """

    def __init__(self, window_size: int) -> None:
        if window_size < 1:
            raise ValueError(f"window_size must be >= 1, got {window_size}")
        self._window_size = window_size
        self._buffer: deque[HealingOutcomeEvent] = deque(maxlen=window_size)

    # -----------------------------------------------------------------
    # Ingest
    # -----------------------------------------------------------------

    def ingest(self, event: HealingOutcomeEvent) -> None:
        """Append an event.  Oldest is dropped when window is full."""
        self._buffer.append(event)

    # -----------------------------------------------------------------
    # Snapshot
    # -----------------------------------------------------------------

    def snapshot(self) -> list[HealingOutcomeStats]:
        """Produce a deterministic stats snapshot from the current window.

        Returns a list sorted by (healer_id, tier, failure_type).
        """
        # Accumulate counts per composite key
        counts: dict[tuple[str, str, str], tuple[int, int]] = {}
        for ev in self._buffer:
            key = (ev.healer_id, ev.tier, ev.failure_type)
            sc, fc = counts.get(key, (0, 0))
            if ev.success:
                counts[key] = (sc + 1, fc)
            else:
                counts[key] = (sc, fc + 1)

        # Build stats with stable sort
        stats: list[HealingOutcomeStats] = []
        for key in sorted(counts):
            healer_id, tier, failure_type = key
            sc, fc = counts[key]
            stats.append(
                HealingOutcomeStats.from_counts(
                    healer_id=healer_id,
                    tier=tier,
                    failure_type=failure_type,
                    success_count=sc,
                    failure_count=fc,
                )
            )
        return stats

    # -----------------------------------------------------------------
    # Proposal
    # -----------------------------------------------------------------

    def build_proposal(self) -> HealingOutcomeProposal:
        """Build a proposal-only container from the current snapshot.

        Phase 1: returns a no-op proposal carrying the snapshot.
        MUST NOT write files, mutate configs, or call external services.
        """
        stats = tuple(self.snapshot())
        return HealingOutcomeProposal(
            stats=stats,
            recommended_actions=(),
        )

    # -----------------------------------------------------------------
    # Introspection (read-only)
    # -----------------------------------------------------------------

    @property
    def window_size(self) -> int:
        """Configured maximum window size."""
        return self._window_size

    @property
    def event_count(self) -> int:
        """Number of events currently in the buffer."""
        return len(self._buffer)


__all__ = [
    "HealingOutcomeAggregator",
]
