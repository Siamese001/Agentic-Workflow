"""Atomic state persistence with ACID guarantees.

Provides transactional state management for workflow checkpointing with
two-phase commit to ensure zero data loss.

Phase 3 - Atomic State Persistence
"""

from .schema import WorkflowState, BackendType, CheckpointMetadata
from .atomic_manager import AtomicStateManager, StatePersistenceError
from .factory import get_state_manager, reset_state_manager

__all__ = [
    "WorkflowState",
    "BackendType",
    "CheckpointMetadata",
    "AtomicStateManager",
    "StatePersistenceError",
    "get_state_manager",
    "reset_state_manager",
]
