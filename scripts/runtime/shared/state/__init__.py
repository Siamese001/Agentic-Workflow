"""Atomic state persistence with ACID guarantees.


logger = logging.getLogger(__name__)
Provides transactional state management for workflow checkpointing with
two-phase commit to ensure zero data loss.

Phase 3 - Atomic State Persistence
"""


__all__ = [
    "WorkflowState",
    "BackendType",
    "CheckpointMetadata",
    "AtomicStateManager",
    "StatePersistenceError",
    "get_state_manager",
    "reset_state_manager",
]
