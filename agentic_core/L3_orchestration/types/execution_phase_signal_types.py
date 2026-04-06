from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "execution_phase_signal_types")
emit_determinism_digest("p0", "execution_phase_signal_types")

_emit_dispatches_healing_run("p1", "execution_phase_signal_types", "L3")
_emit_routes_through("p1", "execution_phase_signal_types", "L3")
_emit_checks_agent_registry("p1", "execution_phase_signal_types", "agent_registry")
_emit_validates_agent_capability("p1", "execution_phase_signal_types", "capability")
_emit_dispatches_execution_plan("p1", "execution_phase_signal_types", "exec_plan")
_emit_agent_executes_agent("p1", "execution_phase_signal_types", "sub_agent")
_emit_routes_to_agent("p1", "execution_phase_signal_types", "target_agent")
_emit_verifies_policy("p1", "execution_phase_signal_types", "policy_check")
_emit_observes_runtime_state("p1", "execution_phase_signal_types", "runtime_state")
_emit_verifies_boundary("p1", "execution_phase_signal_types", "boundary_check")
_emit_transcripts_response("p1", "execution_phase_signal_types", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_phase_signal_types")
_emit_gated_by_confidence("p1", "execution_phase_signal_types", "confidence_gate")
_emit_escalates_to_human("p1", "execution_phase_signal_types", "L3")
_emit_reads_policy_state("p1", "execution_phase_signal_types", "L3")

_emit_snapshots_state("p0", "execution_phase_signal_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "execution_phase_signal_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "execution_phase_signal_types")
_emit_authorize_and_execute("p2", "execution_phase_signal_types", "execution_auth")
_emit_validates_capability("p2", "execution_phase_signal_types", "capability_check")
_emit_routes_to_capability("p2", "execution_phase_signal_types", "capability_route")
_emit_writes_via_uwg("p2", "execution_phase_signal_types", "uwg_write")
_emit_blocks_direct_write("p2", "execution_phase_signal_types", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_phase_signal_types", "tool_invocation")
_emit_captures_execution_output("p2", "execution_phase_signal_types", "exec_output")
_emit_dispatches_agent("p3", "execution_phase_signal_types", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_phase_signal_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_phase_signal_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_phase_signal_types", "healing_outcome")
_emit_escalates_failure("p3", "execution_phase_signal_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_phase_signal_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_phase_signal_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_phase_signal_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_phase_signal_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_phase_signal_types", "eval_metric")
_emit_stores_embedding("p4", "execution_phase_signal_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_phase_signal_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_phase_signal_types", "exec_snapshot_link")

"\nOrchestration Types for agentic_core\n\nCore types used across orchestration components to avoid circular dependencies.\n"
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("execution_phase_signal_types", "p4obs", "metric_1")
_emit_emits_metric_event("execution_phase_signal_types", "p4obs", "metric_2")
_emit_emits_metric_event("execution_phase_signal_types", "p4obs", "metric_3")
_emit_emits_metric_event("execution_phase_signal_types", "p4obs", "metric_4")
_emit_emits_metric_event("execution_phase_signal_types", "p4obs", "metric_5")
_emit_emits_metric_event("execution_phase_signal_types", "p4obs", "metric_6")
_emit_records_incident_event("execution_phase_signal_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_phase_signal_types", "p4obs", "anomaly")
_emit_writes_observability_log("execution_phase_signal_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_phase_signal_types", "p4obs", "mon_state")
_emit_triggers_alert("execution_phase_signal_types", "p4obs", "alert")
_emit_links_incident_trace("execution_phase_signal_types", "p4obs", "trace_link")
_emit_captures_pattern("execution_phase_signal_types", "p3lm", "pattern")
_emit_records_learning_event("execution_phase_signal_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_phase_signal_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_phase_signal_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_phase_signal_types", "p3lm", "routing")
_emit_improves_agent_policy("execution_phase_signal_types", "p3lm", "policy")
_emit_stores_learning_state("execution_phase_signal_types", "p3lm", "state")
_emit_records_execution_trace("execution_phase_signal_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_phase_signal_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_phase_signal_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_phase_signal_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_phase_signal_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_phase_signal_types", "env_read", "p2_env_1")
_emit_reads_environ("execution_phase_signal_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_phase_signal_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_phase_signal_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_phase_signal_types", "context_pull")
_emit_pulls_context("p1", "execution_phase_signal_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "execution_phase_signal_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_phase_signal_types", "uwg_term_secondary")
_emit_writes_through("p1", "execution_phase_signal_types", "write_through")
_emit_writes_through("p1", "execution_phase_signal_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "execution_phase_signal_types", "safety_validation")
_emit_invokes_eval("p1", "execution_phase_signal_types", "eval_call")
_emit_proposal_commits_routing("p1", "execution_phase_signal_types", "routing_commit")


class ExecutionPhaseSignal(Enum):
    """Signal enum for phase logic checks."""

    PLANNING: Any = auto()
    EXECUTION: Any = auto()
    VALIDATION: Any = auto()
    HEALING: Any = auto()


@dataclass
class ExecutionPhase:
    """Definition of an execution phase - sovereign template for apps to extend."""

    name: str
    agents: list[str]
    execution_mode: str = "sequential"
    is_hard_gate: bool = False
    condition: Callable | None = None
    signal: ExecutionPhaseSignal = None

    def __post_init__(self):
        """Map name to signal enum for logic checks."""
        if self.signal is None:
            signal_map = {
                "planning": ExecutionPhaseSignal.PLANNING,
                "execution": ExecutionPhaseSignal.EXECUTION,
                "validation": ExecutionPhaseSignal.VALIDATION,
                "healing": ExecutionPhaseSignal.HEALING,
            }
            self.signal = signal_map.get(self.name.lower(), ExecutionPhaseSignal.PLANNING)


@dataclass
class WorkflowSnapshot:
    """Snapshot of workflow state for rollback - sovereign core type."""

    cycle: int
    context: dict[str, Any]
    outputs: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
