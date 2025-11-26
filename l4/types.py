"""
L4 state management types for resume job alignment.

Defines fundamental types for resume workflow state operations.
"""
from __future__ import annotations
from typing import Any, Dict, Optional, TypeVar, Generic, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json

T = TypeVar('T')

class StateOperation(str, Enum):
    """State operations for resume job alignment workflows."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    PATCH = "patch"

class StateEventType(str, Enum):
    """State events for resume job alignment workflows."""
    TRANSITION = "transition"
    SNAPSHOT = "snapshot"
    ROLLBACK = "rollback"
    PRUNE = "prune"

@dataclass(frozen=True)
class StatePath:
    """Immutable path for resume workflow state tree navigation."""
    parts: tuple[str, ...] = field(default_factory=tuple)
    
    def __truediv__(self, other: str) -> StatePath:
        """Creates new resume workflow state path with component."""
        return StatePath(self.parts + (str(other),))
    
    def __str__(self) -> str:
        """Converts resume workflow state path to dot notation."""
        return ".".join(self.parts)
    
    @classmethod
    def from_string(cls, path_str: str) -> StatePath:
        """Creates resume workflow state path from dot string."""
        return cls(parts=tuple(part for part in path_str.split(".") if part))

@dataclass(frozen=True)
class StateTransition(Generic[T]):
    """Immutable representation of resume workflow state change."""
    operation: StateOperation
    path: StatePath
    value: Any = None
    condition: Optional[Callable[[T], bool]] = field(default=None, compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc), compare=False)
    
    def with_metadata(self, **kwargs: Any) -> StateTransition[T]:
        """Creates new resume workflow transition with metadata."""
        return StateTransition(
            operation=self.operation,
            path=self.path,
            value=self.value,
            condition=self.condition,
            metadata={**self.metadata, **kwargs},
            timestamp=self.timestamp
        )

@dataclass(frozen=True)
class StateSnapshot(Generic[T]):
    """Immutable snapshot of resume workflow state for job alignment."""
    state_id: str
    data: T
    parent_id: Optional[str] = None
    transition: Optional[StateTransition[T]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_hash(self) -> str:
        """Generates deterministic hash of resume workflow snapshot."""
        data = {
            'state_id': self.state_id,
            'data': self.data,
            'parent_id': self.parent_id,
            'timestamp': self.timestamp.isoformat(),
        }
        if self.transition:
            data['transition'] = {
                'operation': self.transition.operation.value,
                'path': str(self.transition.path),
                'value': self.transition.value
            }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

class StateError(Exception):
    """Base error for resume workflow state operations."""
    pass

class StateValidationError(StateError):
    """Error for invalid resume workflow state transitions."""
    pass

class StateRollbackError(StateError):
    """Error for failed resume workflow state rollbacks."""
    pass



