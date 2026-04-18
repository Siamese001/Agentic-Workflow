"""Workflow visualization records and registry helpers."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

get_clock: Any = None

try:
    from agentic_core.L2_execution.utils.providers import (
        get_clock,
    )  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
except ImportError:
    get_clock = None


def _now_epoch() -> float:
    if get_clock is not None:
        try:
            return float(get_clock().now_epoch())
        except (AttributeError, RuntimeError, TypeError, ValueError):
            pass
    return time.time()


class WorkflowStatus(Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class StageTransitionReason(Enum):
    NORMAL_TRANSITION = "NORMAL_TRANSITION"
    RETRY_TRIGGERED = "RETRY_TRIGGERED"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"
    BLOCK_DETECTED = "BLOCK_DETECTED"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"


ACTIVE = WorkflowStatus.ACTIVE
BLOCKED = WorkflowStatus.BLOCKED
RETRYING = WorkflowStatus.RETRYING
ESCALATED = WorkflowStatus.ESCALATED
COMPLETED = WorkflowStatus.COMPLETED
FAILED = WorkflowStatus.FAILED

NORMAL_TRANSITION = StageTransitionReason.NORMAL_TRANSITION
RETRY_TRIGGERED = StageTransitionReason.RETRY_TRIGGERED
ESCALATION_TRIGGERED = StageTransitionReason.ESCALATION_TRIGGERED
BLOCK_DETECTED = StageTransitionReason.BLOCK_DETECTED
WORKFLOW_ERROR = StageTransitionReason.WORKFLOW_ERROR


class WorkflowVisualizationError(Exception):
    """Raised when workflow visualization contracts are violated."""


def _hash_set(values: set[str]) -> str:
    encoded = json.dumps(sorted(values), separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}-{hashlib.sha256(encoded).hexdigest()[:16]}"


@dataclass(frozen=True)
class WorkflowVisualizationRecord:
    workflow_visualization_id: str
    run_id: str
    root_trace_id: str
    workflow_id: str
    current_stage: str
    completed_stages_hash: str
    pending_stages_hash: str
    current_owner_agent_id: str
    previous_owner_agent_id: str | None
    workflow_status: str
    stage_transition_reason_hash: str | None
    last_updated_tick: float
    visualization_epoch: float = field(default_factory=_now_epoch)

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
        previous_owner_agent_id: str | None,
        workflow_status: WorkflowStatus,
        stage_transition_reason: StageTransitionReason | None = None,
    ) -> "WorkflowVisualizationRecord":
        if not current_stage:
            raise WorkflowVisualizationError("current_stage is required")
        if not workflow_status:
            raise WorkflowVisualizationError("workflow_status is required")
        payload = {
            "run_id": run_id,
            "root_trace_id": root_trace_id,
            "workflow_id": workflow_id,
            "current_stage": current_stage,
            "current_owner_agent_id": current_owner_agent_id,
            "workflow_status": workflow_status.value,
            "stage_transition_reason": stage_transition_reason.value if stage_transition_reason else None,
        }
        return cls(
            workflow_visualization_id=_stable_id("wf", payload),
            run_id=run_id,
            root_trace_id=root_trace_id,
            workflow_id=workflow_id,
            current_stage=current_stage,
            completed_stages_hash=_hash_set(set(completed_stages or set())),
            pending_stages_hash=_hash_set(set(pending_stages or set())),
            current_owner_agent_id=current_owner_agent_id,
            previous_owner_agent_id=previous_owner_agent_id,
            workflow_status=workflow_status.value,
            stage_transition_reason_hash=(
                hashlib.sha256(stage_transition_reason.value.encode("utf-8")).hexdigest()[:16]
                if stage_transition_reason
                else None
            ),
            last_updated_tick=_now_epoch(),
        )

    def has_current_stage(self) -> bool:
        return bool(self.current_stage)

    def has_workflow_status(self) -> bool:
        return bool(self.workflow_status)

    def has_owner_transition(self) -> bool:
        return self.current_owner_agent_id is not None and self.previous_owner_agent_id is not None

    def is_terminal_workflow(self) -> bool:
        return self.workflow_status in {WorkflowStatus.COMPLETED.value, WorkflowStatus.FAILED.value}

    def has_blocked_reason(self) -> bool:
        return (
            self.workflow_status == WorkflowStatus.BLOCKED.value
            and self.stage_transition_reason_hash is not None
        )


@dataclass(frozen=True)
class WorkflowStageModel:
    workflow_id: str
    stage_names: list[str]
    allowed_transitions: dict[str, list[str]]
    terminal_stages: set[str]
    retry_stages: set[str]
    escalation_stages: set[str]

    @classmethod
    def create(
        cls,
        workflow_id: str,
        stage_names: list[str],
        allowed_transitions: dict[str, list[str]],
        terminal_stages: set[str] | None = None,
        retry_stages: set[str] | None = None,
        escalation_stages: set[str] | None = None,
    ) -> "WorkflowStageModel":
        return cls(
            workflow_id=workflow_id,
            stage_names=list(stage_names),
            allowed_transitions={key: list(value) for key, value in allowed_transitions.items()},
            terminal_stages=set(terminal_stages or set()),
            retry_stages=set(retry_stages or set()),
            escalation_stages=set(escalation_stages or set()),
        )

    def is_valid_transition(self, from_stage: str, to_stage: str) -> bool:
        return to_stage in self.allowed_transitions.get(from_stage, [])

    def is_terminal_stage(self, stage: str) -> bool:
        return stage in self.terminal_stages

    def is_retry_stage(self, stage: str) -> bool:
        return stage in self.retry_stages

    def is_escalation_stage(self, stage: str) -> bool:
        return stage in self.escalation_stages


class WorkflowVisualizationRegistry:
    _instance: "WorkflowVisualizationRegistry | None" = None
    _singleton_lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, WorkflowVisualizationRecord] = {}
        self._run_index: dict[str, list[str]] = {}
        self._workflow_index: dict[str, list[str]] = {}
        self._status_index: dict[str, list[str]] = {}
        self._stage_models: dict[str, WorkflowStageModel] = {}
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> "WorkflowVisualizationRegistry":
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: WorkflowVisualizationRecord) -> WorkflowVisualizationRecord:
        with self._lock:
            self._records[record.workflow_visualization_id] = record
            self._run_index.setdefault(record.run_id, []).append(record.workflow_visualization_id)
            self._workflow_index.setdefault(record.workflow_id, []).append(record.workflow_visualization_id)
            self._status_index.setdefault(record.workflow_status, []).append(record.workflow_visualization_id)
        return record

    def register_stage_model(self, model: WorkflowStageModel) -> None:
        with self._lock:
            self._stage_models[model.workflow_id] = model

    def get_stage_model(self, workflow_id: str) -> WorkflowStageModel | None:
        with self._lock:
            return self._stage_models.get(workflow_id)

    def query_by_record_id(self, record_id: str) -> WorkflowVisualizationRecord | None:
        with self._lock:
            return self._records.get(record_id)

    def query_by_run_id(self, run_id: str) -> list[WorkflowVisualizationRecord]:
        with self._lock:
            return [self._records[rid] for rid in self._run_index.get(run_id, []) if rid in self._records]

    def query_by_workflow_id(self, workflow_id: str) -> list[WorkflowVisualizationRecord]:
        with self._lock:
            return [
                self._records[rid]
                for rid in self._workflow_index.get(workflow_id, [])
                if rid in self._records
            ]

    def query_by_status(self, status: WorkflowStatus | str) -> list[WorkflowVisualizationRecord]:
        status_value = status.value if isinstance(status, WorkflowStatus) else str(status)
        with self._lock:
            return [
                self._records[rid] for rid in self._status_index.get(status_value, []) if rid in self._records
            ]


def get_workflow_visualization_registry() -> WorkflowVisualizationRegistry:
    return WorkflowVisualizationRegistry.get_instance()


def reset_workflow_visualization_registry() -> None:
    with WorkflowVisualizationRegistry._singleton_lock:
        WorkflowVisualizationRegistry._instance = None


__all__ = [
    "WorkflowStatus",
    "StageTransitionReason",
    "WorkflowVisualizationError",
    "WorkflowVisualizationRecord",
    "WorkflowStageModel",
    "WorkflowVisualizationRegistry",
    "get_workflow_visualization_registry",
    "reset_workflow_visualization_registry",
    "ACTIVE",
    "BLOCKED",
    "RETRYING",
    "ESCALATED",
    "COMPLETED",
    "FAILED",
    "NORMAL_TRANSITION",
    "RETRY_TRIGGERED",
    "ESCALATION_TRIGGERED",
    "BLOCK_DETECTED",
    "WORKFLOW_ERROR",
]
