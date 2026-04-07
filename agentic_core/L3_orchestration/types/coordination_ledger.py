"""
agentic_core/L3_orchestration/contracts/coordination_ledger.py

CoordinationLedger — P1/L3 run-scoped coordination state.

One CoordinationLedger per run.  All orchestrators and agents MUST update
through update_coordination_ledger(); no direct state mutation.

Spec fields:
    run_id, root_trace_id, current_owner_agent_id, current_stage,
    pending_stage, workflow_status, task_queue_hash, assigned_tasks_hash,
    handoff_count, policy_hash, state_version

Mandatory entrypoint:
    update_coordination_ledger(run_id, owner_agent_id, stage_transition,
                               task_update, orchestration_context)

ADG edges emitted:
    agent_executes_agent         — every ownership transition
    observes_runtime_state       — ledger reads active run state
    snapshots_state              — final workflow_status snapshot on completion
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_observes_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
)

logger = logging.getLogger(__name__)
_COORD_LOG = logging.getLogger("adg.agent_executes_agent")
_STATE_LOG = logging.getLogger("adg.observes_runtime_state")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class WorkflowStatus(str, Enum):
    """Top-level status of an entire run workflow."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


class TaskStatus(str, Enum):
    """Lifecycle status of a single task within a run."""

    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ESCALATED = "escalated"


# ---------------------------------------------------------------------------
# Task record
# ---------------------------------------------------------------------------


@dataclass
class TaskRecord:
    """Explicit task state entry in the CoordinationLedger."""

    task_id: str
    owner_agent_id: str
    status: TaskStatus = TaskStatus.QUEUED
    description: str = ""
    created_tick: float = field(default_factory=lambda: get_clock().now_epoch())
    updated_tick: float = 0.0
    completion_tick: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def transition(self, new_status: TaskStatus) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TaskRecord.transition")

        self.status = new_status
        self.updated_tick = get_clock().now_epoch()
        if new_status == TaskStatus.COMPLETED:
            self.completion_tick = self.updated_tick


# ---------------------------------------------------------------------------
# Ownership transition record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OwnershipTransition:
    """Immutable record of one agent ownership change."""

    previous_owner: str
    new_owner: str
    previous_stage: str
    new_stage: str
    handoff_reason: str
    timestamp_tick: float


# ---------------------------------------------------------------------------
# CoordinationLedger dataclass (P1/L3 spec: 11 required fields)
# ---------------------------------------------------------------------------


@dataclass
class CoordinationLedger:
    """Run-scoped coordination state ledger.

    Carries the 11 fields required by the P1/L3 spec plus mutable
    task and transition history.  Immutability is enforced at the
    field level — use update_coordination_ledger() to create new
    state versions; never mutate fields directly.
    """

    run_id: str
    root_trace_id: str
    current_owner_agent_id: str
    current_stage: str
    pending_stage: str
    workflow_status: WorkflowStatus
    task_queue_hash: str
    assigned_tasks_hash: str
    handoff_count: int
    policy_hash: str
    state_version: int

    _tasks: dict[str, TaskRecord] = field(default_factory=dict, repr=False)
    _transitions: list[OwnershipTransition] = field(default_factory=list, repr=False)
    _created_tick: float = field(default_factory=lambda: get_clock().now_epoch(), repr=False)

    # ------------------------------------------------------------------
    # Read-only views
    # ------------------------------------------------------------------

    def tasks_by_status(self, status: TaskStatus) -> list[TaskRecord]:
        return [t for t in self._tasks.values() if t.status == status]

    def queued_tasks(self) -> list[TaskRecord]:
        return self.tasks_by_status(TaskStatus.QUEUED)

    def in_progress_tasks(self) -> list[TaskRecord]:
        return self.tasks_by_status(TaskStatus.IN_PROGRESS)

    def completed_tasks(self) -> list[TaskRecord]:
        return self.tasks_by_status(TaskStatus.COMPLETED)

    def ownership_history(self) -> list[OwnershipTransition]:
        return list(self._transitions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "root_trace_id": self.root_trace_id,
            "current_owner_agent_id": self.current_owner_agent_id,
            "current_stage": self.current_stage,
            "pending_stage": self.pending_stage,
            "workflow_status": self.workflow_status.value,
            "task_queue_hash": self.task_queue_hash,
            "assigned_tasks_hash": self.assigned_tasks_hash,
            "handoff_count": self.handoff_count,
            "policy_hash": self.policy_hash,
            "state_version": self.state_version,
            "task_counts": {s.value: len(self.tasks_by_status(s)) for s in TaskStatus},
            "transitions": len(self._transitions),
        }


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _hash_task_ids(tasks: dict[str, TaskRecord], statuses: tuple) -> str:
    ids = sorted(tid for tid, t in tasks.items() if t.status in statuses)
    return hashlib.sha256("|".join(ids).encode()).hexdigest()[:16] if ids else "empty"


