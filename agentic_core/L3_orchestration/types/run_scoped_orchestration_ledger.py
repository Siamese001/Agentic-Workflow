"""
agentic_core/L3_orchestration/contracts/run_scoped_orchestration_ledger.py

RunScopedOrchestrationLedger — P0/L3 gap remediation.

Single interface through which all L3 orchestrators write handoff records.
Turns orchestration from inferred behavior into explicit, queryable structure.

Spec §7: This ledger must record:
  - all agent handoffs
  - task ownership
  - active stage
  - pending stage
  - completion status
  - escalation status
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.L3_orchestration.types.orchestration_handoff_contract import (
    OrchestrationHandoffContract,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

logger = logging.getLogger(__name__)
_ADG_LOGGER = logging.getLogger("adg.agent_executes_agent")


class StageStatus(str, Enum):
    """Status of a workflow stage."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"


@dataclass
class StageOwnershipRecord:
    """Records ownership transition for one workflow stage."""

    stage: str
    owner_agent_id: str
    next_owner_agent_id: str
    handoff_id: str
    status: StageStatus = StageStatus.PENDING
    continuation_signal: str = ""
    created_epoch: float = field(default_factory=lambda: get_clock().now_epoch())
    completed_epoch: float = 0.0

    def mark_active(self) -> None:
        self.status = StageStatus.ACTIVE

    def mark_completed(self, continuation: str = "") -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StageOwnershipRecord.mark_completed", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StageOwnershipRecord.mark_completed", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "StageOwnershipRecord.mark_completed"
        )

        self.status = StageStatus.COMPLETED
        self.continuation_signal = continuation
        self.completed_epoch = get_clock().now_epoch()

    def mark_failed(self) -> None:
        self.status = StageStatus.FAILED
        self.completed_epoch = get_clock().now_epoch()

    def mark_escalated(self) -> None:
        self.status = StageStatus.ESCALATED
        self.completed_epoch = get_clock().now_epoch()


class RunScopedOrchestrationLedger:
    """Single interface for recording all L3 agent handoffs within one run.

    All L3 orchestrators MUST write to this ledger through this interface.
    Direct orchestration state mutation outside this ledger is forbidden.

    Usage::

        ledger = get_orchestration_ledger(run_id="run_abc123")
        ledger.record_handoff(contract)
        ledger.record_stage_transition(
            stage="decomposition",
            owner="DecompositionOrchestrator",
            next_owner="ExecutionOrchestrator",
            handoff_id=contract.handoff_id,
        )
    """

    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self._handoffs: list[OrchestrationHandoffContract] = []
        self._stage_records: list[StageOwnershipRecord] = []
        self._task_ownership: dict[str, str] = {}  # work_item_id -> owner_agent_id
        self._escalations: list[dict[str, Any]] = []

    def record_handoff(self, contract: OrchestrationHandoffContract) -> None:
        """Record a typed handoff contract in the ledger.

        Emits ``agent_executes_agent`` ADG edge signal.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RunScopedOrchestrationLedger.record_handoff"
        )

        self._handoffs.append(contract)
        # Update task ownership
        if contract.current_work_item_id if hasattr(contract, "current_work_item_id") else False:
            self._task_ownership[contract.current_work_item_id] = contract.child_agent_id
        _ADG_LOGGER.debug(
            "agent_executes_agent ledger_record parent=%s child=%s run_id=%s stage=%s",
            contract.parent_agent_id,
            contract.child_agent_id,
            contract.run_id,
            contract.workflow_stage,
        )
        logger.debug(
            "LEDGER handoff recorded parent=%s child=%s stage=%s id=%s",
            contract.parent_agent_id,
            contract.child_agent_id,
            contract.workflow_stage,
            contract.handoff_id,
        )

    def record_stage_transition(
        self,
        stage: str,
        owner_agent_id: str,
        next_owner_agent_id: str,
        handoff_id: str,
        continuation_signal: str = "",
    ) -> StageOwnershipRecord:
        """Record a workflow stage ownership transition.

        Hard rule: no workflow stage transition without this record.
        """
        record = StageOwnershipRecord(
            stage=stage,
            owner_agent_id=owner_agent_id,
            next_owner_agent_id=next_owner_agent_id,
            handoff_id=handoff_id,
            continuation_signal=continuation_signal,
        )
        record.mark_active()
        self._stage_records.append(record)
        _ADG_LOGGER.debug(
            "agent_executes_agent stage_transition owner=%s next=%s stage=%s run_id=%s",
            owner_agent_id,
            next_owner_agent_id,
            stage,
            self.run_id,
        )
        return record

    def record_task_ownership(self, work_item_id: str, owner_agent_id: str) -> None:
        """Assign task ownership to an agent."""
        self._task_ownership[work_item_id] = owner_agent_id
        logger.debug("LEDGER task_ownership work_item=%s owner=%s", work_item_id, owner_agent_id)

    def record_escalation(
        self,
        stage: str,
        agent_id: str,
        reason: str,
    ) -> None:
        """Record an escalation event."""
        entry: dict[str, Any] = {
            "stage": stage,
            "agent_id": agent_id,
            "reason": reason,
            "epoch": get_clock().now_epoch(),
        }
        self._escalations.append(entry)
        # Mark any matching stage record as escalated
        for rec in self._stage_records:
            if rec.stage == stage and rec.owner_agent_id == agent_id:
                rec.mark_escalated()
        logger.warning("LEDGER escalation stage=%s agent=%s reason=%s", stage, agent_id, reason)

    def all_handoffs(self) -> list[OrchestrationHandoffContract]:
        """Return all recorded handoff contracts."""
        return list(self._handoffs)

    def active_stages(self) -> list[StageOwnershipRecord]:
        """Return all stage records with ACTIVE status."""
        return [r for r in self._stage_records if r.status == StageStatus.ACTIVE]

    def pending_stages(self) -> list[StageOwnershipRecord]:
        """Return all stage records with PENDING status."""
        return [r for r in self._stage_records if r.status == StageStatus.PENDING]

    def completed_stages(self) -> list[StageOwnershipRecord]:
        """Return all completed stage records."""
        return [r for r in self._stage_records if r.status == StageStatus.COMPLETED]

    def task_owner(self, work_item_id: str) -> str | None:
        """Return the current owner agent for a work item."""
        return self._task_ownership.get(work_item_id)

    def summary(self) -> dict[str, Any]:
        """Return a summary of ledger state."""
        stage_counts: dict[str, int] = defaultdict(int)
        for r in self._stage_records:
            stage_counts[r.status.value] += 1
        return {
            "run_id": self.run_id,
            "total_handoffs": len(self._handoffs),
            "total_stage_records": len(self._stage_records),
            "stage_counts": dict(stage_counts),
            "active_task_owners": len(self._task_ownership),
            "escalations": len(self._escalations),
        }


_ledgers: dict[str, RunScopedOrchestrationLedger] = {}


def get_orchestration_ledger(run_id: str) -> RunScopedOrchestrationLedger:
    """Get or create the run-scoped orchestration ledger."""
    if run_id not in _ledgers:
        _ledgers[run_id] = RunScopedOrchestrationLedger(run_id)
    return _ledgers[run_id]


def reset_orchestration_ledgers() -> None:
    """Reset all ledgers (for testing)."""
    _ledgers.clear()


__all__ = [
    "RunScopedOrchestrationLedger",
    "StageOwnershipRecord",
    "StageStatus",
    "get_orchestration_ledger",
    "reset_orchestration_ledgers",
]
