"""Healing Outcome Intake Adapter - persist-only adapter for meta-learning intake."""

from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
from system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore
from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord


class HealingOutcomeIntakeAdapter:
    """Adapter that converts HealingOutcomeAggregator outputs to intake records.

    This adapter is persist-only - it does not perform any configuration
    or routing mutations.
    """

    def __init__(self, store: HealingOutcomeIntakeStore) -> None:
        """Initialize adapter with a store implementation.

        Args:
            store: The store used for persisting records
        """
        self._store = store

    def build_record(
        self, aggregator: HealingOutcomeAggregator, created_utc: int, source: str = "L2.3-healing"
    ) -> HealingOutcomeIntakeRecord:
        """Build an intake record from aggregator state.

        Args:
            aggregator: The aggregator with snapshot and proposal
            created_utc: Explicit timestamp (no wall-clock reads)
            source: Source identifier for the record

        Returns:
            Immutable intake record with deterministically sorted snapshot
        """
        snapshot_tuple = aggregator.snapshot()
        proposal = aggregator.build_proposal()
        sorted_snapshot = tuple(sorted(snapshot_tuple, key=lambda s: (s.healer_id, s.tier, s.failure_type)))
        return HealingOutcomeIntakeRecord(
            schema_version=1,
            created_utc=created_utc,
            window_size=len(sorted_snapshot),
            snapshot=sorted_snapshot,
            proposal=proposal,
            source=source,
        )

    def persist_record(self, record: HealingOutcomeIntakeRecord) -> None:
        """Persist an intake record via the store.

        Args:
            record: The record to persist
        """
        self._store.write(record)

    def get_recent_records(
        self, window_start_utc: int, window_end_utc: int
    ) -> list[HealingOutcomeIntakeRecord]:
        """Return records whose created_utc falls within [window_start_utc, window_end_utc].

        Args:
            window_start_utc: Inclusive lower bound (UTC epoch seconds)
            window_end_utc: Inclusive upper bound (UTC epoch seconds)

        Returns:
            Filtered list of records, preserving insertion order
        """
        if window_start_utc > window_end_utc:
            return []
        return [r for r in self._store.get_records() if window_start_utc <= r.created_utc <= window_end_utc]
