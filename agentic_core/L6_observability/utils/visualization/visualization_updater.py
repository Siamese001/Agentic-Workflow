"""Workflow visualization update entrypoints."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from agentic_core.L3_orchestration.visualization.workflow_visualization import (
    StageTransitionReason,
    WorkflowStatus,
    WorkflowVisualizationError,
    WorkflowVisualizationRecord,
    get_workflow_visualization_registry,
)

logger = logging.getLogger(__name__)


def workflow_visualization_emitted(
    record_id: str,
    run_id: str,
    workflow_id: str,
    stage: str,
    status: str,
) -> None:
    logger.debug(
        "workflow_visualization_emitted record_id=%s run_id=%s workflow_id=%s stage=%s status=%s",
        record_id,
        run_id,
        workflow_id,
        stage,
        status,
    )


def stage_transition_recorded(record_id: str, from_stage: str, to_stage: str, reason: str) -> None:
    logger.debug(
        "stage_transition_recorded record_id=%s from_stage=%s to_stage=%s reason=%s",
        record_id,
        from_stage,
        to_stage,
        reason,
    )


def owner_transition_recorded(record_id: str, current_owner: str, previous_owner: str | None) -> None:
    logger.debug(
        "owner_transition_recorded record_id=%s current_owner=%s previous_owner=%s",
        record_id,
        current_owner,
        previous_owner,
    )


def workflow_completed_recorded(record_id: str, final_stage: str, status: str) -> None:
    logger.debug(
        "workflow_completed_recorded record_id=%s final_stage=%s status=%s",
        record_id,
        final_stage,
        status,
    )


workflow_visualization_emitted("init", "init", "init", "init", "init")
stage_transition_recorded("init", "init", "init", "init")
owner_transition_recorded("init", "init", "init")
workflow_completed_recorded("init", "init", "init")


@dataclass(frozen=True)
class WorkflowVisualizationContext:
    run_id: str
    root_trace_id: str
    workflow_id: str
    current_stage: str
    completed_stages: set[str]
    pending_stages: set[str]
    current_owner_agent_id: str
    previous_owner_agent_id: str | None

    @classmethod
    def create(
        cls,
        run_id: str,
        root_trace_id: str,
        workflow_id: str,
        current_stage: str,
        completed_stages: set[str],
        pending_stages: set[str],
        current_owner_agent_id: str,
        previous_owner_agent_id: str | None = None,
    ) -> "WorkflowVisualizationContext":
        return cls(
            run_id=run_id,
            root_trace_id=root_trace_id,
            workflow_id=workflow_id,
            current_stage=current_stage,
            completed_stages=set(completed_stages or set()),
            pending_stages=set(pending_stages or set()),
            current_owner_agent_id=current_owner_agent_id,
            previous_owner_agent_id=previous_owner_agent_id,
        )


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    parent_trace_id: str | None
    trace_timestamp: float

    @classmethod
    def create(
        cls,
        trace_id: str,
        parent_trace_id: str | None = None,
        trace_timestamp: float | None = None,
    ) -> "TraceContext":
        return cls(
            trace_id=trace_id,
            parent_trace_id=parent_trace_id,
            trace_timestamp=float(trace_timestamp if trace_timestamp is not None else time.time()),
        )


def update_workflow_visualization(
    run_id: str,
    workflow_stage: str,
    owner_transition: tuple[str, str | None],
    workflow_status: WorkflowStatus,
    trace_context: TraceContext,
    *,
    completed_stages: set[str] | None = None,
    pending_stages: set[str] | None = None,
    stage_transition_reason: StageTransitionReason | None = None,
    registry=None,
) -> WorkflowVisualizationRecord:
    registry = registry or get_workflow_visualization_registry()
    if not workflow_stage:
        raise WorkflowVisualizationError("update_workflow_visualization: workflow_stage is required")
    if not trace_context.trace_id:
        raise WorkflowVisualizationError("update_workflow_visualization: trace_id is required")
    current_owner, previous_owner = owner_transition
    if not current_owner:
        raise WorkflowVisualizationError("update_workflow_visualization: current_owner is required")

    record = WorkflowVisualizationRecord.create(
        run_id=run_id,
        root_trace_id=trace_context.trace_id,
        workflow_id=f"workflow_{run_id}",
        current_stage=workflow_stage,
        completed_stages=set(completed_stages or set()),
        pending_stages=set(pending_stages or set()),
        current_owner_agent_id=current_owner,
        previous_owner_agent_id=previous_owner,
        workflow_status=workflow_status,
        stage_transition_reason=stage_transition_reason,
    )
    registry.persist_record(record)
    workflow_visualization_emitted(
        record.workflow_visualization_id,
        run_id,
        record.workflow_id,
        workflow_stage,
        workflow_status.value,
    )
    return record


def record_stage_transition(
    context: WorkflowVisualizationContext,
    to_stage: str,
    reason: StageTransitionReason = StageTransitionReason.NORMAL_TRANSITION,
    *,
    registry=None,
) -> WorkflowVisualizationRecord:
    completed = set(context.completed_stages)
    completed.add(context.current_stage)
    pending = set(context.pending_stages)
    pending.discard(to_stage)
    record = update_workflow_visualization(
        run_id=context.run_id,
        workflow_stage=to_stage,
        owner_transition=(context.current_owner_agent_id, context.previous_owner_agent_id),
        workflow_status=WorkflowStatus.ACTIVE,
        trace_context=TraceContext.create(trace_id=context.root_trace_id),
        completed_stages=completed,
        pending_stages=pending,
        stage_transition_reason=reason,
        registry=registry,
    )
    stage_transition_recorded(record.workflow_visualization_id, context.current_stage, to_stage, reason.value)
    return record


def record_owner_transition(
    context: WorkflowVisualizationContext,
    new_owner: str,
    *,
    registry=None,
) -> WorkflowVisualizationRecord:
    record = update_workflow_visualization(
        run_id=context.run_id,
        workflow_stage=context.current_stage,
        owner_transition=(new_owner, context.current_owner_agent_id),
        workflow_status=WorkflowStatus.ACTIVE,
        trace_context=TraceContext.create(trace_id=context.root_trace_id),
        completed_stages=context.completed_stages,
        pending_stages=context.pending_stages,
        registry=registry,
    )
    owner_transition_recorded(record.workflow_visualization_id, new_owner, context.current_owner_agent_id)
    return record


def record_workflow_completion(
    context: WorkflowVisualizationContext,
    *,
    status: WorkflowStatus = WorkflowStatus.COMPLETED,
    registry=None,
) -> WorkflowVisualizationRecord:
    if status not in {
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.BLOCKED,
        WorkflowStatus.ESCALATED,
    }:
        raise WorkflowVisualizationError("record_workflow_completion: terminal status required")
    completed = set(context.completed_stages)
    completed.add(context.current_stage)
    record = update_workflow_visualization(
        run_id=context.run_id,
        workflow_stage=context.current_stage,
        owner_transition=(context.current_owner_agent_id, context.previous_owner_agent_id),
        workflow_status=status,
        trace_context=TraceContext.create(trace_id=context.root_trace_id),
        completed_stages=completed,
        pending_stages=set(),
        registry=registry,
    )
    workflow_completed_recorded(record.workflow_visualization_id, context.current_stage, status.value)
    return record


def query_workflow_visualization(
    *,
    record_id: str | None = None,
    run_id: str | None = None,
    workflow_id: str | None = None,
    status: WorkflowStatus | str | None = None,
    registry=None,
) -> list[WorkflowVisualizationRecord]:
    registry = registry or get_workflow_visualization_registry()
    if record_id:
        record = registry.query_by_record_id(record_id)
        return [record] if record else []
    if run_id:
        return registry.query_by_run_id(run_id)
    if workflow_id:
        return registry.query_by_workflow_id(workflow_id)
    if status is not None:
        return registry.query_by_status(status)
    return list(getattr(registry, "_records", {}).values())


def update_simple_workflow(
    run_id: str,
    current_stage: str,
    current_owner: str,
    workflow_status: WorkflowStatus,
    trace_id: str,
) -> WorkflowVisualizationRecord:
    return update_workflow_visualization(
        run_id=run_id,
        workflow_stage=current_stage,
        owner_transition=(current_owner, None),
        workflow_status=workflow_status,
        trace_context=TraceContext.create(trace_id=trace_id),
    )


__all__ = [
    "WorkflowVisualizationContext",
    "TraceContext",
    "update_workflow_visualization",
    "record_stage_transition",
    "record_owner_transition",
    "record_workflow_completion",
    "query_workflow_visualization",
    "update_simple_workflow",
    "workflow_visualization_emitted",
    "stage_transition_recorded",
    "owner_transition_recorded",
    "workflow_completed_recorded",
]
