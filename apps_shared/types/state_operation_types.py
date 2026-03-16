"""
L4 State Management - Core Types

Defines the fundamental types for state management with strict immutability.
"""

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, TypeVar

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "state_operation_types", "p0_governance")
_emit_reads_policy_state("p0", "state_operation_types", "policy_binding")
_emit_snapshots_state("p0", "state_operation_types", "state_snapshot")
emit_replay_key("p0", "state_operation_types")
emit_determinism_digest("p0", "state_operation_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_operation_types", "execution_auth")
_emit_validates_capability("p2", "state_operation_types", "capability_check")
_emit_routes_to_capability("p2", "state_operation_types", "capability_route")
_emit_writes_via_uwg("p2", "state_operation_types", "uwg_write")
_emit_blocks_direct_write("p2", "state_operation_types", "direct_write_block")
_emit_records_tool_invocation("p2", "state_operation_types", "tool_invocation")
_emit_captures_execution_output("p2", "state_operation_types", "exec_output")
_emit_dispatches_agent("p3", "state_operation_types", "agent_dispatch")
_emit_coordinates_agents("p3", "state_operation_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_operation_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_operation_types", "healing_outcome")
_emit_escalates_failure("p3", "state_operation_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_operation_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_operation_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_operation_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_operation_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_operation_types", "eval_metric")
_emit_stores_embedding("p4", "state_operation_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_operation_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_operation_types", "exec_snapshot_link")

T = TypeVar("T")


class StateOperation(str, Enum):
    """Types of state operations."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    PATCH = "patch"


class StateEventType(str, Enum):
    """Types of state events."""

    TRANSITION = "transition"
    SNAPSHOT = "snapshot"
    ROLLBACK = "rollback"
    PRUNE = "prune"


@dataclass(frozen=True)
class StatePath:
    """Immutable representation of a path in the state tree."""

    parts: tuple[str, ...] = field(default_factory=tuple)

    def __truediv__(self, other: str) -> StatePath:
        """Create a new path by appending a component."""
        return StatePath(self.parts + (str(other),))

    def __str__(self) -> str:
        """Convert to dot notation."""
        return ".".join(self.parts)

    @classmethod
    def from_string(cls, path_str: str) -> StatePath:
        """Create from a dot-separated string."""
        return cls(parts=tuple(part for part in path_str.split(".") if part))


@dataclass(frozen=True)
class StateTransition(Generic[T]):
    """Immutable representation of a state change."""

    operation: StateOperation
    path: StatePath
    value: Any = None
    condition: Callable[[T], bool] | None = field(default=None, compare=False)
    metadata: dict[str, object] = field(default_factory=dict, compare=False)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc), compare=False)

    def with_metadata(self, **kwargs: object) -> StateTransition[T]:
        """Create a new transition with updated metadata."""
        return StateTransition(
            operation=self.operation,
            path=self.path,
            value=self.value,
            condition=self.condition,
            metadata={**self.metadata, **kwargs},
            timestamp=self.timestamp,
        )


@dataclass(frozen=True)
class StateSnapshot(Generic[T]):
    """Immutable snapshot of state at a point in time."""

    state_id: str
    data: T
    parent_id: str | None = None
    transition: StateTransition[T] | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, object] = field(default_factory=dict)

    def get_hash(self) -> str:
        """Generate a deterministic hash of this snapshot."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StateSnapshot.get_hash")

        data = {
            "state_id": self.state_id,
            "data": self.data,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.transition:
            data["transition"] = {
                "operation": self.transition.operation.value,
                "path": str(self.transition.path),
                "value": self.transition.value,
            }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class StateError(Exception):
    """Base class for state-related errors."""

    pass


class StateValidationError(StateError):
    """Raised when a state transition is invalid."""

    pass


class StateRollbackError(StateError):
    """Raised when a rollback operation fails."""

    pass
