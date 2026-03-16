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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "state_operation_types", "p0_governance")
_emit_reads_policy_state("p0", "state_operation_types", "policy_binding")
_emit_snapshots_state("p0", "state_operation_types", "state_snapshot")
emit_replay_key("p0", "state_operation_types")
emit_determinism_digest("p0", "state_operation_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
