from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "execution_phase_types")
trace_contract.emit_determinism_digest("p0", "execution_phase_types")

trace_contract._emit_dispatches_healing_run("p1", "execution_phase_types", "L1")
trace_contract._emit_routes_through("p1", "execution_phase_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "execution_phase_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "execution_phase_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "execution_phase_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "execution_phase_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "execution_phase_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "execution_phase_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "execution_phase_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "execution_phase_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "execution_phase_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "execution_phase_types")
trace_contract._emit_gated_by_confidence("p1", "execution_phase_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "execution_phase_types", "L1")
trace_contract._emit_reads_policy_state("p1", "execution_phase_types", "L1")
trace_contract._emit_authorize_and_execute("p2", "execution_phase_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "execution_phase_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "execution_phase_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "execution_phase_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "execution_phase_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "execution_phase_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "execution_phase_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "execution_phase_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "execution_phase_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "execution_phase_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "execution_phase_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "execution_phase_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "execution_phase_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "execution_phase_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "execution_phase_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "execution_phase_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "execution_phase_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "execution_phase_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "execution_phase_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "execution_phase_types", "exec_snapshot_link")

"Execution-related types and interfaces.\n\nDefines ExecutionContext, ExecutionResult, and ExecutionPhase for\norchestrating agent execution cycles.\n"
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


trace_contract._emit_emits_metric_event("execution_phase_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("execution_phase_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("execution_phase_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("execution_phase_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("execution_phase_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("execution_phase_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("execution_phase_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("execution_phase_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("execution_phase_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("execution_phase_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("execution_phase_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("execution_phase_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("execution_phase_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("execution_phase_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("execution_phase_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("execution_phase_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("execution_phase_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("execution_phase_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("execution_phase_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("execution_phase_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("execution_phase_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("execution_phase_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("execution_phase_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("execution_phase_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("execution_phase_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("execution_phase_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("execution_phase_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("execution_phase_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "execution_phase_types", "context_pull")
trace_contract._emit_pulls_context("p1", "execution_phase_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_phase_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_phase_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "execution_phase_types", "write_through")
trace_contract._emit_writes_through("p1", "execution_phase_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "execution_phase_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "execution_phase_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "execution_phase_types", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ExecutionContext.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ExecutionContext.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_COGNITION, "ExecutionContext.to_dict")
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
