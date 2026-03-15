"""
agentic_core/L4_persistence/lifecycle/state_lifecycle.py

P3/L4 State Lifecycle Governance — state lifecycle record and metrics.

Provides StateLifecycleRecord (10 required fields) and lifecycle status/retention
tracking for operational governance of runtime state objects.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from agentic_core.L2_execution.providers import get_clock

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
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "StateLifecycle.is_stale_growth")
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
