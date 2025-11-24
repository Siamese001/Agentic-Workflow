"""
L4 - Pure State Management Layer

This layer handles all state management operations.
No business logic, tool execution, or orchestration is allowed here.
"""
from __future__ import annotations
from typing import Any, Dict, Generic, List, Optional, TypeVar, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

T = TypeVar('T')

class StateOperation(str, Enum):
    """Types of state operations."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    PATCH = "patch"

@dataclass
class StateTransition:
    """Represents a state change operation."""
    operation: StateOperation
    path: str  # Dot notation path to the state being modified
    value: Any = None
    condition: Optional[Callable[[Any], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StateSnapshot(Generic[T]):
    """Immutable snapshot of state at a point in time."""
    state_id: str
    data: T
    parent_id: Optional[str] = None
    timestamp: float = field(default_factory=lambda: datetime.datetime.now().timestamp())
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager(Generic[T]):
    """Manages state with full history and rollback capabilities."""
    
    def __init__(self, initial_state: T):
        self._current: StateSnapshot[T] = StateSnapshot(
            state_id=str(uuid.uuid4()),
            data=initial_state
        )
        self._history: List[StateSnapshot[T]] = [self._current]
    
    @property
    def current(self) -> StateSnapshot[T]:
        """Get the current state snapshot."""
        return self._current
    
    def get_history(self) -> List[StateSnapshot[T]]:
        """Get the complete history of state changes."""
        return self._history.copy()
    
    def apply_transition(self, transition: StateTransition) -> StateSnapshot[T]:
        """Apply a state transition and return the new snapshot."""
        new_data = self._apply_to_state(
            self._current.data,
            transition.path,
            transition.operation,
            transition.value
        )
        
        new_snapshot = StateSnapshot(
            state_id=str(uuid.uuid4()),
            data=new_data,
            parent_id=self._current.state_id,
            metadata={
                **self._current.metadata,
                **transition.metadata,
                'operation': transition.operation.value,
                'path': transition.path
            }
        )
        
        self._current = new_snapshot
        self._history.append(new_snapshot)
        return new_snapshot
    
    def rollback(self, target_state_id: str) -> Optional[StateSnapshot[T]]:
        """Roll back to a previous state by its ID."""
        for snapshot in reversed(self._history):
            if snapshot.state_id == target_state_id:
                self._current = snapshot
                return snapshot
        return None
    
    def _apply_to_state(
        self, 
        state: Any, 
        path: str, 
        operation: StateOperation,
        value: Any = None
    ) -> Any:
        """Apply an operation to a nested state object."""
        # Implementation of state patching logic
        # This is a simplified version - a real implementation would:
        # - Handle nested paths (e.g., "user.profile.name")
        # - Support different patch strategies
        # - Handle edge cases and errors
        if operation == StateOperation.CREATE:
            return value
        elif operation == StateOperation.READ:
            return self._get_nested(state, path)
        elif operation == StateOperation.UPDATE:
            return self._set_nested(state, path, value)
        elif operation == StateOperation.DELETE:
            return self._delete_nested(state, path)
        elif operation == StateOperation.PATCH:
            current = self._get_nested(state, path)
            if isinstance(current, dict) and isinstance(value, dict):
                return {**current, **value}
            return value
        
        raise ValueError(f"Unsupported operation: {operation}")
    
    def _get_nested(self, obj: Any, path: str) -> Any:
        """Get a value from a nested object using dot notation."""
        for part in path.split('.'):
            if isinstance(obj, dict):
                obj = obj.get(part)
            else:
                obj = getattr(obj, part, None)
            if obj is None:
                break
        return obj
    
    def _set_nested(self, obj: Any, path: str, value: Any) -> Any:
        """Set a value in a nested object using dot notation."""
        # Implementation left as an exercise
        # Should handle creating intermediate dictionaries/objects as needed
        pass
    
    def _delete_nested(self, obj: Any, path: str) -> Any:
        """Delete a value from a nested object using dot notation."""
        # Implementation left as an exercise
        pass

# Re-export public interfaces
__all__ = [
    'StateOperation',
    'StateTransition',
    'StateSnapshot',
    'StateManager',
]
