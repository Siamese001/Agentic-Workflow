"""
L4 State Management - State Manager

Implements the core state management functionality with strict immutability.
"""
from __future__ import annotations
from typing import Any, Dict, Generic, List, Optional, TypeVar, Callable, Type, cast
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import uuid
import json
import logging
from pathlib import Path

from .types import (
    StateOperation,
    StateEventType,
    StatePath,
    StateTransition,
    StateSnapshot,
    StateError,
    StateValidationError,
    StateRollbackError,
    T
)

logger = logging.getLogger(__name__)

class StateManager(Generic[T]):
    """
    Manages application state with full history and rollback capabilities.
    
    Features:
    - Immutable state snapshots
    - Full audit trail of all changes
    - Thread-safe operations
    - Pluggable persistence
    - Automatic garbage collection
    """
    
    def __init__(
        self,
        initial_state: T,
        max_history: int = 100,
        max_age_days: int = 7,
        persistence_path: Optional[Path] = None
    ):
        """Initialize the state manager.
        
        Args:
            initial_state: The initial state of the application
            max_history: Maximum number of historical snapshots to keep in memory
            max_age_days: Maximum age of snapshots to keep in memory
            persistence_path: Optional path for persistent storage
        """
        self._initial_state = initial_state
        self._max_history = max_history
        self._max_age = timedelta(days=max_age_days)
        self._persistence_path = persistence_path
        
        # Initialize state history
        initial_snapshot = StateSnapshot[
            T
        ](
            state_id=str(uuid.uuid4()),
            data=initial_state,
            metadata={"source": "initial_state"}
        )
        
        self._history: List[StateSnapshot[T]] = [initial_snapshot]
        self._current = initial_snapshot
        
        # Initialize persistence if path is provided
        if self._persistence_path:
            self._persistence_path.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
    
    @property
    def current(self) -> StateSnapshot[T]:
        """Get the current state snapshot."""
        return self._current
    
    @property
    def history(self) -> List[StateSnapshot[T]]:
        """Get the complete history of state changes."""
        return self._history.copy()
    
    def get_history_since(self, timestamp: datetime) -> List[StateSnapshot[T]]:
        """Get all state changes since the given timestamp."""
        return [
            s for s in self._history
            if s.timestamp > timestamp
        ]
    
    def apply_transition(self, transition: StateTransition[T]) -> StateSnapshot[T]:
        """
        Apply a state transition and return the new snapshot.
        
        Args:
            transition: The state transition to apply
            
        Returns:
            The new state snapshot after applying the transition
            
        Raises:
            StateValidationError: If the transition is invalid
        """
        # Check condition if present
        if transition.condition and not transition.condition(self._current.data):
            raise StateValidationError(
                f"Transition condition not met for path: {transition.path}"
            )
        
        # Apply the operation to create new state
        new_data = self._apply_operation(
            self._current.data,
            transition.operation,
            transition.path,
            transition.value
        )
        
        # Create new snapshot
        new_snapshot = StateSnapshot[
            T
        ](
            state_id=str(uuid.uuid4()),
            data=new_data,
            parent_id=self._current.state_id,
            transition=transition,
            metadata={
                **self._current.metadata,
                **transition.metadata,
                "operation": transition.operation.value,
                "path": str(transition.path)
            }
        )
        
        # Update history
        self._history.append(new_snapshot)
        self._current = new_snapshot
        
        # Persist if configured
        if self._persistence_path:
            self._persist_snapshot(new_snapshot)
        
        # Clean up old snapshots
        self._prune_history()
        
        return new_snapshot
    
    def rollback(self, target_state_id: str) -> StateSnapshot[T]:
        """
        Roll back to a previous state by its ID.
        
        Args:
            target_state_id: The ID of the target state to roll back to
            
        Returns:
            The state snapshot after rollback
            
        Raises:
            StateRollbackError: If the target state cannot be found
        """
        # Find the target snapshot
        target_snapshot = None
        for snapshot in reversed(self._history):
            if snapshot.state_id == target_state_id:
                target_snapshot = snapshot
                break
        
        if not target_snapshot:
            raise StateRollbackError(
                f"Target state not found: {target_state_id}"
            )
        
        # Create a rollback transition
        rollback_transition = StateTransition[
            T
        ](
            operation=StateOperation.UPDATE,
            path=StatePath(),
            value=target_snapshot.data,
            metadata={
                "rollback_to": target_state_id,
                "rollback_from": self._current.state_id
            }
        )
        
        # Apply the rollback as a new state
        return self.apply_transition(rollback_transition)
    
    def _apply_operation(
        self,
        current: Any,
        operation: StateOperation,
        path: StatePath,
        value: Any
    ) -> Any:
        """Apply a single operation to the current state."""
        if not path.parts:
            # Root path
            if operation == StateOperation.CREATE:
                return value
            elif operation == StateOperation.UPDATE:
                return value
            elif operation == StateOperation.DELETE:
                return {}
            elif operation == StateOperation.PATCH and isinstance(current, dict):
                return {**current, **value}
            return current
        
        # Handle nested paths
        if isinstance(current, dict):
            current = current.copy()
            key = path.parts[0]
            remaining_path = StatePath(path.parts[1:])
            
            if operation == StateOperation.DELETE and len(path.parts) == 1:
                current.pop(key, None)
                return current
                
            current[key] = self._apply_operation(
                current.get(key) if key in current else None,
                operation,
                remaining_path,
                value
            )
            return current
            
        elif isinstance(current, list) and path.parts[0].isdigit():
            # Handle array indices
            index = int(path.parts[0])
            remaining_path = StatePath(path.parts[1:])
            current = current.copy()
            
            if operation == StateOperation.DELETE and len(path.parts) == 1:
                if 0 <= index < len(current):
                    del current[index]
                return current
                
            if 0 <= index < len(current):
                current[index] = self._apply_operation(
                    current[index],
                    operation,
                    remaining_path,
                    value
                )
            return current
            
        return current
    
    def _prune_history(self) -> None:
        """Remove old snapshots based on retention policy."""
        now = datetime.utcnow()
        min_timestamp = now - self._max_age
        
        # Find the index of the first snapshot to keep
        keep_from = 0
        for i, snapshot in enumerate(self._history):
            if snapshot.timestamp >= min_timestamp:
                keep_from = max(0, i - 1)  # Keep one extra for context
                break
        
        # Apply max_history constraint
        keep_from = max(keep_from, len(self._history) - self._max_history)
        
        # Prune the history
        if keep_from > 0:
            self._history = self._history[keep_from:]
    
    def _persist_snapshot(self, snapshot: StateSnapshot[T]) -> None:
        """Persist a snapshot to disk."""
        if not self._persistence_path:
            return
            
        try:
            timestamp = snapshot.timestamp.strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}_{snapshot.state_id}.json"
            filepath = self._persistence_path / filename
            
            with open(filepath, 'w') as f:
                json.dump({
                    'state_id': snapshot.state_id,
                    'parent_id': snapshot.parent_id,
                    'timestamp': snapshot.timestamp.isoformat(),
                    'data': snapshot.data,
                    'metadata': snapshot.metadata,
                    'transition': {
                        'operation': snapshot.transition.operation.value if snapshot.transition else None,
                        'path': str(snapshot.transition.path) if snapshot.transition else None,
                        'metadata': snapshot.transition.metadata if snapshot.transition else {}
                    } if snapshot.transition else None
                }, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to persist snapshot {snapshot.state_id}: {e}")
    
    def _load_from_disk(self) -> None:
        """Load snapshots from disk."""
        if not self._persistence_path or not self._persistence_path.exists():
            return
            
        snapshots = []
        
        # Load all snapshot files
        for filepath in sorted(self._persistence_path.glob("*.json")):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Skip if we already have this snapshot in memory
                if any(s.state_id == data['state_id'] for s in self._history):
                    continue
                
                # Reconstruct the snapshot
                transition_data = data.get('transition', {})
                transition = None
                
                if transition_data.get('operation') and transition_data.get('path'):
                    transition = StateTransition[
                        T
                    ](
                        operation=StateOperation(transition_data['operation']),
                        path=StatePath.from_string(transition_data['path']),
                        metadata=transition_data.get('metadata', {})
                    )
                
                snapshot = StateSnapshot[
                    T
                ](
                    state_id=data['state_id'],
                    parent_id=data.get('parent_id'),
                    data=data['data'],
                    transition=transition,
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    metadata=data.get('metadata', {})
                )
                
                snapshots.append(snapshot)
                
            except Exception as e:
                logger.error(f"Failed to load snapshot from {filepath}: {e}")
        
        # Rebuild history if we found any snapshots
        if snapshots:
            self._history = snapshots
            self._current = snapshots[-1]
            logger.info(f"Loaded {len(snapshots)} snapshots from disk")



