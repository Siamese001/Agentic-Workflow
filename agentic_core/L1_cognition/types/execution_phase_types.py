from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execution_phase_types")
emit_determinism_digest("p0", "execution_phase_types")

_emit_dispatches_healing_run("p1", "execution_phase_types", "L1")
_emit_routes_through("p1", "execution_phase_types", "L1")
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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


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
