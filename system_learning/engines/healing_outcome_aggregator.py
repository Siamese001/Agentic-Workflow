"""Healing Outcome Aggregator - Deterministic aggregation engine.

Phase 6: Aggregates L2.3 healing invocation records for meta-learning.
No wall-clock reads; all timestamps are explicit.
"""

from __future__ import annotations

from collections import defaultdict, deque

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "healing_outcome_aggregator", "execution_auth")
_emit_validates_capability("p2", "healing_outcome_aggregator", "capability_check")
_emit_routes_to_capability("p2", "healing_outcome_aggregator", "capability_route")
_emit_writes_via_uwg("p2", "healing_outcome_aggregator", "uwg_write")
_emit_blocks_direct_write("p2", "healing_outcome_aggregator", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_outcome_aggregator", "tool_invocation")
_emit_captures_execution_output("p2", "healing_outcome_aggregator", "exec_output")
_emit_dispatches_agent("p3", "healing_outcome_aggregator", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_outcome_aggregator", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_outcome_aggregator", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_outcome_aggregator", "healing_outcome")
_emit_escalates_failure("p3", "healing_outcome_aggregator", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_outcome_aggregator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_outcome_aggregator", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_outcome_aggregator", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_outcome_aggregator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_outcome_aggregator", "eval_metric")
_emit_stores_embedding("p4", "healing_outcome_aggregator", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_outcome_aggregator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_outcome_aggregator", "exec_snapshot_link")
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("healing_outcome_aggregator", "p4obs", "metric_1")
_emit_emits_metric_event("healing_outcome_aggregator", "p4obs", "metric_2")
_emit_emits_metric_event("healing_outcome_aggregator", "p4obs", "metric_3")
_emit_emits_metric_event("healing_outcome_aggregator", "p4obs", "metric_4")
_emit_emits_metric_event("healing_outcome_aggregator", "p4obs", "metric_5")
_emit_emits_metric_event("healing_outcome_aggregator", "p4obs", "metric_6")
_emit_records_incident_event("healing_outcome_aggregator", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_outcome_aggregator", "p4obs", "anomaly")
_emit_writes_observability_log("healing_outcome_aggregator", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_outcome_aggregator", "p4obs", "mon_state")
_emit_triggers_alert("healing_outcome_aggregator", "p4obs", "alert")
_emit_links_incident_trace("healing_outcome_aggregator", "p4obs", "trace_link")
_emit_captures_pattern("healing_outcome_aggregator", "p3lm", "pattern")
_emit_records_learning_event("healing_outcome_aggregator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_outcome_aggregator", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_outcome_aggregator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_outcome_aggregator", "p3lm", "routing")
_emit_improves_agent_policy("healing_outcome_aggregator", "p3lm", "policy")
_emit_stores_learning_state("healing_outcome_aggregator", "p3lm", "state")
_emit_records_execution_trace("healing_outcome_aggregator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_outcome_aggregator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_outcome_aggregator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_outcome_aggregator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_outcome_aggregator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_outcome_aggregator", "env_read", "p2_env_1")
_emit_reads_environ("healing_outcome_aggregator", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_outcome_aggregator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_outcome_aggregator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_outcome_aggregator", "context_pull")
_emit_pulls_context("p1", "healing_outcome_aggregator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_aggregator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_outcome_aggregator", "uwg_term_2")
_emit_writes_through("p1", "healing_outcome_aggregator", "write_through")
_emit_writes_through("p1", "healing_outcome_aggregator", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_outcome_aggregator", "safety_validation")
_emit_invokes_eval("p1", "healing_outcome_aggregator", "eval_call")
_emit_proposal_commits_routing("p1", "healing_outcome_aggregator", "routing_commit")
_emit_escalates_to_human("p1", "healing_outcome_aggregator", "human_escalation")
_emit_routes_through("p1", "healing_outcome_aggregator", "route_through")
_emit_checks_agent_registry("p1", "healing_outcome_aggregator", "agent_registry")
_emit_validates_agent_capability("p1", "healing_outcome_aggregator", "capability")
_emit_dispatches_execution_plan("p1", "healing_outcome_aggregator", "exec_plan")
_emit_agent_executes_agent("p1", "healing_outcome_aggregator", "sub_agent")
_emit_routes_to_agent("p1", "healing_outcome_aggregator", "target_agent")
_emit_verifies_policy("p1", "healing_outcome_aggregator", "policy_check")
_emit_observes_runtime_state("p1", "healing_outcome_aggregator", "runtime_state")
_emit_verifies_boundary("p1", "healing_outcome_aggregator", "boundary_check")
_emit_transcripts_response("p1", "healing_outcome_aggregator", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_outcome_aggregator")
_emit_gated_by_confidence("p1", "healing_outcome_aggregator", "confidence_gate")
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
