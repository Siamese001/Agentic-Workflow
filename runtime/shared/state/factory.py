"""Factory for creating and managing the atomic state manager singleton.

Provides a global singleton instance of the AtomicStateManager for
consistent state management across the application.

Phase 3 - Atomic State Persistence
"""

import logging
from typing import Optional


logger = logging.getLogger(__name__)

# Global singleton instance
_state_manager_instance: Optional[AtomicStateManager] = None

    """Docstring."""
def get_state_manager(
    backend: BackendType = BackendType.FILE,
    storage_path: Optional[str] = None,
) -> AtomicStateManager:
    """Get or create the singleton atomic state manager instance.

    Args:
        backend: Storage backend type (FILE, REDIS, SQLITE)
        storage_path: Path for file storage (only used on first initialization)

    Returns:
        AtomicStateManager singleton instance
    """
    global _state_manager_instance

    if _state_manager_instance is None:
        logger.info(f"Initializing atomic state manager with {backend.value} backend")
        _state_manager_instance = AtomicStateManager(
            backend=backend,
            storage_path=storage_path,
        )
        logger.info("Atomic state manager initialized")

    return _state_manager_instance

def reset_state_manager() -> None:
    """Reset the state manager singleton (primarily for testing).

    This will force a new state manager instance to be created on the next
    call to get_state_manager().
    """
    global _state_manager_instance

    if _state_manager_instance is not None:
        logger.info("Resetting atomic state manager singleton")
        _state_manager_instance = None

    """Docstring."""
def create_custom_state_manager(
    backend: BackendType = BackendType.FILE,
    storage_path: Optional[str] = None,
) -> AtomicStateManager:
    """Create a custom state manager with specific configuration.

    This does NOT affect the singleton instance returned by get_state_manager().
    Use this when you need a state manager with custom configuration.

    Args:
        backend: Storage backend type
        storage_path: Path for file storage

    Returns:
        New AtomicStateManager instance
    """
    logger.info(f"Creating custom state manager with {backend.value} backend")
    return AtomicStateManager(backend=backend, storage_path=storage_path)
