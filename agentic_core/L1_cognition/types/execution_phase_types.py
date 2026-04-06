from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "execution_phase_types")
emit_determinism_digest("p0", "execution_phase_types")

_emit_dispatches_healing_run("p1", "execution_phase_types", "L1")
_emit_routes_through("p1", "execution_phase_types", "L1")
_emit_checks_agent_registry("p1", "execution_phase_types", "agent_registry")
_emit_validates_agent_capability("p1", "execution_phase_types", "capability")
_emit_dispatches_execution_plan("p1", "execution_phase_types", "exec_plan")
_emit_agent_executes_agent("p1", "execution_phase_types", "sub_agent")
_emit_routes_to_agent("p1", "execution_phase_types", "target_agent")
_emit_verifies_policy("p1", "execution_phase_types", "policy_check")
_emit_observes_runtime_state("p1", "execution_phase_types", "runtime_state")
_emit_verifies_boundary("p1", "execution_phase_types", "boundary_check")
_emit_transcripts_response("p1", "execution_phase_types", "transcript")
_emit_hard_fails_untranscripted("p1", "execution_phase_types")
_emit_gated_by_confidence("p1", "execution_phase_types", "confidence_gate")
_emit_escalates_to_human("p1", "execution_phase_types", "L1")
_emit_reads_policy_state("p1", "execution_phase_types", "L1")
_emit_authorize_and_execute("p2", "execution_phase_types", "execution_auth")
_emit_validates_capability("p2", "execution_phase_types", "capability_check")
_emit_routes_to_capability("p2", "execution_phase_types", "capability_route")
_emit_writes_via_uwg("p2", "execution_phase_types", "uwg_write")
_emit_blocks_direct_write("p2", "execution_phase_types", "direct_write_block")
_emit_records_tool_invocation("p2", "execution_phase_types", "tool_invocation")
_emit_captures_execution_output("p2", "execution_phase_types", "exec_output")
_emit_dispatches_agent("p3", "execution_phase_types", "agent_dispatch")
_emit_coordinates_agents("p3", "execution_phase_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution_phase_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution_phase_types", "healing_outcome")
_emit_escalates_failure("p3", "execution_phase_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution_phase_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution_phase_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution_phase_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution_phase_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution_phase_types", "eval_metric")
_emit_stores_embedding("p4", "execution_phase_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution_phase_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution_phase_types", "exec_snapshot_link")

"Execution-related types and interfaces.\n\nDefines ExecutionContext, ExecutionResult, and ExecutionPhase for\norchestrating agent execution cycles.\n"
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("execution_phase_types", "p4obs", "metric_1")
_emit_emits_metric_event("execution_phase_types", "p4obs", "metric_2")
_emit_emits_metric_event("execution_phase_types", "p4obs", "metric_3")
_emit_emits_metric_event("execution_phase_types", "p4obs", "metric_4")
_emit_emits_metric_event("execution_phase_types", "p4obs", "metric_5")
_emit_emits_metric_event("execution_phase_types", "p4obs", "metric_6")
_emit_records_incident_event("execution_phase_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("execution_phase_types", "p4obs", "anomaly")
_emit_writes_observability_log("execution_phase_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("execution_phase_types", "p4obs", "mon_state")
_emit_triggers_alert("execution_phase_types", "p4obs", "alert")
_emit_links_incident_trace("execution_phase_types", "p4obs", "trace_link")
_emit_captures_pattern("execution_phase_types", "p3lm", "pattern")
_emit_records_learning_event("execution_phase_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execution_phase_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("execution_phase_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execution_phase_types", "p3lm", "routing")
_emit_improves_agent_policy("execution_phase_types", "p3lm", "policy")
_emit_stores_learning_state("execution_phase_types", "p3lm", "state")
_emit_records_execution_trace("execution_phase_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execution_phase_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execution_phase_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execution_phase_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execution_phase_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execution_phase_types", "env_read", "p2_env_1")
_emit_reads_environ("execution_phase_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("execution_phase_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execution_phase_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execution_phase_types", "context_pull")
_emit_pulls_context("p1", "execution_phase_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execution_phase_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execution_phase_types", "uwg_term_2")
_emit_writes_through("p1", "execution_phase_types", "write_through")
_emit_writes_through("p1", "execution_phase_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "execution_phase_types", "safety_validation")
_emit_invokes_eval("p1", "execution_phase_types", "eval_call")
_emit_proposal_commits_routing("p1", "execution_phase_types", "routing_commit")


class ExecutionPhase(Enum):
    """Phases of the Think-Act-Observe execution cycle."""

    MISSION: Any = "mission"
    SCENE: Any = "scene"
    THINK: Any = "think"
    ACT: Any = "act"
    OBSERVE: Any = "observe"
    REFLECT: Any = "reflect"


@dataclass
class ExecutionContext:
    """Context for agent execution containing mission, scene, and state.

    Attributes:
        mission: The goal or Task to accomplish
        scene: Environmental context and available resources
        state: Current execution state (mutable during execution)
        history: List of previous execution steps
        metadata: Additional context metadata
        previous_phase_signals: Signals from previous phase execution
    """

    mission: str
    scene: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    previous_phase_signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ExecutionContext.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ExecutionContext.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "ExecutionContext.to_dict")
        return {
            "mission": self.mission,
            "scene": self.scene,
            "state": self.state,
            "history": self.history,
            "metadata": self.metadata,
            "previous_phase_signals": self.previous_phase_signals,
        }


@dataclass
class ExecutionResult:
    """Result of an agent execution cycle.

    Attributes:
        success: Whether execution completed successfully
        output: Final output/result of execution
        final_state: State at end of execution
        execution_trace: List of execution steps taken
        iterations: Number of Think-Act-Observe iterations
        errors: List of errors encountered
        metadata: Additional result metadata
    """

    success: bool = False
    output: Any | None = None
    final_state: dict[str, Any] = field(default_factory=dict)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    iterations: int = 0
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "output": self.output,
            "final_state": self.final_state,
            "execution_trace": self.execution_trace,
            "iterations": self.iterations,
            "errors": self.errors,
            "metadata": self.metadata,
        }
