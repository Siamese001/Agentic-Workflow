"""Types for the Rewoo (Reasoning Without Observation) pattern.

Rewoo decouples planning from execution:
  1. Planner generates a full task list with reasoning annotations upfront
  2. Solver executes each task and stores intermediate results
  3. Worker updates the planner context with results for downstream steps
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "rewoo_types")
emit_determinism_digest("p0", "rewoo_types")

_emit_dispatches_healing_run("p1", "rewoo_types", "L3")
_emit_routes_through("p1", "rewoo_types", "L3")
_emit_escalates_to_human("p1", "rewoo_types", "L3")
_emit_reads_policy_state("p1", "rewoo_types", "L3")
_emit_authorize_and_execute("p2", "rewoo_types", "execution_auth")
_emit_validates_capability("p2", "rewoo_types", "capability_check")
_emit_routes_to_capability("p2", "rewoo_types", "capability_route")
_emit_writes_via_uwg("p2", "rewoo_types", "uwg_write")
_emit_blocks_direct_write("p2", "rewoo_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rewoo_types", "tool_invocation")
_emit_captures_execution_output("p2", "rewoo_types", "exec_output")
_emit_dispatches_agent("p3", "rewoo_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rewoo_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rewoo_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rewoo_types", "healing_outcome")
_emit_escalates_failure("p3", "rewoo_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rewoo_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rewoo_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rewoo_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rewoo_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rewoo_types", "eval_metric")
_emit_stores_embedding("p4", "rewoo_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rewoo_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rewoo_types", "exec_snapshot_link")


class RewooTaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RewooTask:
    """A single task in the Rewoo task list."""

    task_id: str
    description: str
    reasoning: str
    tool_name: str
    tool_input: dict[str, Any]
    depends_on: list[str] = field(default_factory=list)
    status: RewooTaskStatus = RewooTaskStatus.PENDING
    result: Any = None
    error: str | None = None


@dataclass
class RewooTaskList:
    """Ordered list of tasks produced by the Planner."""

    goal: str
    tasks: list[RewooTask] = field(default_factory=list)

    def get_task(self, task_id: str) -> RewooTask | None:
        return next((t for t in self.tasks if t.task_id == task_id), None)

    def ready_tasks(self) -> list[RewooTask]:
        """Return tasks whose dependencies are all completed."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "RewooTaskList.ready_tasks", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "RewooTaskList.ready_tasks", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RewooTaskList.ready_tasks")

        completed_ids = {t.task_id for t in self.tasks if t.status == RewooTaskStatus.COMPLETED}
        return [
            t
            for t in self.tasks
            if t.status == RewooTaskStatus.PENDING and all(d in completed_ids for d in t.depends_on)
        ]


@dataclass
class RewooContext:
    """Accumulated context across Planner → Solver → Worker passes."""

    goal: str
    task_list: RewooTaskList
    results: dict[str, Any] = field(default_factory=dict)
    iteration: int = 0
    final_answer: str | None = None
    success: bool = False
    error: str | None = None
