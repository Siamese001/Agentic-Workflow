from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execution_phase_signal_types")
emit_determinism_digest("p0", "execution_phase_signal_types")

_emit_dispatches_healing_run("p1", "execution_phase_signal_types", "L3")
_emit_routes_through("p1", "execution_phase_signal_types", "L3")
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
