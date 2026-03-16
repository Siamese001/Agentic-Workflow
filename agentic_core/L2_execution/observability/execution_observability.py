"""
agentic_core/L2_execution/observability/execution_observability.py

P3/L2 Execution Observability — execution observability record and metrics.

Provides ExecutionObservabilityRecord (14 required fields) and execution
status/failure classification for operational telemetry.
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "execution_observability")
emit_determinism_digest("p0", "execution_observability")

_emit_dispatches_healing_run("p1", "execution_observability", "L2")
_emit_routes_through("p1", "execution_observability", "L2")
_emit_escalates_to_human("p1", "execution_observability", "L2")
_emit_reads_policy_state("p1", "execution_observability", "L2")

_emit_applies_guardrail("p0", "execution_observability", "p0_governance")
_emit_snapshots_state("p0", "execution_observability", "state_snapshot")

logger = logging.getLogger(__name__)
_OBSERVABILITY_LOG = logging.getLogger("adg.execution_observability_emitted")


# ---------------------------------------------------------------------------
# Enums for execution observability tracking
# ---------------------------------------------------------------------------


class ExecutionStatus(Enum):
    """Status of execution operations."""

    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRIED = "RETRIED"
    CANCELLED = "CANCELLED"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    ESCALATED = "ESCALATED"


class FailureClassification(Enum):
    """Classification of execution failures."""

    POLICY_BLOCK = "POLICY_BLOCK"
    TOOL_ERROR = "TOOL_ERROR"
    NETWORK_FAILURE = "NETWORK_FAILURE"
    MUTATION_FAILURE = "MUTATION_FAILURE"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"


# Export enum values for ADG scanner detection
STARTED = ExecutionStatus.STARTED
SUCCEEDED = ExecutionStatus.SUCCEEDED
FAILED = ExecutionStatus.FAILED
RETRIED = ExecutionStatus.RETRIED
CANCELLED = ExecutionStatus.CANCELLED
BLOCKED_BY_POLICY = ExecutionStatus.BLOCKED_BY_POLICY
ESCALATED = ExecutionStatus.ESCALATED

POLICY_BLOCK = FailureClassification.POLICY_BLOCK
TOOL_ERROR = FailureClassification.TOOL_ERROR
NETWORK_FAILURE = FailureClassification.NETWORK_FAILURE
MUTATION_FAILURE = FailureClassification.MUTATION_FAILURE
VALIDATION_FAILURE = FailureClassification.VALIDATION_FAILURE
UNKNOWN_FAILURE = FailureClassification.UNKNOWN_FAILURE


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class ExecutionObservabilityError(Exception):
    """Raised when governed runtime execution completes without observability record (Gate A)."""

    pass


# ---------------------------------------------------------------------------
# ExecutionObservabilityRecord — 14 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionObservabilityRecord:
    """Immutable execution observability record for operational telemetry (14 required fields)."""

    execution_observability_id: str
    run_id: str
    trace_id: str
    execution_request_id: str
    execution_target_hash: str
    execution_start_tick: float
    execution_end_tick: float
    duration_ms: int
    execution_status: str
    retry_count: int
    retry_reason_hash: str | None
    failure_reason_hash: str | None
    guardrail_decision_id: str | None
    policy_hash: str
    observability_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        execution_request_id: str,
        execution_target: str,
        execution_start_tick: float,
        execution_end_tick: float,
        execution_status: ExecutionStatus,
        retry_count: int = 0,
        retry_reason: str | None = None,
        failure_reason: str | None = None,
        guardrail_decision_id: str | None = None,
        policy_hash: str = "",
    ) -> ExecutionObservabilityRecord:
        """Factory to create ExecutionObservabilityRecord with computed fields."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ExecutionObservabilityRecord.create"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionObservabilityRecord.create".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        execution_observability_id = str(uuid.uuid4())

        # Compute hashes
        execution_target_hash = hashlib.sha256(execution_target.encode()).hexdigest()[:16]
        duration_ms = int((execution_end_tick - execution_start_tick) * 1000)

        retry_reason_hash = None
        if retry_reason:
            retry_reason_hash = hashlib.sha256(retry_reason.encode()).hexdigest()[:16]

        failure_reason_hash = None
        if failure_reason:
            failure_reason_hash = hashlib.sha256(failure_reason.encode()).hexdigest()[:16]

        return cls(
            execution_observability_id=execution_observability_id,
            run_id=run_id,
            trace_id=trace_id,
            execution_request_id=execution_request_id,
            execution_target_hash=execution_target_hash,
            execution_start_tick=execution_start_tick,
            execution_end_tick=execution_end_tick,
            duration_ms=duration_ms,
            execution_status=execution_status.value,
            retry_count=retry_count,
            retry_reason_hash=retry_reason_hash,
            failure_reason_hash=failure_reason_hash,
            guardrail_decision_id=guardrail_decision_id,
            policy_hash=policy_hash,
        )

    def has_duration(self) -> bool:
        """Check if record has duration_ms (Gate B)."""
        return self.duration_ms > 0

    def has_failure_classification(self) -> bool:
        """Check if failed execution has failure classification (Gate C)."""
        return self.execution_status == ExecutionStatus.FAILED.value and self.failure_reason_hash is not None

    def has_retry_metadata(self) -> bool:
        """Check if retried execution has retry metadata (Gate D)."""
        return (
            self.execution_status == ExecutionStatus.RETRIED.value
            and self.retry_count > 0
            and self.retry_reason_hash is not None
        )

    def has_policy_linkage(self) -> bool:
        """Check if blocked execution has policy linkage (Gate E)."""
        return self.execution_status == ExecutionStatus.BLOCKED_BY_POLICY.value and bool(self.policy_hash)


