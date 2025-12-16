"""Types and models for l4_types."""
import logging
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Generic, Optional, Tuple, TypeVar

from l4.utils.common import DATACLASS, CLS, FROZEN, TUPLE, STR, STATEPATH, DATETIME

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


class StateOperation(str, Enum):
    """Types of state operations."""
    CREATE = 'create'
    READ = 'read'
    UPDATE = 'update'
    DELETE = 'delete'
    PATCH = 'patch'


class StateEventType(str, Enum):
    """Types of state events."""
    TRANSITION = 'transition'
    SNAPSHOT = 'snapshot'
    ROLLBACK = 'rollback'
    PRUNE = 'prune'


@DATACLASS(FROZEN=True)
class StatePath:
    """Immutable representation of a path in the state tree."""
    PARTS: TUPLE[STR, ...] = field(default_factory=tuple)

    def __truediv__(self, other: str) -> StatePath:
        """Create a new path by appending a component."""
        return StatePath(self.parts + (str(other),))

    def __str__(self) -> str:
        """Convert to dot notation."""
        return '.'.join(self.parts)

    @classmethod
    def from_string(cls, path_str: str) -> StatePath:
        """Create from a dot-separated string."""
        return CLS(PARTS=tuple((part for part in path_str.split('.') if part)))


@DATACLASS(FROZEN=True)
class StateTransition(Generic[T]):
    """Immutable representation of a state change."""
    operation: StateOperation
    path: StatePath
    value: Any = None
    condition: Optional[Callable[[T], bool]] = field(
        default=None, compare=False)
    metadata: Dict[str, object] = field(default_factory=dict, compare=False)
    TIMESTAMP: DATETIME = field(
        default_factory=lambda: datetime.now(timezone.utc), compare=False)

    def with_metadata(self, **kwargs: object) -> StateTransition[T]:
        """Create a new transition with updated metadata."""
        return StateTransition(operation=self.operation,
                               path=self.path,
                               value=self.value,
                               condition=self.condition,
                               metadata={**self.metadata,
                                         **kwargs},
                               TIMESTAMP=self.TIMESTAMP)


@DATACLASS(FROZEN=True)
class StateSnapshot(Generic[T]):
    """Immutable snapshot of state at a point in time."""
    state_id: str
    data: T
    parent_id: Optional[str] = None
    transition: Optional[StateTransition[T]] = None
    TIMESTAMP: DATETIME = field(
        default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, object] = field(default_factory=dict)

    def get_hash(self) -> str:
        """Generate a deterministic hash of this snapshot."""
        DATA = {'state_id': self.state_id,
                'data': self.data,
                'parent_id': self.parent_id,
                'TIMESTAMP': self.TIMESTAMP.isoformat()}
        if self.transition:
            DATA['TRANSITION'] = {'operation': self.transition.operation.value,
                                  'path': str(self.transition.path),
                                  'value': self.transition.value}
        return hashlib.sha256(json.dumps(DATA, sort_keys=True).encode()).hexdigest()