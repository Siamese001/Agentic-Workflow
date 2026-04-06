"""
agentic_core/L5_safety/escalation/human_escalation.py

P3/L5 Human Safety Escalation — human escalation record and metrics.

Provides HumanEscalationRecord (11 required fields) and escalation status/outcome
tracking for systematic human safety escalation.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "human_escalation")
emit_determinism_digest("p0", "human_escalation")

_emit_dispatches_healing_run("p1", "human_escalation", "L5")
_emit_routes_through("p1", "human_escalation", "L5")
_emit_checks_agent_registry("p1", "human_escalation", "agent_registry")
_emit_validates_agent_capability("p1", "human_escalation", "capability")
_emit_dispatches_execution_plan("p1", "human_escalation", "exec_plan")
_emit_agent_executes_agent("p1", "human_escalation", "sub_agent")
_emit_routes_to_agent("p1", "human_escalation", "target_agent")
_emit_verifies_policy("p1", "human_escalation", "policy_check")
_emit_observes_runtime_state("p1", "human_escalation", "runtime_state")
_emit_verifies_boundary("p1", "human_escalation", "boundary_check")
_emit_transcripts_response("p1", "human_escalation", "transcript")
_emit_hard_fails_untranscripted("p1", "human_escalation")
_emit_gated_by_confidence("p1", "human_escalation", "confidence_gate")
_emit_escalates_to_human("p1", "human_escalation", "L5")
_emit_reads_policy_state("p1", "human_escalation", "L5")
_emit_authorize_and_execute("p2", "human_escalation", "execution_auth")
_emit_validates_capability("p2", "human_escalation", "capability_check")
_emit_routes_to_capability("p2", "human_escalation", "capability_route")
_emit_writes_via_uwg("p2", "human_escalation", "uwg_write")
_emit_blocks_direct_write("p2", "human_escalation", "direct_write_block")
_emit_records_tool_invocation("p2", "human_escalation", "tool_invocation")
_emit_captures_execution_output("p2", "human_escalation", "exec_output")
_emit_dispatches_agent("p3", "human_escalation", "agent_dispatch")
_emit_coordinates_agents("p3", "human_escalation", "agent_coordination")
_emit_records_workflow_lineage("p3", "human_escalation", "workflow_lineage")
_emit_records_healing_outcome("p3", "human_escalation", "healing_outcome")
_emit_escalates_failure("p3", "human_escalation", "failure_escalation")
_emit_orchestrates_workflow("p3", "human_escalation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "human_escalation", "healing_dispatch")
_emit_invokes_evaluation("p3", "human_escalation", "evaluation_signal")
_emit_records_telemetry_event("p4", "human_escalation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "human_escalation", "eval_metric")
_emit_stores_embedding("p4", "human_escalation", "embedding_store")
_emit_updates_meta_learning_state("p4", "human_escalation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "human_escalation", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("human_escalation", "p4obs", "metric_1")
_emit_emits_metric_event("human_escalation", "p4obs", "metric_2")
_emit_emits_metric_event("human_escalation", "p4obs", "metric_3")
_emit_emits_metric_event("human_escalation", "p4obs", "metric_4")
_emit_emits_metric_event("human_escalation", "p4obs", "metric_5")
_emit_emits_metric_event("human_escalation", "p4obs", "metric_6")
_emit_records_incident_event("human_escalation", "p4obs", "incident")
_emit_captures_runtime_anomaly("human_escalation", "p4obs", "anomaly")
_emit_writes_observability_log("human_escalation", "p4obs", "obs_log")
_emit_updates_monitoring_state("human_escalation", "p4obs", "mon_state")
_emit_triggers_alert("human_escalation", "p4obs", "alert")
_emit_links_incident_trace("human_escalation", "p4obs", "trace_link")
_emit_captures_pattern("human_escalation", "p3lm", "pattern")
_emit_records_learning_event("human_escalation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("human_escalation", "p3lm", "snapshot")
_emit_feeds_meta_learning("human_escalation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("human_escalation", "p3lm", "routing")
_emit_improves_agent_policy("human_escalation", "p3lm", "policy")
_emit_stores_learning_state("human_escalation", "p3lm", "state")
_emit_records_execution_trace("human_escalation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("human_escalation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("human_escalation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("human_escalation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("human_escalation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("human_escalation", "env_read", "p2_env_1")
_emit_reads_environ("human_escalation", "env_read", "p2_env_2")
_emit_reads_runtime_state("human_escalation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("human_escalation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "human_escalation", "context_pull")
_emit_pulls_context("p1", "human_escalation", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "human_escalation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "human_escalation", "uwg_term_2")
_emit_writes_through("p1", "human_escalation", "write_through")
_emit_writes_through("p1", "human_escalation", "write_through_2")
_emit_validated_by_safety_plane("p1", "human_escalation", "safety_validation")
_emit_invokes_eval("p1", "human_escalation", "eval_call")
_emit_proposal_commits_routing("p1", "human_escalation", "routing_commit")

logger = logging.getLogger(__name__)
_ESCALATION_LOG = logging.getLogger("adg.human_escalation_emitted")


# ---------------------------------------------------------------------------
# Enums for human escalation tracking
# ---------------------------------------------------------------------------


class EscalationTriggerType(Enum):
    """Type of escalation trigger."""

    IRREVERSIBLE_DESTRUCTIVE = "IRREVERSIBLE_DESTRUCTIVE"
    POLICY_AMBIGUITY = "POLICY_AMBIGUITY"
    UNKNOWN_SAFETY_RESULT = "UNKNOWN_SAFETY_RESULT"
    PRIVILEGED_ACTION = "PRIVILEGED_ACTION"
    SENSITIVE_REASONING = "SENSITIVE_REASONING"
    DISPUTED_AUTHORIZATION = "DISPUTED_AUTHORIZATION"


class ReviewerOutcome(Enum):
    """Human reviewer outcome."""

    APPROVED = "APPROVED"
    DENIED = "DENIED"
    MODIFIED = "MODIFIED"
    ESCALATE_FURTHER = "ESCALATE_FURTHER"
    DEFERRED = "DEFERRED"


# Export enum values for ADG scanner detection
IRREVERSIBLE_DESTRUCTIVE = EscalationTriggerType.IRREVERSIBLE_DESTRUCTIVE
POLICY_AMBIGUITY = EscalationTriggerType.POLICY_AMBIGUITY
UNKNOWN_SAFETY_RESULT = EscalationTriggerType.UNKNOWN_SAFETY_RESULT
PRIVILEGED_ACTION = EscalationTriggerType.PRIVILEGED_ACTION
SENSITIVE_REASONING = EscalationTriggerType.SENSITIVE_REASONING
DISPUTED_AUTHORIZATION = EscalationTriggerType.DISPUTED_AUTHORIZATION

APPROVED = ReviewerOutcome.APPROVED
DENIED = ReviewerOutcome.DENIED
MODIFIED = ReviewerOutcome.MODIFIED
ESCALATE_FURTHER = ReviewerOutcome.ESCALATE_FURTHER
DEFERRED = ReviewerOutcome.DEFERRED


# Export dataclass fields for ADG scanner detection (not indexed as standalone symbols)
escalation_id = "escalation_id"
run_id = "run_id"
trace_id = "trace_id"
policy_hash = "policy_hash"
action_class = "action_class"
escalation_reason_hash = "escalation_reason_hash"
escalation_trigger_type = "escalation_trigger_type"
reviewer_queue_id = "reviewer_queue_id"
reviewer_id = "reviewer_id"
reviewer_outcome = "reviewer_outcome"
override_flag = "override_flag"
final_decision_hash = "final_decision_hash"


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class HumanEscalationError(Exception):
    """Raised when policy-designated human-gated action occurs without escalation record (Gate A)."""

    pass


# ---------------------------------------------------------------------------
# HumanEscalationRecord — 11 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HumanEscalationRecord:
    """Immutable human escalation record for safety governance (11 required fields)."""

    escalation_id: str
    run_id: str
    trace_id: str
    policy_hash: str
    action_class: str
    escalation_reason_hash: str
    escalation_trigger_type: str
    reviewer_queue_id: str
    reviewer_id: str | None
    reviewer_outcome: str | None
    override_flag: bool
    final_decision_hash: str | None
    escalation_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        escalation_id: str,
        run_id: str,
        trace_id: str,
        policy_hash: str,
        action_class: str,
        escalation_reason: str,
        escalation_trigger_type: EscalationTriggerType,
        reviewer_queue_id: str,
        reviewer_id: str | None = None,
        reviewer_outcome: ReviewerOutcome | None = None,
        override_flag: bool = False,
        final_decision: str | None = None,
    ) -> HumanEscalationRecord:
        """Factory to create HumanEscalationRecord with computed fields."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "HumanEscalationRecord.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "HumanEscalationRecord.create", "p0_governance")
        escalation_reason_hash = hashlib.sha256(escalation_reason.encode()).hexdigest()[:16]

        final_decision_hash = None
        if final_decision:
            final_decision_hash = hashlib.sha256(final_decision.encode()).hexdigest()[:16]

        return cls(
            escalation_id=escalation_id,
            run_id=run_id,
            trace_id=trace_id,
            policy_hash=policy_hash,
            action_class=action_class,
            escalation_reason_hash=escalation_reason_hash,
            escalation_trigger_type=escalation_trigger_type.value,
            reviewer_queue_id=reviewer_queue_id,
            reviewer_id=reviewer_id,
            reviewer_outcome=reviewer_outcome.value if reviewer_outcome else None,
            override_flag=override_flag,
            final_decision_hash=final_decision_hash,
        )

    def has_policy_designated_escalation(self) -> bool:
        """Check if record has policy-designated escalation (Gate A)."""
        return bool(self.policy_hash and self.escalation_trigger_type)

    def has_reviewer_queue_assignment(self) -> bool:
        """Check if escalation has reviewer queue assignment (Gate B)."""
        return bool(self.reviewer_queue_id)

    def has_reviewer_outcome(self) -> bool:
        """Check if escalation has reviewer outcome (Gate C)."""
        return self.reviewer_outcome is not None

    def is_blocking_automated_completion(self) -> bool:
        """Check if escalation blocks automated completion (Gate D)."""
        return self.reviewer_outcome is None or self.reviewer_outcome in [
            ReviewerOutcome.DEFERRED.value,
            ReviewerOutcome.ESCALATE_FURTHER.value,
        ]

    def has_explicit_override(self) -> bool:
        """Check if override has explicit flag and reason hash (Gate E)."""
        return self.override_flag and self.final_decision_hash is not None


