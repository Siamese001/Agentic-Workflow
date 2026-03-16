"""Healing Outcome Aggregator - Deterministic aggregation engine.

Phase 6: Aggregates L2.3 healing invocation records for meta-learning.
No wall-clock reads; all timestamps are explicit.
"""

from __future__ import annotations

from collections import defaultdict, deque

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.healing_outcome_types import (
    HealingOutcomeEvent,
    HealingOutcomeProposal,
    HealingOutcomeStats,
)

_emit_applies_guardrail("p0", "healing_outcome_aggregator", "p0_governance")
_emit_reads_policy_state("p0", "healing_outcome_aggregator", "policy_binding")
_emit_snapshots_state("p0", "healing_outcome_aggregator", "state_snapshot")
emit_replay_key("p0", "healing_outcome_aggregator")
emit_determinism_digest("p0", "healing_outcome_aggregator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class HealingOutcomeAggregator:
    """Deterministic aggregator for healing outcome data.

    Aggregates healing invocation records into deterministic snapshots.
    No wall-clock reads; all timestamps are explicit.
    """

    def __init__(self, window_size: int = 1000) -> None:
        """Initialize aggregator with optional window size.

        Parameters
        ----------
        window_size : int
            Maximum number of events retained. When exceeded, the oldest
            event is dropped (FIFO). Must be >= 1.
        """
        if window_size < 1:
            raise ValueError(f"window_size must be >= 1, got {window_size}")
        self._window_size = window_size
        self._buffer: deque[HealingOutcomeEvent] = deque(maxlen=window_size)
        # Internal state for new aggregation methods
        self._aggregates: dict[HealingOutcomeAggregateKey, tuple[int, int]] = defaultdict(lambda: (0, 0))

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingOutcomeAggregator.snapshot")

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

    # -----------------------------------------------------------------
    # New Phase 6 Methods
    # -----------------------------------------------------------------

    def ingest_invocation(self, invocation_record: InvocationRecord) -> None:
        """Ingest a healing invocation record.

        Args:
            invocation_record: Record of a healing invocation attempt.
        """
        key = HealingOutcomeAggregateKey(
            healer_name=invocation_record.healer_name,
            tier=invocation_record.tier,
            failure_type=invocation_record.failure_type
        )

        success_count, failure_count = self._aggregates[key]
        if invocation_record.success:
            success_count += 1
        else:
            failure_count += 1

        self._aggregates[key] = (success_count, failure_count)

    def compute_success_rate(self, key: HealingOutcomeAggregateKey) -> float:
        """Compute success rate for a specific key.

        Args:
            key: The aggregation key to compute rate for.

        Returns:
            Success rate (0.0 to 1.0) with deterministic rounding.
        """
        success_count, failure_count = self._aggregates[key]
        total_count = success_count + failure_count

        if total_count == 0:
            return 0.0

        # Round to 4 decimal places using round-half-up
        raw_rate = success_count / total_count
        return round(raw_rate + 1e-10, 4)  # Small epsilon for round-half-up

    def create_snapshot(self, created_utc: int) -> HealingOutcomeAggregateSnapshot:
        """Create a deterministic snapshot of current aggregates.

        Args:
            created_utc: Explicit timestamp for the snapshot.

        Returns:
            Deterministic snapshot with sorted aggregates.
        """
        # Convert internal state to aggregate objects
        aggregate_pairs = []
        for key, (success_count, failure_count) in self._aggregates.items():
            total_count = success_count + failure_count
            aggregate = HealingOutcomeAggregate(
                success_count=success_count,
                failure_count=failure_count,
                total_count=total_count
            )
            aggregate_pairs.append((key, aggregate))

        # Sort deterministically by (healer_name, tier, failure_type)
        aggregate_pairs.sort(key=lambda pair: (
            pair[0].healer_name,
            pair[0].tier,
            pair[0].failure_type
        ))

        # Create temporary snapshot without version_id to compute hash
        temp_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="temp",  # Temporary value
            created_utc=created_utc,
            aggregates=tuple(aggregate_pairs)
        )

        # Compute version_id as hash of content (excluding version_id)
        version_id = temp_snapshot.content_hash()

        # Create final snapshot with correct version_id
        snapshot = HealingOutcomeAggregateSnapshot(
            version_id=version_id,
            created_utc=created_utc,
            aggregates=tuple(aggregate_pairs)
        )

        return snapshot

    def clear_aggregates(self) -> None:
        """Clear all aggregated data."""
        self._aggregates.clear()


# Protocol for injection
class InvocationRecord:
    """Record of a single healing invocation.

    This is a simplified version for the aggregator.
    In practice, this would be imported from L2.3.
    """

    def __init__(
        self,
        healer_name: str,
        tier: str,
        failure_type: str,
        success: bool,
        timestamp_utc: int,
        trace_id: str | None = None,
        error_signature: str | None = None
    ) -> None:
        """Initialize invocation record."""
        self.healer_name = healer_name
        self.tier = tier
        self.failure_type = failure_type
        self.success = success
        self.timestamp_utc = timestamp_utc
        self.trace_id = trace_id
        self.error_signature = error_signature


# Protocol for the aggregator seam
class HealingOutcomeAggregatorProtocol:
    """Protocol for healing outcome aggregator injection."""

    def ingest_invocation(self, invocation_record: InvocationRecord) -> None:
        """Ingest a healing invocation record."""
        ...

    def compute_success_rate(self, key: HealingOutcomeAggregateKey) -> float:
        """Compute success rate for a key."""
        ...

    def create_snapshot(self, created_utc: int) -> HealingOutcomeAggregateSnapshot:
        """Create snapshot of aggregates."""
        ...


__all__ = [
    "HealingOutcomeAggregator",
    "InvocationRecord",
    "HealingOutcomeAggregatorProtocol",
]