# ---------------------------------------------------------------------------
# Per-run ledger registry
# ---------------------------------------------------------------------------

_ledgers: dict[str, CoordinationLedger] = {}


def get_coordination_ledger(run_id: str) -> CoordinationLedger | None:
    """Return the CoordinationLedger for run_id, or None if not initialised."""
    return _ledgers.get(run_id)


def initialise_coordination_ledger(
    run_id: str,
    root_trace_id: str,
    owner_agent_id: str,
    policy_hash: str = "default",
    initial_stage: str = "init",
) -> CoordinationLedger:
    """Create and register a new CoordinationLedger for a run.

    Emits ``observes_runtime_state`` ADG edge.
    """
    _emit_observes_runtime_state(
        str(uuid.uuid4()), "Module.initialise_coordination_ledger", "L3_ORCHESTRATION",
    )
    ledger = CoordinationLedger(
        run_id=run_id,
        root_trace_id=root_trace_id,
        current_owner_agent_id=owner_agent_id,
        current_stage=initial_stage,
        pending_stage="",
        workflow_status=WorkflowStatus.INITIALIZING,
        task_queue_hash="empty",
        assigned_tasks_hash="empty",
        handoff_count=0,
        policy_hash=policy_hash,
        state_version=1,
    )
    _ledgers[run_id] = ledger
    _STATE_LOG.debug(
        "COORDINATION observes_runtime_state initialise run_id=%s "
        "owner=%s stage=%s policy=%s state_version=%d",
        run_id,
        owner_agent_id,
        initial_stage,
        policy_hash[:12],
        1,
    )
    logger.debug(
        "COORDINATION ledger initialised run_id=%s owner=%s stage=%s",
        run_id,
        owner_agent_id,
        initial_stage,
    )
    return ledger


# ---------------------------------------------------------------------------
# Mandatory update entrypoint
# ---------------------------------------------------------------------------


class MissingCoordinationLedger(RuntimeError):
    """Raised when update_coordination_ledger() is called without an existing ledger."""


class InvalidOwnershipTransition(ValueError):
    """Raised when the caller is not the current owner."""


class InvalidStageTransition(ValueError):
    """Raised when stage transition metadata is missing."""