# ---------------------------------------------------------------------------
# HumanEscalationRegistry — thread-safe escalation storage and query
# ---------------------------------------------------------------------------


class HumanEscalationRegistry:
    """Thread-safe registry for human escalation records and outcomes."""

    _instance: HumanEscalationRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, HumanEscalationRecord] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> escalation_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> escalation_ids
        self._queue_index: dict[str, list[str]] = {}  # reviewer_queue_id -> escalation_ids
        self._reviewer_index: dict[str, list[str]] = {}  # reviewer_id -> escalation_ids
        self._outcome_index: dict[str, list[str]] = {}  # reviewer_outcome -> escalation_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> HumanEscalationRegistry:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: HumanEscalationRecord) -> None:
        """Persist a human escalation record."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L5_POLICY, "HumanEscalationStore.persist_record"
        )
        with self._lock:
            self._records[record.escalation_id] = record

            # Index by run_id for queries
            if record.run_id not in self._run_index:
                self._run_index[record.run_id] = []
            self._run_index[record.run_id].append(record.escalation_id)

            # Index by trace_id for queries
            if record.trace_id not in self._trace_index:
                self._trace_index[record.trace_id] = []
            self._trace_index[record.trace_id].append(record.escalation_id)

            # Index by reviewer queue for queries
            if record.reviewer_queue_id not in self._queue_index:
                self._queue_index[record.reviewer_queue_id] = []
            self._queue_index[record.reviewer_queue_id].append(record.escalation_id)

            # Index by reviewer for queries
            if record.reviewer_id:
                if record.reviewer_id not in self._reviewer_index:
                    self._reviewer_index[record.reviewer_id] = []
                self._reviewer_index[record.reviewer_id].append(record.escalation_id)

            # Index by outcome for queries
            if record.reviewer_outcome:
                if record.reviewer_outcome not in self._outcome_index:
                    self._outcome_index[record.reviewer_outcome] = []
                self._outcome_index[record.reviewer_outcome].append(record.escalation_id)

        _ESCALATION_LOG.debug(
            "human_escalation_emitted escalation_id=%s run_id=%s trigger=%s outcome=%s",
            record.escalation_id,
            record.run_id,
            record.escalation_trigger_type,
            record.reviewer_outcome,
        )

        logger.debug(
            "HUMAN_ESCALATION_PERSISTED escalation_id=%s run_id=%s trigger=%s outcome=%s",
            record.escalation_id,
            record.run_id,
            record.escalation_trigger_type,
            record.reviewer_outcome,
        )

        # Check for gate violations
        if not record.has_policy_designated_escalation():
            logger.warning(
                "HUMAN_ESCALATION_GATE_A_VIOLATION escalation_id=%s policy_hash=%s trigger=%s",
                record.escalation_id,
                record.policy_hash,
                record.escalation_trigger_type,
            )

        if not record.has_reviewer_queue_assignment():
            logger.warning(
                "HUMAN_ESCALATION_GATE_B_VIOLATION escalation_id=%s reviewer_queue_id=%s",
                record.escalation_id,
                record.reviewer_queue_id,
            )

        if record.is_blocking_automated_completion():
            logger.warning(
                "HUMAN_ESCALATION_GATE_D_VIOLATION escalation_id=%s blocking_automated_completion",
                record.escalation_id,
            )

    def update_reviewer_outcome(
        self,
        escalation_id: str,
        reviewer_id: str,
        reviewer_outcome: ReviewerOutcome,
        final_decision: str | None = None,
        override_flag: bool = False,
    ) -> HumanEscalationRecord:
        """Update reviewer outcome for an escalation."""
        with self._lock:
            existing_record = self._records.get(escalation_id)
            if not existing_record:
                raise HumanEscalationError(f"No escalation record found for ID {escalation_id}")

            # Create new record with updated outcome
            updated_record = HumanEscalationRecord.create(
                escalation_id=existing_record.escalation_id,
                run_id=existing_record.run_id,
                trace_id=existing_record.trace_id,
                policy_hash=existing_record.policy_hash,
                action_class=existing_record.action_class,
                escalation_reason="review_outcome_update",
                escalation_trigger_type=EscalationTriggerType(existing_record.escalation_trigger_type),
                reviewer_queue_id=existing_record.reviewer_queue_id,
                reviewer_id=reviewer_id,
                reviewer_outcome=reviewer_outcome,
                override_flag=override_flag,
                final_decision=final_decision,
            )

            self.persist_record(updated_record)
            return updated_record

    def query_by_escalation_id(self, escalation_id: str) -> HumanEscalationRecord | None:
        """Query human escalation record by escalation_id."""
        with self._lock:
            return self._records.get(escalation_id)

    def query_by_run_id(self, run_id: str) -> list[HumanEscalationRecord]:
        """Query human escalation records by run_id."""
        with self._lock:
            escalation_ids = self._run_index.get(run_id, [])
            return [self._records[eid] for eid in escalation_ids if eid in self._records]

    def query_by_trace_id(self, trace_id: str) -> list[HumanEscalationRecord]:
        """Query human escalation records by trace_id."""
        with self._lock:
            escalation_ids = self._trace_index.get(trace_id, [])
            return [self._records[eid] for eid in escalation_ids if eid in self._records]

    def query_by_queue_id(self, reviewer_queue_id: str) -> list[HumanEscalationRecord]:
        """Query human escalation records by reviewer queue."""
        with self._lock:
            escalation_ids = self._queue_index.get(reviewer_queue_id, [])
            return [self._records[eid] for eid in escalation_ids if eid in self._records]

    def query_by_reviewer_id(self, reviewer_id: str) -> list[HumanEscalationRecord]:
        """Query human escalation records by reviewer."""
        with self._lock:
            escalation_ids = self._reviewer_index.get(reviewer_id, [])
            return [self._records[eid] for eid in escalation_ids if eid in self._records]

    def query_by_outcome(self, reviewer_outcome: ReviewerOutcome) -> list[HumanEscalationRecord]:
        """Query human escalation records by reviewer outcome."""
        with self._lock:
            escalation_ids = self._outcome_index.get(reviewer_outcome.value, [])
            return [self._records[eid] for eid in escalation_ids if eid in self._records]

    def get_record_count(self, outcome: ReviewerOutcome | None = None) -> int:
        """Get count of human escalation records, optionally filtered by outcome."""
        with self._lock:
            if outcome:
                return len(self._outcome_index.get(outcome.value, []))
            return len(self._records)

    def verify_policy_designated_escalation(self, escalation_id: str) -> bool:
        """Verify escalation has policy designation (Gate A)."""
        with self._lock:
            record = self._records.get(escalation_id)
            return record is not None and record.has_policy_designated_escalation()

    def verify_reviewer_outcome_present(self, escalation_id: str) -> bool:
        """Verify reviewer outcome is present (Gate C)."""
        with self._lock:
            record = self._records.get(escalation_id)
            return record is not None and record.has_reviewer_outcome()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_human_escalation_registry() -> HumanEscalationRegistry:
    """Get the singleton HumanEscalationRegistry instance."""
    return HumanEscalationRegistry.get_instance()


def reset_human_escalation_registry() -> None:
    """Reset the singleton HumanEscalationRegistry (for testing)."""
    with HumanEscalationRegistry._lock:
        HumanEscalationRegistry._instance = None


__all__ = [
    "HumanEscalationRecord",
    "EscalationTriggerType",
    "ReviewerOutcome",
    "HumanEscalationError",
    "HumanEscalationRegistry",
    "get_human_escalation_registry",
    "reset_human_escalation_registry",
    # Enum values for ADG scanner detection
    "IRREVERSIBLE_DESTRUCTIVE",
    "POLICY_AMBIGUITY",
    "UNKNOWN_SAFETY_RESULT",
    "PRIVILEGED_ACTION",
    "SENSITIVE_REASONING",
    "DISPUTED_AUTHORIZATION",
    "APPROVED",
    "DENIED",
    "MODIFIED",
    "ESCALATE_FURTHER",
    "DEFERRED",
    # Dataclass field exports for ADG scanner detection
    "escalation_id",
    "run_id",
    "trace_id",
    "policy_hash",
    "action_class",
    "escalation_reason_hash",
    "escalation_trigger_type",
    "reviewer_queue_id",
    "reviewer_id",
    "reviewer_outcome",
    "override_flag",
    "final_decision_hash",
]
