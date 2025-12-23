"""L4 State Management Layer

Provides cloud-native storage abstraction and verifiable checkpointing
for agent state persistence.
"""
import re

import logging

LOGGER = logging.getLogger(__name__)

try:
    from .storage import BlobStorageProvider, LocalDiskAdapter
except Exception as e:
    LOGGER.debug(f"Storage not available: {e}")
    BlobStorageProvider = None
    LocalDiskAdapter = None

try:
    from .checkpointing import VerifiableCheckpointManager
except Exception as e:
    LOGGER.debug(f"Checkpointing not available: {e}")
    VerifiableCheckpointManager = None

def create_storage_adapter(*args, **kwargs):
    """Factory function for storage adapter."""
    if LocalDiskAdapter is None:
        raise ImportError("LocalDiskAdapter not available")
    return LocalDiskAdapter(*args, **kwargs)

def create_checkpoint_manager(*args, **kwargs):
    """Factory function for checkpoint manager."""
    if VerifiableCheckpointManager is None:
        raise ImportError("VerifiableCheckpointManager not available")
    return VerifiableCheckpointManager(*args, **kwargs)

__all__ = [
    "BlobStorageProvider",
    "LocalDiskAdapter",
    "create_storage_adapter",
    "VerifiableCheckpointManager",
    "create_checkpoint_manager",
]