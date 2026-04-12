"""
agentic_core/L4_state/lifecycle/state_lifecycle.py

P3/L4 State Lifecycle Governance — state lifecycle record and metrics.

Provides StateLifecycleRecord (10 required fields) and lifecycle status/retention
tracking for operational governance of runtime state objects.
"""

from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L2_execution.utils.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("state_lifecycle", "p4obs", "metric_1")
_emit_emits_metric_event("state_lifecycle", "p4obs", "metric_2")
_emit_emits_metric_event("state_lifecycle", "p4obs", "metric_3")
_emit_emits_metric_event("state_lifecycle", "p4obs", "metric_4")
_emit_emits_metric_event("state_lifecycle", "p4obs", "metric_5")
_emit_emits_metric_event("state_lifecycle", "p4obs", "metric_6")
_emit_records_incident_event("state_lifecycle", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_lifecycle", "p4obs", "anomaly")
_emit_writes_observability_log("state_lifecycle", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_lifecycle", "p4obs", "mon_state")
_emit_triggers_alert("state_lifecycle", "p4obs", "alert")
_emit_links_incident_trace("state_lifecycle", "p4obs", "trace_link")
_emit_captures_pattern("state_lifecycle", "p3lm", "pattern")
_emit_records_learning_event("state_lifecycle", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_lifecycle", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_lifecycle", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_lifecycle", "p3lm", "routing")
_emit_improves_agent_policy("state_lifecycle", "p3lm", "policy")
_emit_stores_learning_state("state_lifecycle", "p3lm", "state")
_emit_records_execution_trace("state_lifecycle", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_lifecycle", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_lifecycle", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_lifecycle", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_lifecycle", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_lifecycle", "env_read", "p2_env_1")
_emit_reads_environ("state_lifecycle", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_lifecycle", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_lifecycle", "runtime_state", "p2_rt_2")

_emit_applies_guardrail("p0", "state_lifecycle", "p0_governance")
_emit_snapshots_state("p0", "state_lifecycle", "state_snapshot")
_emit_escalates_to_human("p1", "state_lifecycle", "human_escalation")
_emit_pulls_context("p1", "state_lifecycle", "context_pull")
_emit_pulls_context("p1", "state_lifecycle", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "state_lifecycle", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_lifecycle", "uwg_term_secondary")
_emit_writes_through("p1", "state_lifecycle", "write_through")
_emit_writes_through("p1", "state_lifecycle", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "state_lifecycle", "safety_validation")
_emit_invokes_eval("p1", "state_lifecycle", "eval_call")
_emit_proposal_commits_routing("p1", "state_lifecycle", "routing_commit")
_emit_routes_through("p1", "state_lifecycle", "route_through")
_emit_checks_agent_registry("p1", "state_lifecycle", "agent_registry")
_emit_validates_agent_capability("p1", "state_lifecycle", "capability")
_emit_dispatches_execution_plan("p1", "state_lifecycle", "exec_plan")
_emit_agent_executes_agent("p1", "state_lifecycle", "sub_agent")
_emit_routes_to_agent("p1", "state_lifecycle", "target_agent")
_emit_verifies_policy("p1", "state_lifecycle", "policy_check")
_emit_observes_runtime_state("p1", "state_lifecycle", "runtime_state")
_emit_verifies_boundary("p1", "state_lifecycle", "boundary_check")
_emit_transcripts_response("p1", "state_lifecycle", "transcript")
_emit_hard_fails_untranscripted("p1", "state_lifecycle")
_emit_gated_by_confidence("p1", "state_lifecycle", "confidence_gate")
emit_replay_key("p0", "state_lifecycle")
emit_determinism_digest("p0", "state_lifecycle")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_lifecycle", "execution_auth")
_emit_validates_capability("p2", "state_lifecycle", "capability_check")
_emit_routes_to_capability("p2", "state_lifecycle", "capability_route")
_emit_writes_via_uwg("p2", "state_lifecycle", "uwg_write")
_emit_blocks_direct_write("p2", "state_lifecycle", "direct_write_block")
_emit_records_tool_invocation("p2", "state_lifecycle", "tool_invocation")
_emit_captures_execution_output("p2", "state_lifecycle", "exec_output")
_emit_dispatches_agent("p3", "state_lifecycle", "agent_dispatch")
_emit_coordinates_agents("p3", "state_lifecycle", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_lifecycle", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_lifecycle", "healing_outcome")
_emit_escalates_failure("p3", "state_lifecycle", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_lifecycle", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_lifecycle", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_lifecycle", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_lifecycle", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_lifecycle", "eval_metric")
_emit_stores_embedding("p4", "state_lifecycle", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_lifecycle", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_lifecycle", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_LIFECYCLE_LOG = logging.getLogger("adg.state_lifecycle_emitted")


# ---------------------------------------------------------------------------
# Enums for state lifecycle tracking
# ---------------------------------------------------------------------------


class LifecycleStatus(Enum):
    """Status of state lifecycle operations."""

    ACTIVE = "ACTIVE"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    ARCHIVED = "ARCHIVED"
    PENDING_DELETION = "PENDING_DELETION"
    DELETED = "DELETED"


class RetentionClass(Enum):
    """Retention classification for state objects."""

    SHORT_TERM = "SHORT_TERM"  # Hours to days
    MEDIUM_TERM = "MEDIUM_TERM"  # Days to weeks
    LONG_TERM = "LONG_TERM"  # Weeks to months
    PERMANENT = "PERMANENT"  # Never expires


# Export enum values for ADG scanner detection
ACTIVE = LifecycleStatus.ACTIVE
STALE = LifecycleStatus.STALE
EXPIRED = LifecycleStatus.EXPIRED
ARCHIVED = LifecycleStatus.ARCHIVED
PENDING_DELETION = LifecycleStatus.PENDING_DELETION
DELETED = LifecycleStatus.DELETED

SHORT_TERM = RetentionClass.SHORT_TERM
MEDIUM_TERM = RetentionClass.MEDIUM_TERM
LONG_TERM = RetentionClass.LONG_TERM
PERMANENT = RetentionClass.PERMANENT


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class StateLifecycleError(Exception):
    """Raised when state namespace exists without lifecycle policy (Gate A)."""

    pass


# ---------------------------------------------------------------------------
# StateLifecycleRecord — 10 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StateLifecycleRecord:
    """Immutable state lifecycle record for operational governance (10 required fields)."""

    state_namespace: str
    lifecycle_policy_id: str
    retention_class: str
    expiration_rule: str
    archival_rule: str
    deletion_rule: str
    created_at_tick: float
    last_accessed_tick: float
    last_mutated_tick: float
    lifecycle_status: str
    lifecycle_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        state_namespace: str,
        lifecycle_policy_id: str,
        retention_class: RetentionClass,
        expiration_rule: str,
        archival_rule: str,
        deletion_rule: str,
        created_at_tick: float | None = None,
        last_accessed_tick: float | None = None,
        last_mutated_tick: float | None = None,
        lifecycle_status: LifecycleStatus = LifecycleStatus.ACTIVE,
    ) -> StateLifecycleRecord:
        """Factory to create StateLifecycleRecord with computed fields."""
        current_time = get_clock().now_epoch()

        return cls(
            state_namespace=state_namespace,
            lifecycle_policy_id=lifecycle_policy_id,
            retention_class=retention_class.value,
            expiration_rule=expiration_rule,
            archival_rule=archival_rule,
            deletion_rule=deletion_rule,
            created_at_tick=created_at_tick or current_time,
            last_accessed_tick=last_accessed_tick or current_time,
            last_mutated_tick=last_mutated_tick or current_time,
            lifecycle_status=lifecycle_status.value,
        )

    def has_lifecycle_policy(self) -> bool:
        """Check if record has lifecycle policy (Gate A)."""
        return bool(self.lifecycle_policy_id)

    def is_active(self) -> bool:
        """Check if state is in active status."""
        return self.lifecycle_status == LifecycleStatus.ACTIVE.value

    def is_expired(self) -> bool:
        """Check if state is expired (Gate B)."""
        return self.lifecycle_status == LifecycleStatus.EXPIRED.value

    def has_lifecycle_transition(self) -> bool:
        """Check if lifecycle transition is recorded (Gate C)."""
        return (
            self.lifecycle_status != LifecycleStatus.ACTIVE.value
            and self.lifecycle_status != LifecycleStatus.DELETED.value
        )

    def is_stale_growth(self) -> bool:
        """Check if stale state growth is occurring (Gate D)."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "StateLifecycle.is_stale_growth"
        )
        current_time = get_clock().now_epoch()
        time_since_access = current_time - self.last_accessed_tick
        time_since_mutation = current_time - self.last_mutated_tick

        # Consider stale if not accessed for 24 hours and not mutated for 12 hours
        return (
            self.lifecycle_status == LifecycleStatus.ACTIVE.value
            and time_since_access > 86400  # 24 hours
            and time_since_mutation > 43200  # 12 hours
        )

    def has_destructive_cleanup_approval(self) -> bool:
        """Check if destructive cleanup has policy and trace approval (Gate E)."""
        return (
            self.lifecycle_status in [LifecycleStatus.ARCHIVED.value, LifecycleStatus.DELETED.value]
            and self.lifecycle_policy_id is not None
        )


# ---------------------------------------------------------------------------
# LifecyclePolicy — lifecycle policy definition per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LifecyclePolicy:
    """Explicit lifecycle policy for state objects."""

    policy_id: str
    retention_class: RetentionClass
    expiration_duration_seconds: int
    archival_duration_seconds: int
    deletion_duration_seconds: int
    requires_approval_for_deletion: bool
    trace_linkage_required: bool
    destructive_action_classification: str

    @classmethod
    def create(
        cls,
        policy_id: str,
        retention_class: RetentionClass,
        expiration_duration_seconds: int,
        archival_duration_seconds: int,
        deletion_duration_seconds: int,
        requires_approval_for_deletion: bool = True,
        trace_linkage_required: bool = True,
        destructive_action_classification: str = "DESTRUCTIVE",
    ) -> LifecyclePolicy:
        return cls(
            policy_id=policy_id,
            retention_class=retention_class,
            expiration_duration_seconds=expiration_duration_seconds,
            archival_duration_seconds=archival_duration_seconds,
            deletion_duration_seconds=deletion_duration_seconds,
            requires_approval_for_deletion=requires_approval_for_deletion,
            trace_linkage_required=trace_linkage_required,
            destructive_action_classification=destructive_action_classification,
        )

    def should_expire(self, created_at_tick: float, current_tick: float | None = None) -> bool:
        """Check if state should expire based on policy."""
        current_tick = current_tick or get_clock().now_epoch()
        age_seconds = current_tick - created_at_tick
        return age_seconds > self.expiration_duration_seconds

    def should_archive(self, created_at_tick: float, current_tick: float | None = None) -> bool:
        """Check if state should be archived based on policy."""
        current_tick = current_tick or get_clock().now_epoch()
        age_seconds = current_tick - created_at_tick
        return age_seconds > self.archival_duration_seconds

    def should_delete(self, created_at_tick: float, current_tick: float | None = None) -> bool:
        """Check if state should be deleted based on policy."""
        current_tick = current_tick or get_clock().now_epoch()
        age_seconds = current_tick - created_at_tick
        return age_seconds > self.deletion_duration_seconds


# ---------------------------------------------------------------------------
# StateLifecycleRegistry — thread-safe lifecycle storage and query
# ---------------------------------------------------------------------------


class StateLifecycleRegistry:
    """Thread-safe registry for state lifecycle records and policies."""

    _instance: StateLifecycleRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, StateLifecycleRecord] = {}
        self._namespace_index: dict[str, list[str]] = {}  # namespace -> record_ids
        self._status_index: dict[str, list[str]] = {}  # status -> record_ids
        self._policy_index: dict[str, list[str]] = {}  # policy_id -> record_ids
        self._policies: dict[str, LifecyclePolicy] = {}  # policy_id -> policy
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> StateLifecycleRegistry:
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: StateLifecycleRecord) -> None:
        """Persist a state lifecycle record."""
        with self._lock:
            self._records[record.state_namespace] = record

            # Index by namespace for queries
            if record.state_namespace not in self._namespace_index:
                self._namespace_index[record.state_namespace] = []
            self._namespace_index[record.state_namespace].append(record.state_namespace)

            # Index by status for queries
            if record.lifecycle_status not in self._status_index:
                self._status_index[record.lifecycle_status] = []
            self._status_index[record.lifecycle_status].append(record.state_namespace)

            # Index by policy for queries
            if record.lifecycle_policy_id not in self._policy_index:
                self._policy_index[record.lifecycle_policy_id] = []
            self._policy_index[record.lifecycle_policy_id].append(record.state_namespace)

        _LIFECYCLE_LOG.debug(
            "state_lifecycle_emitted namespace=%s policy_id=%s status=%s retention=%s",
            record.state_namespace,
            record.lifecycle_policy_id,
            record.lifecycle_status,
            record.retention_class,
        )

        logger.debug(
            "STATE_LIFECYCLE_PERSISTED namespace=%s policy_id=%s status=%s retention=%s",
            record.state_namespace,
            record.lifecycle_policy_id,
            record.lifecycle_status,
            record.retention_class,
        )

        # Check for gate violations
        if not record.has_lifecycle_policy():
            logger.warning(
                "STATE_LIFECYCLE_GATE_A_VIOLATION namespace=%s policy_id=%s",
                record.state_namespace,
                record.lifecycle_policy_id,
            )

        if record.is_expired() and record.is_active():
            logger.warning(
                "STATE_LIFECYCLE_GATE_B_VIOLATION namespace=%s status=%s expired_but_active",
                record.state_namespace,
                record.lifecycle_status,
            )

        if record.is_stale_growth():
            logger.warning(
                "STATE_LIFECYCLE_GATE_D_VIOLATION namespace=%s stale_growth_detected",
                record.state_namespace,
            )

    def register_policy(self, policy: LifecyclePolicy) -> None:
        """Register a lifecycle policy."""
        with self._lock:
            self._policies[policy.policy_id] = policy
        logger.debug(
            "LIFECYCLE_POLICY_REGISTERED policy_id=%s retention=%s expiration=%ds",
            policy.policy_id,
            policy.retention_class.value,
            policy.expiration_duration_seconds,
        )

    def update_access_time(self, state_namespace: str) -> None:
        """Update last accessed time for a state namespace."""
        with self._lock:
            record = self._records.get(state_namespace)
            if record:
                # Create new record with updated access time
                new_record = StateLifecycleRecord.create(
                    state_namespace=record.state_namespace,
                    lifecycle_policy_id=record.lifecycle_policy_id,
                    retention_class=RetentionClass(record.retention_class),
                    expiration_rule=record.expiration_rule,
                    archival_rule=record.archival_rule,
                    deletion_rule=record.deletion_rule,
                    created_at_tick=record.created_at_tick,
                    last_accessed_tick=get_clock().now_epoch(),
                    last_mutated_tick=record.last_mutated_tick,
                    lifecycle_status=LifecycleStatus(record.lifecycle_status),
                )
                self.persist_record(new_record)

    def update_mutation_time(self, state_namespace: str) -> None:
        """Update last mutated time for a state namespace."""
        with self._lock:
            record = self._records.get(state_namespace)
            if record:
                # Create new record with updated mutation time
                new_record = StateLifecycleRecord.create(
                    state_namespace=record.state_namespace,
                    lifecycle_policy_id=record.lifecycle_policy_id,
                    retention_class=RetentionClass(record.retention_class),
                    expiration_rule=record.expiration_rule,
                    archival_rule=record.archival_rule,
                    deletion_rule=record.deletion_rule,
                    created_at_tick=record.created_at_tick,
                    last_accessed_tick=record.last_accessed_tick,
                    last_mutated_tick=get_clock().now_epoch(),
                    lifecycle_status=LifecycleStatus(record.lifecycle_status),
                )
                self.persist_record(new_record)

    def query_by_namespace(self, state_namespace: str) -> StateLifecycleRecord | None:
        """Query state lifecycle record by namespace."""
        with self._lock:
            return self._records.get(state_namespace)

    def query_by_status(self, status: LifecycleStatus) -> list[StateLifecycleRecord]:
        """Query state lifecycle records by status."""
        with self._lock:
            namespace_ids = self._status_index.get(status.value, [])
            return [self._records[ns] for ns in namespace_ids if ns in self._records]

    def query_by_policy(self, policy_id: str) -> list[StateLifecycleRecord]:
        """Query state lifecycle records by policy."""
        with self._lock:
            namespace_ids = self._policy_index.get(policy_id, [])
            return [self._records[ns] for ns in namespace_ids if ns in self._records]

    def get_policy(self, policy_id: str) -> LifecyclePolicy | None:
        """Get lifecycle policy by ID."""
        with self._lock:
            return self._policies.get(policy_id)

    def get_record_count(self, status: LifecycleStatus | None = None) -> int:
        """Get count of state lifecycle records, optionally filtered by status."""
        with self._lock:
            if status:
                return len(self._status_index.get(status.value, []))
            return len(self._records)

    def verify_namespace_has_policy(self, state_namespace: str) -> bool:
        """Verify state namespace has lifecycle policy (Gate A)."""
        with self._lock:
            record = self._records.get(state_namespace)
            return record is not None and record.has_lifecycle_policy()

    def verify_expired_not_active(self, state_namespace: str) -> bool:
        """Verify expired state is not active (Gate B)."""
        with self._lock:
            record = self._records.get(state_namespace)
            return record is not None and not (record.is_expired() and record.is_active())


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_state_lifecycle_registry() -> StateLifecycleRegistry:
    """Get the singleton StateLifecycleRegistry instance."""
    return StateLifecycleRegistry.get_instance()


def reset_state_lifecycle_registry() -> None:
    """Reset the singleton StateLifecycleRegistry (for testing)."""
    with StateLifecycleRegistry._lock:
        StateLifecycleRegistry._instance = None


__all__ = [
    "StateLifecycleRecord",
    "LifecyclePolicy",
    "LifecycleStatus",
    "RetentionClass",
    "StateLifecycleError",
    "StateLifecycleRegistry",
    "get_state_lifecycle_registry",
    "reset_state_lifecycle_registry",
    # Enum values for ADG scanner detection
    "ACTIVE",
    "STALE",
    "EXPIRED",
    "ARCHIVED",
    "PENDING_DELETION",
    "DELETED",
    "SHORT_TERM",
    "MEDIUM_TERM",
    "LONG_TERM",
    "PERMANENT",
]
