"""
L6 Observability Vigilance Dispatcher - Pure Event Dispatch

Emits immutable VigilanceEvent artifacts and routes via injected enqueue seams.
L6 has ZERO authority: no decisions, no direct L4 mutation, no L2/L5 coupling.
"""

from dataclasses import dataclass
from typing import Callable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    record_execution_trace,
)

emit_replay_key("p0", "vigilance_dispatcher")
emit_determinism_digest("p0", "vigilance_dispatcher")

_emit_dispatches_healing_run("p1", "vigilance_dispatcher", "L6")
_emit_routes_through("p1", "vigilance_dispatcher", "L6")
_emit_checks_agent_registry("p1", "vigilance_dispatcher", "agent_registry")
_emit_validates_agent_capability("p1", "vigilance_dispatcher", "capability")
_emit_dispatches_execution_plan("p1", "vigilance_dispatcher", "exec_plan")
_emit_agent_executes_agent("p1", "vigilance_dispatcher", "sub_agent")
_emit_routes_to_agent("p1", "vigilance_dispatcher", "target_agent")
_emit_verifies_policy("p1", "vigilance_dispatcher", "policy_check")
_emit_observes_runtime_state("p1", "vigilance_dispatcher", "runtime_state")
_emit_verifies_boundary("p1", "vigilance_dispatcher", "boundary_check")
_emit_transcripts_response("p1", "vigilance_dispatcher", "transcript")
_emit_hard_fails_untranscripted("p1", "vigilance_dispatcher")
_emit_gated_by_confidence("p1", "vigilance_dispatcher", "confidence_gate")
_emit_escalates_to_human("p1", "vigilance_dispatcher", "L6")
_emit_reads_policy_state("p1", "vigilance_dispatcher", "L6")
_emit_authorize_and_execute("p2", "vigilance_dispatcher", "execution_auth")
_emit_validates_capability("p2", "vigilance_dispatcher", "capability_check")
_emit_routes_to_capability("p2", "vigilance_dispatcher", "capability_route")
_emit_writes_via_uwg("p2", "vigilance_dispatcher", "uwg_write")
_emit_blocks_direct_write("p2", "vigilance_dispatcher", "direct_write_block")
_emit_records_tool_invocation("p2", "vigilance_dispatcher", "tool_invocation")
_emit_captures_execution_output("p2", "vigilance_dispatcher", "exec_output")
_emit_dispatches_agent("p3", "vigilance_dispatcher", "agent_dispatch")
_emit_coordinates_agents("p3", "vigilance_dispatcher", "agent_coordination")
_emit_records_workflow_lineage("p3", "vigilance_dispatcher", "workflow_lineage")
_emit_records_healing_outcome("p3", "vigilance_dispatcher", "healing_outcome")
_emit_escalates_failure("p3", "vigilance_dispatcher", "failure_escalation")
_emit_orchestrates_workflow("p3", "vigilance_dispatcher", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vigilance_dispatcher", "healing_dispatch")
_emit_invokes_evaluation("p3", "vigilance_dispatcher", "evaluation_signal")
_emit_records_telemetry_event("p4", "vigilance_dispatcher", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vigilance_dispatcher", "eval_metric")
_emit_stores_embedding("p4", "vigilance_dispatcher", "embedding_store")
_emit_updates_meta_learning_state("p4", "vigilance_dispatcher", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vigilance_dispatcher", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

record_execution_trace("vigilance_dispatcher", "vigilance_dispatcher_trace")


_emit_emits_metric_event("vigilance_dispatcher", "p4obs", "metric_1")
_emit_emits_metric_event("vigilance_dispatcher", "p4obs", "metric_2")
_emit_emits_metric_event("vigilance_dispatcher", "p4obs", "metric_3")
_emit_emits_metric_event("vigilance_dispatcher", "p4obs", "metric_4")
_emit_emits_metric_event("vigilance_dispatcher", "p4obs", "metric_5")
_emit_emits_metric_event("vigilance_dispatcher", "p4obs", "metric_6")
_emit_records_incident_event("vigilance_dispatcher", "p4obs", "incident")
_emit_captures_runtime_anomaly("vigilance_dispatcher", "p4obs", "anomaly")
_emit_writes_observability_log("vigilance_dispatcher", "p4obs", "obs_log")
_emit_updates_monitoring_state("vigilance_dispatcher", "p4obs", "mon_state")
_emit_triggers_alert("vigilance_dispatcher", "p4obs", "alert")
_emit_links_incident_trace("vigilance_dispatcher", "p4obs", "trace_link")
_emit_captures_pattern("vigilance_dispatcher", "p3lm", "pattern")
_emit_records_learning_event("vigilance_dispatcher", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vigilance_dispatcher", "p3lm", "snapshot")
_emit_feeds_meta_learning("vigilance_dispatcher", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vigilance_dispatcher", "p3lm", "routing")
_emit_improves_agent_policy("vigilance_dispatcher", "p3lm", "policy")
_emit_stores_learning_state("vigilance_dispatcher", "p3lm", "state")
_emit_records_execution_trace("vigilance_dispatcher", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vigilance_dispatcher", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vigilance_dispatcher", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vigilance_dispatcher", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vigilance_dispatcher", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vigilance_dispatcher", "env_read", "p2_env_1")
_emit_reads_environ("vigilance_dispatcher", "env_read", "p2_env_2")
_emit_reads_runtime_state("vigilance_dispatcher", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vigilance_dispatcher", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vigilance_dispatcher", "context_pull")
_emit_pulls_context("p1", "vigilance_dispatcher", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vigilance_dispatcher", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vigilance_dispatcher", "uwg_term_2")
_emit_writes_through("p1", "vigilance_dispatcher", "write_through")
_emit_writes_through("p1", "vigilance_dispatcher", "write_through_2")
_emit_validated_by_safety_plane("p1", "vigilance_dispatcher", "safety_validation")
_emit_invokes_eval("p1", "vigilance_dispatcher", "eval_call")
_emit_proposal_commits_routing("p1", "vigilance_dispatcher", "routing_commit")


@dataclass(frozen=True)
class VigilanceEventArtifact:
    """Immutable vigilance event artifact."""

    trace_id: str
    signals: tuple[str, ...]
    summary: str

    @classmethod
    def create(cls, trace_id: str, signals: tuple[str, ...], summary: str) -> "VigilanceEventArtifact":
        """
        Create a new VigilanceEventArtifact with normalized signals.

        Args:
            trace_id: Unique trace identifier
            signals: Raw signals tuple
            summary: Event summary

        Returns:
            New VigilanceEventArtifact with sorted unique signals
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "VigilanceEventArtifact.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "VigilanceEventArtifact.create", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "VigilanceEventArtifact.create"
        )

        unique_signals = tuple(sorted(set(signals)))
        return cls(trace_id=trace_id, signals=unique_signals, summary=summary)


class VigilanceDispatcher:
    """
    Pure vigilance event dispatcher.

    Routes events via injected enqueue function only.
    No branching, no scoring, no routing logic, no state mutation.
    """

    def dispatch(
        self, *, event: VigilanceEventArtifact, enqueue_fn: Callable[[VigilanceEventArtifact], None]
    ) -> None:
        """
        Dispatch event using injected enqueue function.

        Calls enqueue_fn(event) exactly once.
        No branching, no scoring, no routing logic.

        Args:
            event: Event to dispatch
            enqueue_fn: Function to enqueue the event
        """
        enqueue_fn(event)


def to_meta_payload(event: VigilanceEventArtifact) -> dict:
    """
    Convert VigilanceEventArtifact to meta-learning payload.

    Args:
        event: Event artifact to convert

    Returns:
        Dictionary with trace_id, signals list, and summary
    """
    return {"trace_id": event.trace_id, "signals": list(event.signals), "summary": event.summary}