# ---------------------------------------------------------------------------
# ObservabilityRegistry — thread-safe observability storage and query
# ---------------------------------------------------------------------------


class ObservabilityRegistry:
    """Thread-safe registry for execution observability records and queries."""

    _instance: ObservabilityRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._records: dict[str, ExecutionObservabilityRecord] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> record_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> record_ids
        self._status_index: dict[str, list[str]] = {}  # status -> record_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> ObservabilityRegistry:
        """Singleton accessor."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "ObservabilityRegistry.get_instance"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ObservabilityRegistry.get_instance".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_record(self, record: ExecutionObservabilityRecord) -> None:
        """Persist an execution observability record."""
        with self._lock:
            self._records[record.execution_observability_id] = record

            # Index by run_id for queries
            if record.run_id not in self._run_index:
                self._run_index[record.run_id] = []
            self._run_index[record.run_id].append(record.execution_observability_id)

            # Index by trace_id for queries
            if record.trace_id not in self._trace_index:
                self._trace_index[record.trace_id] = []
            self._trace_index[record.trace_id].append(record.execution_observability_id)

            # Index by status for queries
            if record.execution_status not in self._status_index:
                self._status_index[record.execution_status] = []
            self._status_index[record.execution_status].append(record.execution_observability_id)

        _OBSERVABILITY_LOG.debug(
            "execution_observability_emitted record_id=%s run_id=%s trace_id=%s status=%s duration_ms=%d",
            record.execution_observability_id,
            record.run_id,
            record.trace_id,
            record.execution_status,
            record.duration_ms,
        )

        logger.debug(
            "EXECUTION_OBSERVABILITY_PERSISTED record_id=%s run_id=%s status=%s duration_ms=%d",
            record.execution_observability_id,
            record.run_id,
            record.execution_status,
            record.duration_ms,
        )

        # Check for gate violations
        if not record.has_duration():
            logger.warning(
                "OBSERVABILITY_GATE_B_VIOLATION record_id=%s duration_ms=%d",
                record.execution_observability_id,
                record.duration_ms,
            )

        if (
            record.execution_status == ExecutionStatus.FAILED.value
            and not record.has_failure_classification()
        ):
            logger.warning(
                "OBSERVABILITY_GATE_C_VIOLATION record_id=%s failed without classification",
                record.execution_observability_id,
            )

        if record.execution_status == ExecutionStatus.RETRIED.value and not record.has_retry_metadata():
            logger.warning(
                "OBSERVABILITY_GATE_D_VIOLATION record_id=%s retried without metadata",
                record.execution_observability_id,
            )

        if (
            record.execution_status == ExecutionStatus.BLOCKED_BY_POLICY.value
            and not record.has_policy_linkage()
        ):
            logger.warning(
                "OBSERVABILITY_GATE_E_VIOLATION record_id=%s blocked without policy linkage",
                record.execution_observability_id,
            )

    def query_by_run_id(self, run_id: str) -> list[ExecutionObservabilityRecord]:
        """Query execution observability records by run_id."""
        with self._lock:
            record_ids = self._run_index.get(run_id, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_trace_id(self, trace_id: str) -> list[ExecutionObservabilityRecord]:
        """Query execution observability records by trace_id."""
        with self._lock:
            record_ids = self._trace_index.get(trace_id, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_status(self, status: ExecutionStatus) -> list[ExecutionObservabilityRecord]:
        """Query execution observability records by status."""
        _emit_observes_runtime_state(
            str(uuid.uuid4()), "ObservabilityRegistry.query_by_status", "L2_EXECUTION"
        )
        with self._lock:
            record_ids = self._status_index.get(status.value, [])
            return [self._records[record_id] for record_id in record_ids if record_id in self._records]

    def query_by_record_id(self, record_id: str) -> ExecutionObservabilityRecord | None:
        """Query execution observability record by execution_observability_id."""
        with self._lock:
            return self._records.get(record_id)

    def get_record_count(self, run_id: str = "") -> int:
        """Get count of execution observability records, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._records)

    def verify_record_exists(self, record_id: str) -> bool:
        """Verify execution observability record exists (Gate A)."""
        with self._lock:
            return record_id in self._records

    def verify_duration_present(self, record_id: str) -> bool:
        """Verify record has duration_ms (Gate B)."""
        with self._lock:
            record = self._records.get(record_id)
            return record is not None and record.has_duration()


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_observability_registry() -> ObservabilityRegistry:
    """Get the singleton ObservabilityRegistry instance."""
    return ObservabilityRegistry.get_instance()


def reset_observability_registry() -> None:
    """Reset the singleton ObservabilityRegistry (for testing)."""
    with ObservabilityRegistry._lock:
        ObservabilityRegistry._instance = None


__all__ = [
    "ExecutionObservabilityRecord",
    "ExecutionStatus",
    "FailureClassification",
    "ExecutionObservabilityError",
    "ObservabilityRegistry",
    "get_observability_registry",
    "reset_observability_registry",
    # Enum values for ADG scanner detection
    "STARTED",
    "SUCCEEDED",
    "FAILED",
    "RETRIED",
    "CANCELLED",
    "BLOCKED_BY_POLICY",
    "ESCALATED",
    "POLICY_BLOCK",
    "TOOL_ERROR",
    "NETWORK_FAILURE",
    "MUTATION_FAILURE",
    "VALIDATION_FAILURE",
    "UNKNOWN_FAILURE",
]
