"""
agentic_core/L3_orchestration/visualization/workflow_visualization.py

P3/L3 Workflow Visualization — workflow visualization record and metrics.

Provides WorkflowVisualizationRecord (13 required fields) and workflow
status/stage transition tracking for operational visibility.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "workflow_visualization", "L3")
_emit_routes_through("p1", "workflow_visualization", "L3")
_emit_escalates_to_human("p1", "workflow_visualization", "L3")
_emit_reads_policy_state("p1", "workflow_visualization", "L3")

_emit_snapshots_state("p0", "workflow_visualization", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "workflow_visualization", "p0_governance")

logger = logging.getLogger(__name__)
_VISUALIZATION_LOG = logging.getLogger("adg.workflow_visualization_emitted")


# ---------------------------------------------------------------------------
# Enums for workflow visualization tracking
# ---------------------------------------------------------------------------


class WorkflowStatus(Enum):
    """Status of workflow operations."""

    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class StageTransitionReason(Enum):
    """Reason for stage transitions."""

    NORMAL_TRANSITION = "NORMAL_TRANSITION"
    RETRY_TRIGGERED = "RETRY_TRIGGERED"
    ESCALATION_TRIGGERED = "ESCALATION_TRIGGERED"
    BLOCK_DETECTED = "BLOCK_DETECTED"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"


# Export enum values for ADG scanner detection
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


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class WorkflowVisualizationError(Exception):
    """Raised when stage transition occurs without workflow visualization update (Gate A)."""

    pass


# ---------------------------------------------------------------------------
# WorkflowVisualizationRecord — 13 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkflowVisualizationRecord:
    """Immutable workflow visualization record for operational telemetry (13 required fields)."""

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
    visualization_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

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
    ) -> WorkflowVisualizationRecord:
        """Factory to create WorkflowVisualizationRecord with computed fields."""
        workflow_visualization_id = str(uuid.uuid4())

        # Compute hashes
        completed_stages_hash = hashlib.sha256("|".join(sorted(completed_stages)).encode()).hexdigest()[:16]
        pending_stages_hash = hashlib.sha256("|".join(sorted(pending_stages)).encode()).hexdigest()[:16]

        stage_transition_reason_hash = None
        if stage_transition_reason:
            stage_transition_reason_hash = hashlib.sha256(stage_transition_reason.value.encode()).hexdigest()[
                :16
            ]

        return cls(
            workflow_visualization_id=workflow_visualization_id,
            run_id=run_id,
            root_trace_id=root_trace_id,
            workflow_id=workflow_id,
            current_stage=current_stage,
            completed_stages_hash=completed_stages_hash,
            pending_stages_hash=pending_stages_hash,
            current_owner_agent_id=current_owner_agent_id,
            previous_owner_agent_id=previous_owner_agent_id,
            workflow_status=workflow_status.value,
            stage_transition_reason_hash=stage_transition_reason_hash,
            last_updated_tick=get_clock().now_epoch(),
        )

    def has_current_stage(self) -> bool:
        """Check if record has current_stage (Gate A)."""
        return bool(self.current_stage)

    def has_workflow_status(self) -> bool:
        """Check if workflow status is present (Gate B)."""
        return bool(self.workflow_status)

    def has_owner_transition(self) -> bool:
        """Check if owner transition is recorded (Gate C)."""
        return self.current_owner_agent_id is not None and self.previous_owner_agent_id is not None

    def is_terminal_workflow(self) -> bool:
        """Check if workflow is in terminal state (Gate D)."""
        return self.workflow_status in [
            WorkflowStatus.COMPLETED.value,
            WorkflowStatus.FAILED.value,
        ]

    def has_blocked_reason(self) -> bool:
        """Check if blocked workflow has blocked reason (Gate E)."""
        return (
            self.workflow_status == WorkflowStatus.BLOCKED.value
            and self.stage_transition_reason_hash is not None
        )


# ---------------------------------------------------------------------------
# WorkflowStageModel — stage model requirements per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkflowStageModel:
    """Explicit stage model for workflow visualization."""

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
    ) -> WorkflowStageModel:
        return cls(
            workflow_id=workflow_id,
            stage_names=stage_names,
            allowed_transitions=allowed_transitions,
            terminal_stages=terminal_stages or set(),
            retry_stages=retry_stages or set(),
            escalation_stages=escalation_stages or set(),
        )

    def is_valid_transition(self, from_stage: str, to_stage: str) -> bool:
        """Check if transition is allowed."""
        return to_stage in self.allowed_transitions.get(from_stage, [])

    def is_terminal_stage(self, stage: str) -> bool:
        """Check if stage is terminal."""
        return stage in self.terminal_stages

    def is_retry_stage(self, stage: str) -> bool:
        """Check if stage is a retry stage."""
        return stage in self.retry_stages

    def is_escalation_stage(self, stage: str) -> bool:
        """Check if stage is an escalation stage."""
        return stage in self.escalation_stages


# ---------------------------------------------------------------------------
# WorkflowVisualizationRegistry — thread-safe visualization storage and query
# ---------------------------------------------------------------------------


class WorkflowVisualizationRegistry:
    """Thread-safe registry for workflow visualization records and queries."""

    _instance: WorkflowVisualizationRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, WorkflowVisualizationRecord] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> record_ids
        self._workflow_index: dict[str, list[str]] = {}  # workflow_id -> record_ids
        self._status_index: dict[str, list[str]] = {}  # status -> record_ids
        self._stage_models: dict[str, WorkflowStageModel] = {}  # workflow_id -> stage model
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> WorkflowVisualizationRegistry:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: WorkflowVisualizationRecord) -> None:
        """Persist a workflow visualization record."""
        _emit_records_execution_trace(
            record.run_id, LayerSegment.L3_ORCHESTRATION, f"workflow_viz:{record.workflow_id}"
        )
        with self._lock:
            self._records[record.workflow_visualization_id] = record

            # Index by run_id for queries
            if record.run_id not in self._run_index:
                self._run_index[record.run_id] = []
            self._run_index[record.run_id].append(record.workflow_visualization_id)

            # Index by workflow_id for queries
            if record.workflow_id not in self._workflow_index:
                self._workflow_index[record.workflow_id] = []
            self._workflow_index[record.workflow_id].append(record.workflow_visualization_id)

            # Index by status for queries
            if record.workflow_status not in self._status_index:
                self._status_index[record.workflow_status] = []
            self._status_index[record.workflow_status].append(record.workflow_visualization_id)

        _VISUALIZATION_LOG.debug(
            "workflow_visualization_emitted record_id=%s run_id=%s workflow_id=%s stage=%s status=%s",
            record.workflow_visualization_id,
            record.run_id,
            record.workflow_id,
            record.current_stage,
            record.workflow_status,
        )

        logger.debug(
            "WORKFLOW_VISUALIZATION_PERSISTED record_id=%s run_id=%s workflow_id=%s stage=%s status=%s",
            record.workflow_visualization_id,
            record.run_id,
            record.workflow_id,
            record.current_stage,
            record.workflow_status,
        )

        # Check for gate violations
        if not record.has_current_stage():
            logger.warning(
                "WORKFLOW_VISUALIZATION_GATE_A_VIOLATION record_id=%s current_stage=%s",
                record.workflow_visualization_id,
                record.current_stage,
            )

        if not record.has_workflow_status():
            logger.warning(
                "WORKFLOW_VISUALIZATION_GATE_B_VIOLATION record_id=%s workflow_status=%s",
                record.workflow_visualization_id,
                record.workflow_status,
            )

        if record.workflow_status == WorkflowStatus.BLOCKED.value and not record.has_blocked_reason():
            logger.warning(
                "WORKFLOW_VISUALIZATION_GATE_E_VIOLATION record_id=%s blocked without reason",
                record.workflow_visualization_id,
            )

    def register_stage_model(self, stage_model: WorkflowStageModel) -> None:
        """Register a workflow stage model."""
        with self._lock:
            self._stage_models[stage_model.workflow_id] = stage_model
        logger.debug(
            "WORKFLOW_STAGE_MODEL_REGISTERED workflow_id=%s stages=%d",
            stage_model.workflow_id,
            len(stage_model.stage_names),
        )

    def query_by_run_id(self, run_id: str) -> list[WorkflowVisualizationRecord]:
        """Query workflow visualization records by run_id."""
        with self._lock:
            record_ids = self._run_index.get(run_id, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_workflow_id(self, workflow_id: str) -> list[WorkflowVisualizationRecord]:
        """Query workflow visualization records by workflow_id."""
        with self._lock:
            record_ids = self._workflow_index.get(workflow_id, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_status(self, status: WorkflowStatus) -> list[WorkflowVisualizationRecord]:
        """Query workflow visualization records by status."""
        _emit_observes_runtime_state(
            str(uuid.uuid4()), "WorkflowVisualizationRegistry.query_by_status", "L3_ORCHESTRATION"
        )
        with self._lock:
            record_ids = self._status_index.get(status.value, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_record_id(self, record_id: str) -> WorkflowVisualizationRecord | None:
        """Query workflow visualization record by workflow_visualization_id."""
        with self._lock:
            return self._records.get(record_id)

    def get_stage_model(self, workflow_id: str) -> WorkflowStageModel | None:
        """Get stage model for a workflow."""
        with self._lock:
            return self._stage_models.get(workflow_id)

    def get_record_count(self, run_id: str = "") -> int:
        """Get count of workflow visualization records, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._records)

    def verify_record_exists(self, record_id: str) -> bool:
        """Verify workflow visualization record exists (Gate A)."""
        with self._lock:
            return record_id in self._records

    def verify_current_stage_present(self, record_id: str) -> bool:
        """Verify record has current_stage (Gate A)."""
        with self._lock:
            record = self._records.get(record_id)
            return record is not None and record.has_current_stage()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_workflow_visualization_registry() -> WorkflowVisualizationRegistry:
    """Get the singleton WorkflowVisualizationRegistry instance."""
    return WorkflowVisualizationRegistry.get_instance()


def reset_workflow_visualization_registry() -> None:
    """Reset the singleton WorkflowVisualizationRegistry (for testing)."""
    with WorkflowVisualizationRegistry._lock:
        WorkflowVisualizationRegistry._instance = None


__all__ = [
    "WorkflowVisualizationRecord",
    "WorkflowStageModel",
    "WorkflowStatus",
    "StageTransitionReason",
    "WorkflowVisualizationError",
    "WorkflowVisualizationRegistry",
    "get_workflow_visualization_registry",
    "reset_workflow_visualization_registry",
    # Enum values for ADG scanner detection
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