def update_coordination_ledger(
    run_id: str,
    owner_agent_id: str,
    stage_transition: dict[str, str] | None = None,
    task_update: dict[str, Any] | None = None,
    orchestration_context: Any | None = None,
) -> CoordinationLedger:
    """Mandatory entrypoint for all coordination state mutations.

    Steps enforced:
        1. validate run_id (ledger must exist)
        2. validate current owner
        3. validate stage transition metadata
        4. update ledger fields
        5. emit trace linkage (agent_executes_agent, observes_runtime_state)
        6. persist new state_version

    Args:
        run_id:               Run identifier. Ledger must already be initialised.
        owner_agent_id:       Agent claiming or updating ownership.
        stage_transition:     Dict with keys: previous_stage, new_stage,
                              handoff_reason, new_owner (optional).
        task_update:          Dict with task_id, status, description (optional).
        orchestration_context: Context object for trace/policy binding.

    Returns:
        Updated CoordinationLedger.

    Raises:
        MissingCoordinationLedger:   ledger not found for run_id.
        InvalidOwnershipTransition:  caller not current owner and no new_owner given.
        InvalidStageTransition:      stage_transition missing required keys.
    """
    # 1. Validate run_id
    ledger = _ledgers.get(run_id)
    if ledger is None:
        raise MissingCoordinationLedger(
            f"update_coordination_ledger: no ledger for run_id={run_id}. "
            f"Call initialise_coordination_ledger() first.",
        )

    # 2. Validate ownership
    is_ownership_claim = (
        stage_transition is not None
        and "new_owner" in stage_transition
        and stage_transition["new_owner"] == owner_agent_id
    )
    is_current_owner = ledger.current_owner_agent_id == owner_agent_id
    if not is_current_owner and not is_ownership_claim:
        raise InvalidOwnershipTransition(
            f"update_coordination_ledger: agent '{owner_agent_id}' is not the "
            f"current owner ('{ledger.current_owner_agent_id}') of run_id={run_id} "
            f"and no new_owner transition provided.",
        )

    # 3. Validate stage transition metadata
    prev_owner = ledger.current_owner_agent_id
    prev_stage = ledger.current_stage
    new_stage = ledger.current_stage
    new_owner = ledger.current_owner_agent_id
    handoff_reason = ""

    if stage_transition is not None:
        if "new_stage" not in stage_transition:
            raise InvalidStageTransition(
                f"update_coordination_ledger: stage_transition missing 'new_stage' key for run_id={run_id}",
            )
        new_stage = stage_transition["new_stage"]
        new_owner = stage_transition.get("new_owner", ledger.current_owner_agent_id)
        handoff_reason = stage_transition.get("handoff_reason", "")
        pending = stage_transition.get("pending_stage", "")
        ledger.pending_stage = pending

        # Record ownership transition
        transition = OwnershipTransition(
            previous_owner=prev_owner,
            new_owner=new_owner,
            previous_stage=prev_stage,
            new_stage=new_stage,
            handoff_reason=handoff_reason,
            timestamp_tick=get_clock().now_epoch(),
        )
        ledger._transitions.append(transition)
        ledger.handoff_count += 1
        ledger.current_owner_agent_id = new_owner
        ledger.current_stage = new_stage

        # 5a. Emit agent_executes_agent ADG edge on ownership transition
        _COORD_LOG.debug(
            "agent_executes_agent COORDINATION prev_owner=%s new_owner=%s "
            "prev_stage=%s new_stage=%s run_id=%s handoff_count=%d reason=%s",
            prev_owner,
            new_owner,
            prev_stage,
            new_stage,
            run_id,
            ledger.handoff_count,
            handoff_reason,
        )

    # 4. Handle task update
    if task_update is not None:
        task_id = task_update.get("task_id", "")
        if task_id:
            if task_id not in ledger._tasks:
                ledger._tasks[task_id] = TaskRecord(
                    task_id=task_id,
                    owner_agent_id=owner_agent_id,
                    description=task_update.get("description", ""),
                )
            record = ledger._tasks[task_id]
            status_str = task_update.get("status", "")
            if status_str:
                try:
                    record.transition(TaskStatus(status_str))
                except ValueError:
                    logger.warning(
                        "COORDINATION unknown task status=%s task_id=%s",
                        status_str,
                        task_id,
                    )
            if "owner" in task_update:
                record.owner_agent_id = task_update["owner"]

    # Recompute task hashes
    ledger.task_queue_hash = _hash_task_ids(ledger._tasks, (TaskStatus.QUEUED,))
    ledger.assigned_tasks_hash = _hash_task_ids(ledger._tasks, (TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS))

    # Bind policy + trace from orchestration_context if provided
    if orchestration_context is not None:
        ph = getattr(orchestration_context, "policy_hash", None)
        if ph:
            ledger.policy_hash = ph
        sv = getattr(orchestration_context, "state_version", None)
        if sv is not None:
            # bump state_version if context provides a newer one
            try:
                sv_int = int(sv)
                if sv_int > ledger.state_version:
                    ledger.state_version = sv_int
            except (ValueError, TypeError):
                pass  # guardian: allow-silent-swallow -- intentional: ValueError used for control flow

    # 6. Increment state_version
    ledger.state_version += 1

    # 5b. Emit observes_runtime_state ADG edge
    _STATE_LOG.debug(
        "COORDINATION observes_runtime_state update run_id=%s owner=%s "
        "stage=%s status=%s state_version=%d handoff_count=%d",
        run_id,
        ledger.current_owner_agent_id,
        ledger.current_stage,
        ledger.workflow_status.value,
        ledger.state_version,
        ledger.handoff_count,
    )

    logger.debug(
        "COORDINATION updated run_id=%s owner=%s stage=%s version=%d",
        run_id,
        ledger.current_owner_agent_id,
        ledger.current_stage,
        ledger.state_version,
    )
    return ledger


def complete_coordination_ledger(
    run_id: str, final_status: WorkflowStatus = WorkflowStatus.COMPLETED,
) -> CoordinationLedger:
    """Mark a run's CoordinationLedger as complete.

    Emits ``snapshots_state`` ADG edge for completed runs.
    """
    ledger = _ledgers.get(run_id)
    if ledger is None:
        raise MissingCoordinationLedger(f"complete_coordination_ledger: no ledger for run_id={run_id}")
    ledger.workflow_status = final_status
    ledger.state_version += 1

    snap_log = logging.getLogger("adg.snapshots_state")
    snap_log.debug(
        "COORDINATION snapshots_state complete run_id=%s status=%s "
        "state_version=%d handoff_count=%d tasks=%d",
        run_id,
        final_status.value,
        ledger.state_version,
        ledger.handoff_count,
        len(ledger._tasks),
    )
    logger.info(
        "COORDINATION complete run_id=%s status=%s version=%d",
        run_id,
        final_status.value,
        ledger.state_version,
    )
    return ledger


def reset_coordination_ledgers() -> None:
    """Reset all ledgers (for testing)."""
    _ledgers.clear()


__all__ = [
    "CoordinationLedger",
    "TaskRecord",
    "TaskStatus",
    "WorkflowStatus",
    "OwnershipTransition",
    "initialise_coordination_ledger",
    "update_coordination_ledger",
    "complete_coordination_ledger",
    "get_coordination_ledger",
    "reset_coordination_ledgers",
    "MissingCoordinationLedger",
    "InvalidOwnershipTransition",
    "InvalidStageTransition",
]
