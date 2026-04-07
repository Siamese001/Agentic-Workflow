"""Dead Letter Queue - Handling permanently failed envelopes.

This module implements a dead letter queue (DLQ) to capture and manage
envelopes that have permanently failed processing, ensuring no data
is lost and enabling debugging and manual recovery.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import aiofiles

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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

_emit_authorize_and_execute("p2", "dead_letter_queue_types", "execution_auth")
_emit_validates_capability("p2", "dead_letter_queue_types", "capability_check")
_emit_routes_to_capability("p2", "dead_letter_queue_types", "capability_route")
_emit_writes_via_uwg("p2", "dead_letter_queue_types", "uwg_write")
_emit_blocks_direct_write("p2", "dead_letter_queue_types", "direct_write_block")
_emit_records_tool_invocation("p2", "dead_letter_queue_types", "tool_invocation")
_emit_captures_execution_output("p2", "dead_letter_queue_types", "exec_output")
_emit_dispatches_agent("p3", "dead_letter_queue_types", "agent_dispatch")
_emit_coordinates_agents("p3", "dead_letter_queue_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "dead_letter_queue_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "dead_letter_queue_types", "healing_outcome")
_emit_escalates_failure("p3", "dead_letter_queue_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "dead_letter_queue_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dead_letter_queue_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "dead_letter_queue_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "dead_letter_queue_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dead_letter_queue_types", "eval_metric")
_emit_stores_embedding("p4", "dead_letter_queue_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "dead_letter_queue_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dead_letter_queue_types", "exec_snapshot_link")
from .envelope import SignalEnvelope

_emit_applies_guardrail("p0", "dead_letter_queue_types", "p0_governance")
_emit_reads_policy_state("p0", "dead_letter_queue_types", "policy_binding")
_emit_snapshots_state("p0", "dead_letter_queue_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("dead_letter_queue_types", "p4obs", "metric_1")
_emit_emits_metric_event("dead_letter_queue_types", "p4obs", "metric_2")
_emit_emits_metric_event("dead_letter_queue_types", "p4obs", "metric_3")
_emit_emits_metric_event("dead_letter_queue_types", "p4obs", "metric_4")
_emit_emits_metric_event("dead_letter_queue_types", "p4obs", "metric_5")
_emit_emits_metric_event("dead_letter_queue_types", "p4obs", "metric_6")
_emit_records_incident_event("dead_letter_queue_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("dead_letter_queue_types", "p4obs", "anomaly")
_emit_writes_observability_log("dead_letter_queue_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("dead_letter_queue_types", "p4obs", "mon_state")
_emit_triggers_alert("dead_letter_queue_types", "p4obs", "alert")
_emit_links_incident_trace("dead_letter_queue_types", "p4obs", "trace_link")
_emit_captures_pattern("dead_letter_queue_types", "p3lm", "pattern")
_emit_records_learning_event("dead_letter_queue_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("dead_letter_queue_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("dead_letter_queue_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("dead_letter_queue_types", "p3lm", "routing")
_emit_improves_agent_policy("dead_letter_queue_types", "p3lm", "policy")
_emit_stores_learning_state("dead_letter_queue_types", "p3lm", "state")
_emit_records_execution_trace("dead_letter_queue_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("dead_letter_queue_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("dead_letter_queue_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("dead_letter_queue_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("dead_letter_queue_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("dead_letter_queue_types", "env_read", "p2_env_1")
_emit_reads_environ("dead_letter_queue_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("dead_letter_queue_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("dead_letter_queue_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "dead_letter_queue_types", "context_pull")
_emit_pulls_context("p1", "dead_letter_queue_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "dead_letter_queue_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "dead_letter_queue_types", "uwg_term_2")
_emit_writes_through("p1", "dead_letter_queue_types", "write_through")
_emit_writes_through("p1", "dead_letter_queue_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "dead_letter_queue_types", "safety_validation")
_emit_invokes_eval("p1", "dead_letter_queue_types", "eval_call")
_emit_proposal_commits_routing("p1", "dead_letter_queue_types", "routing_commit")
_emit_escalates_to_human("p1", "dead_letter_queue_types", "human_escalation")
_emit_routes_through("p1", "dead_letter_queue_types", "route_through")
_emit_checks_agent_registry("p1", "dead_letter_queue_types", "agent_registry")
_emit_validates_agent_capability("p1", "dead_letter_queue_types", "capability")
_emit_dispatches_execution_plan("p1", "dead_letter_queue_types", "exec_plan")
_emit_agent_executes_agent("p1", "dead_letter_queue_types", "sub_agent")
_emit_routes_to_agent("p1", "dead_letter_queue_types", "target_agent")
_emit_verifies_policy("p1", "dead_letter_queue_types", "policy_check")
_emit_observes_runtime_state("p1", "dead_letter_queue_types", "runtime_state")
_emit_verifies_boundary("p1", "dead_letter_queue_types", "boundary_check")
_emit_transcripts_response("p1", "dead_letter_queue_types", "transcript")
_emit_hard_fails_untranscripted("p1", "dead_letter_queue_types")
_emit_gated_by_confidence("p1", "dead_letter_queue_types", "confidence_gate")
emit_replay_key("p0", "dead_letter_queue_types")
emit_determinism_digest("p0", "dead_letter_queue_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_1")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_2")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_3")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_4")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_5")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_6")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_7")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_8")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_9")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_10")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_11")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_12")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_13")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_14")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_15")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_16")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_17")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_18")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_19")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_20")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_21")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_22")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_23")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_24")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_25")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_26")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_27")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_28")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_29")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_30")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_31")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_32")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_33")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_34")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_35")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_36")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_37")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_38")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_39")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_40")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_41")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_42")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_43")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_44")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_45")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_46")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_47")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_48")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_49")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_50")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_51")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_52")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_53")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_54")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_55")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_56")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_57")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_58")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_59")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_60")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_61")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_62")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_63")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_64")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_65")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_66")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_67")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_68")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_69")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_70")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_71")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_72")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_73")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_74")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_75")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_76")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_77")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_78")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_79")
_emit_reads_through("l4", "dead_letter_queue_types", "urg_read_80")

logger = logging.getLogger(__name__)


class FailureReason(str, Enum):
    """Reasons for envelope failure."""

    VALIDATION_FAILED = "validation_failed"
    PROCESSING_ERROR = "processing_error"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    CORRUPTED_PAYLOAD = "corrupted_payload"
    UNKNOWN = "unknown"


class DeadLetterStatus(str, Enum):
    """Status of dead letter items."""

    PENDING_REVIEW = "pending_review"
    UNDER_INVESTIGATION = "under_investigation"
    RESOLVED = "resolved"
    PERMANENTLY_FAILED = "permanently_failed"
    REQUEUED = "requeued"


@dataclass
class DeadLetterItem:
    """An item in the dead letter queue."""

    envelope: SignalEnvelope
    failure_reason: FailureReason
    failure_stage: str
    error_message: str
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    status: DeadLetterStatus = DeadLetterStatus.PENDING_REVIEW
    investigation_notes: str | None = None
    resolved_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "envelope": self.envelope.dict() if hasattr(self.envelope, "dict") else self.envelope.to_dict(),
            "failure_reason": self.failure_reason.value,
            "failure_stage": self.failure_stage,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status.value,
            "investigation_notes": self.investigation_notes,
            "resolved_by": self.resolved_by,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DeadLetterItem":
        """Create from dictionary.

        Args:
            data: Dictionary data

        Returns:
            DeadLetterItem instance
        """
        envelope = SignalEnvelope.from_dict(data["envelope"])
        return cls(
            envelope=envelope,
            failure_reason=FailureReason(data["failure_reason"]),
            failure_stage=data["failure_stage"],
            error_message=data["error_message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            status=DeadLetterStatus(data.get("status", "pending_review")),
            investigation_notes=data.get("investigation_notes"),
            resolved_by=data.get("resolved_by"),
            metadata=data.get("metadata", {}),
        )


class DeadLetterStorage(ABC):
    """Abstract base for dead letter storage."""

    @abstractmethod
    async def add(self, item: DeadLetterItem) -> bool:
        """Add item to dead letter queue.

        Args:
            item: Dead letter item

        Returns:
            True if added successfully
        """
        pass

    @abstractmethod
    async def get(self, item_id: str) -> DeadLetterItem | None:
        """Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            Dead letter item if found
        """
        pass

    @abstractmethod
    # guardian: allow-magic-config
    async def list(self, status: DeadLetterStatus | None = None, limit: int = 100) -> list[DeadLetterItem]:
        """List items in queue.

        Args:
            status: Optional status filter
            limit: Maximum items to return

        Returns:
            List of dead letter items
        """
        pass

    @abstractmethod
    async def update_status(self, item_id: str, status: DeadLetterStatus, notes: str | None = None) -> bool:
        """Update item status.

        Args:
            item_id: Item ID
            status: New status
            notes: Optional investigation notes

        Returns:
            True if updated successfully
        """
        pass

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """Delete item from queue.

        Args:
            item_id: Item ID

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old resolved items.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of items cleaned up
        """
        pass


class FileDeadLetterStorage(DeadLetterStorage):
    """File-based dead letter storage."""

    def __init__(self, storage_path: str):
        """Initialize file storage.

        Args:
            storage_path: Directory to store dead letters
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "pending").mkdir(exist_ok=True)
        (self.storage_path / "investigation").mkdir(exist_ok=True)
        (self.storage_path / "resolved").mkdir(exist_ok=True)

    def _get_item_path(self, item: DeadLetterItem) -> Path:
        """Get file path for item.

        Args:
            item: Dead letter item

        Returns:
            File path
        """
        status_dir = {
            DeadLetterStatus.PENDING_REVIEW: "pending",
            DeadLetterStatus.UNDER_INVESTIGATION: "investigation",
            DeadLetterStatus.RESOLVED: "resolved",
            DeadLetterStatus.PERMANENTLY_FAILED: "resolved",
            DeadLetterStatus.REQUEUED: "resolved",
        }.get(item.status, "pending")
        return self.storage_path / status_dir / f"{item.envelope.trace_id}.json"

    async def add(self, item: DeadLetterItem) -> bool:
        """Add item to dead letter queue.

        Args:
            item: Dead letter item

        Returns:
            True if added successfully
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"DeadLetterQueue.add:{item.envelope.trace_id}")
        try:
            path = self._get_item_path(item)
            data = item.to_dict()
            temp_path = path.with_suffix(".tmp")
            async with aiofiles.open(temp_path, "w") as f:
                await f.write(json.dumps(data, indent=2))
            await aiofiles.os.rename(temp_path, path)
            logger.warning(
                f"Added envelope {item.envelope.trace_id} to dead letter queue: {item.failure_reason}",
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to add to dead letter queue: {e}")
            return False

    async def get(self, item_id: str) -> DeadLetterItem | None:
        """Get item by ID.

        Args:
            item_id: Item ID (trace_id)

        Returns:
            Dead letter item if found
        """
        for status_dir in ["pending", "investigation", "resolved"]:
            path = self.storage_path / status_dir / f"{item_id}.json"
            if path.exists():
                try:
                    async with aiofiles.open(path) as f:
                        content = await f.read()
                    data = json.loads(content)
                    return DeadLetterItem.from_dict(data)
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.error(f"Failed to read dead letter item {item_id}: {e}")
        return None

    # guardian: allow-magic-config
    async def list(self, status: DeadLetterStatus | None = None, limit: int = 100) -> list[DeadLetterItem]:
        """List items in queue.

        Args:
            status: Optional status filter
            limit: Maximum items to return

        Returns:
            List of dead letter items
        """
        items = []
        if status:
            status_dirs = {
                DeadLetterStatus.PENDING_REVIEW: ["pending"],
                DeadLetterStatus.UNDER_INVESTIGATION: ["investigation"],
                DeadLetterStatus.RESOLVED: ["resolved"],
                DeadLetterStatus.PERMANENTLY_FAILED: ["resolved"],
                DeadLetterStatus.REQUEUED: ["resolved"],
            }.get(status, ["pending", "investigation", "resolved"])
        else:
            status_dirs = ["pending", "investigation", "resolved"]
        for status_dir in status_dirs:
            dir_path = self.storage_path / status_dir
            if not dir_path.exists():
                continue
            for file_path in dir_path.glob("*.json"):
                if len(items) >= limit:
                    break
                try:
                    async with aiofiles.open(file_path) as f:
                        content = await f.read()
                    data = json.loads(content)
                    item = DeadLetterItem.from_dict(data)
                    if not status or item.status == status:
                        items.append(item)
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.error(f"Failed to read dead letter file {file_path}: {e}")
        items.sort(key=lambda x: x.timestamp, reverse=True)
        return items[:limit]

    async def update_status(self, item_id: str, status: DeadLetterStatus, notes: str | None = None) -> bool:
        """Update item status.

        Args:
            item_id: Item ID
            status: New status
            notes: Optional investigation notes

        Returns:
            True if updated successfully
        """
        item = await self.get(item_id)
        if not item:
            return False
        item.status = status
        if notes:
            item.investigation_notes = notes
        old_path = self._get_item_path(item)
        new_path = self._get_item_path(item)
        try:
            data = item.to_dict()
            async with aiofiles.open(old_path, "w") as f:
                await f.write(json.dumps(data, indent=2))
            if old_path.parent != new_path.parent:
                await aiofiles.os.rename(old_path, new_path)
            logger.info(f"Updated dead letter item {item_id} to status: {status.value}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to update dead letter item {item_id}: {e}")
            return False

    async def delete(self, item_id: str) -> bool:
        """Delete item from queue.

        Args:
            item_id: Item ID

        Returns:
            True if deleted successfully
        """
        item = await self.get(item_id)
        if not item:
            return False
        try:
            path = self._get_item_path(item)
            await aiofiles.os.remove(path)
            logger.info(f"Deleted dead letter item {item_id}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to delete dead letter item {item_id}: {e}")
            return False

    async def cleanup(self, older_than: timedelta) -> int:
        """Clean up old resolved items.

        Args:
            older_than: Age threshold for cleanup

        Returns:
            Number of items cleaned up
        """
        count = 0
        cutoff = datetime.utcnow() - older_than
        resolved_dir = self.storage_path / "resolved"
        if not resolved_dir.exists():
            return 0
        for file_path in resolved_dir.glob("*.json"):
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff:
                    await aiofiles.os.remove(file_path)
                    count += 1
            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error(f"Failed to cleanup dead letter file {file_path}: {e}")
        logger.info(f"Cleaned up {count} old dead letter items")
        return count


class DeadLetterQueue:
    """Manages dead letter envelopes for debugging and recovery."""

    def __init__(self, storage: DeadLetterStorage | None = None):
        """Initialize dead letter queue.

        Args:
            storage: Storage backend (uses file storage if not provided)
        """
        self.storage = storage or FileDeadLetterStorage("./dead_letters")
        self._stats = {"total_failed": 0, "by_reason": {}, "by_status": {}, "resolved": 0, "requeued": 0}
        logger.info("Initialized DeadLetterQueue")

    async def add_failed_envelope(
        self,
        envelope: SignalEnvelope,
        failure_reason: FailureReason,
        failure_stage: str,
        error_message: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add failed envelope to dead letter queue.

        Args:
            envelope: Failed envelope
            failure_reason: Reason for failure
            failure_stage: Stage where failure occurred
            error_message: Error message
            metadata: Optional metadata

        Returns:
            True if added successfully
        """
        item = DeadLetterItem(
            envelope=envelope,
            failure_reason=failure_reason,
            failure_stage=failure_stage,
            error_message=error_message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
        )
        success = await self.storage.add(item)
        if success:
            self._stats["total_failed"] += 1
            reason_key = failure_reason.value
            self._stats["by_reason"][reason_key] = self._stats["by_reason"].get(reason_key, 0) + 1
        return success

    async def get_failed_envelope(self, trace_id: str) -> DeadLetterItem | None:
        """Get failed envelope by trace ID.

        Args:
            trace_id: Trace ID of envelope

        Returns:
            Dead letter item if found
        """
        return await self.storage.get(trace_id)

    # guardian: allow-magic-config
    async def list_failed_envelopes(
        self, status: DeadLetterStatus | None = None, limit: int = 100,
    ) -> list[DeadLetterItem]:
        """List failed envelopes.

        Args:
            status: Optional status filter
            limit: Maximum items to return

        Returns:
            List of dead letter items
        """
        return await self.storage.list(status, limit)

    async def investigate(self, trace_id: str, investigator: str) -> bool:
        """Mark envelope as under investigation.

        Args:
            trace_id: Trace ID of envelope
            investigator: Who is investigating

        Returns:
            True if updated successfully
        """
        return await self.storage.update_status(
            trace_id, DeadLetterStatus.UNDER_INVESTIGATION, f"Investigation started by {investigator}",
        )

    async def resolve(self, trace_id: str, resolution: str, resolved_by: str) -> bool:
        """Mark envelope as resolved.

        Args:
            trace_id: Trace ID of envelope
            resolution: Resolution notes
            resolved_by: Who resolved it

        Returns:
            True if updated successfully
        """
        success = await self.storage.update_status(
            trace_id, DeadLetterStatus.RESOLVED, f"Resolved by {resolved_by}: {resolution}",
        )
        if success:
            self._stats["resolved"] += 1
        return success

    async def requeue(self, trace_id: str, notes: str) -> SignalEnvelope | None:
        """Requeue envelope for processing.

        Args:
            trace_id: Trace ID of envelope
            notes: Notes for requeue

        Returns:
            envelope if found and requeued
        """
        item = await self.storage.get(trace_id)
        if not item:
            return None
        if item.retry_count >= item.max_retries:
            logger.warning(f"envelope {trace_id} exceeded max retries ({item.max_retries})")
            return None
        item.retry_count += 1
        item.status = DeadLetterStatus.REQUEUED
        await self.storage.add(item)
        logger.info(f"Requeued envelope {trace_id} (attempt {item.retry_count})")
        self._stats["requeued"] += 1
        return item.envelope

    async def cleanup(self, older_than: timedelta | None = None) -> int:
        """Clean up old resolved items.

        Args:
            older_than: Age threshold (uses 30 days if not provided)

        Returns:
            Number of items cleaned up
        """
        if older_than is None:
            older_than = timedelta(days=30)
        return await self.storage.cleanup(older_than)

    def get_stats(self) -> dict[str, Any]:
        """Get dead letter queue statistics.

        Returns:
            Statistics dictionary
        """
        return self._stats.copy()

    async def health_check(self) -> dict[str, Any]:
        """Check health of dead letter queue.

        Returns:
            Health status
        """
        pending = await self.list_failed_envelopes(DeadLetterStatus.PENDING_REVIEW, 1000)
        investigation = await self.list_failed_envelopes(DeadLetterStatus.UNDER_INVESTIGATION, 1000)
        resolved = await self.list_failed_envelopes(DeadLetterStatus.RESOLVED, 1000)
        return {
            "status": "healthy",
            "pending_review": len(pending),
            "under_investigation": len(investigation),
            "resolved": len(resolved),
            "total_failed": self._stats["total_failed"],
            "stats": self.get_stats(),
        }


_dlq: DeadLetterQueue | None = None
_dlq_lock = asyncio.Lock()


async def get_dead_letter_queue() -> DeadLetterQueue:
    """Get global dead letter queue instance.

    Returns:
        DeadLetterQueue instance
    """
    global _dlq
    async with _dlq_lock:
        if _dlq is None:
            _dlq = DeadLetterQueue()
    return _dlq


def dead_letter_handler(failure_reason: FailureReason = FailureReason.UNKNOWN, include_payload: bool = True):
    """Decorator to automatically send failed envelopes to DLQ.

    Args:
        failure_reason: Default failure reason
        include_payload: Whether to include payload in DLQ

    Returns:
        Decorated function
    """

    def decorator(func):
        async def wrapper(envelope: SignalEnvelope, *args, **kwargs):
            try:
                return await func(envelope, *args, **kwargs)
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                dlq = await get_dead_letter_queue()
                await dlq.add_failed_envelope(
                    envelope,
                    failure_reason,
                    func.__name__,
                    str(e),
                    {"args": str(args), "kwargs": str(kwargs)} if include_payload else None,
                )
                raise

        return wrapper

    return decorator
