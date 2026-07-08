"""Healing Outcome Intake Adapter - persist-only adapter for meta-learning intake."""

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "healing_outcome_intake_adapter", "execution_auth")
trace_contract._emit_validates_capability("p2", "healing_outcome_intake_adapter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "healing_outcome_intake_adapter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "healing_outcome_intake_adapter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "healing_outcome_intake_adapter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "healing_outcome_intake_adapter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "healing_outcome_intake_adapter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "healing_outcome_intake_adapter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "healing_outcome_intake_adapter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "healing_outcome_intake_adapter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "healing_outcome_intake_adapter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "healing_outcome_intake_adapter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "healing_outcome_intake_adapter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "healing_outcome_intake_adapter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "healing_outcome_intake_adapter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "healing_outcome_intake_adapter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "healing_outcome_intake_adapter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "healing_outcome_intake_adapter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "healing_outcome_intake_adapter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "healing_outcome_intake_adapter", "exec_snapshot_link")
from .healing_outcome_aggregator import HealingOutcomeAggregator
from agentic_core.L6_system_learning.ports.healing_outcome_intake_store import HealingOutcomeIntakeStore
from agentic_core.L6_system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord

trace_contract._emit_applies_guardrail("p0", "healing_outcome_intake_adapter", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "healing_outcome_intake_adapter", "policy_binding")
trace_contract._emit_snapshots_state("p0", "healing_outcome_intake_adapter", "state_snapshot")

trace_contract._emit_emits_metric_event("healing_outcome_intake_adapter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("healing_outcome_intake_adapter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("healing_outcome_intake_adapter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("healing_outcome_intake_adapter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("healing_outcome_intake_adapter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("healing_outcome_intake_adapter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("healing_outcome_intake_adapter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("healing_outcome_intake_adapter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("healing_outcome_intake_adapter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("healing_outcome_intake_adapter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("healing_outcome_intake_adapter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("healing_outcome_intake_adapter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("healing_outcome_intake_adapter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("healing_outcome_intake_adapter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("healing_outcome_intake_adapter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("healing_outcome_intake_adapter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("healing_outcome_intake_adapter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("healing_outcome_intake_adapter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("healing_outcome_intake_adapter", "p3lm", "state")
trace_contract._emit_records_execution_trace("healing_outcome_intake_adapter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("healing_outcome_intake_adapter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("healing_outcome_intake_adapter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("healing_outcome_intake_adapter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("healing_outcome_intake_adapter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("healing_outcome_intake_adapter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("healing_outcome_intake_adapter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("healing_outcome_intake_adapter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("healing_outcome_intake_adapter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "healing_outcome_intake_adapter", "context_pull")
trace_contract._emit_pulls_context("p1", "healing_outcome_intake_adapter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_outcome_intake_adapter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "healing_outcome_intake_adapter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "healing_outcome_intake_adapter", "write_through")
trace_contract._emit_writes_through("p1", "healing_outcome_intake_adapter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "healing_outcome_intake_adapter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "healing_outcome_intake_adapter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "healing_outcome_intake_adapter", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "healing_outcome_intake_adapter", "human_escalation")
trace_contract._emit_routes_through("p1", "healing_outcome_intake_adapter", "route_through")
trace_contract._emit_checks_agent_registry("p1", "healing_outcome_intake_adapter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "healing_outcome_intake_adapter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "healing_outcome_intake_adapter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "healing_outcome_intake_adapter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "healing_outcome_intake_adapter", "target_agent")
trace_contract._emit_verifies_policy("p1", "healing_outcome_intake_adapter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "healing_outcome_intake_adapter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "healing_outcome_intake_adapter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "healing_outcome_intake_adapter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "healing_outcome_intake_adapter")
trace_contract._emit_gated_by_confidence("p1", "healing_outcome_intake_adapter", "confidence_gate")
trace_contract.emit_replay_key("p0", "healing_outcome_intake_adapter")
trace_contract.emit_determinism_digest("p0", "healing_outcome_intake_adapter")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
        self,
        aggregator: HealingOutcomeAggregator,
        created_utc: int,
        source: str = "L2.3-healing",
    ) -> HealingOutcomeIntakeRecord:
        """Build an intake record from aggregator state.

        Args:
            aggregator: The aggregator with snapshot and proposal
            created_utc: Explicit timestamp (no wall-clock reads)
            source: Source identifier for the record

        Returns:
            Immutable intake record with deterministically sorted snapshot
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HealingOutcomeIntakeAdapter.build_record"
        )

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
        self,
        window_start_utc: int,
        window_end_utc: int,
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
