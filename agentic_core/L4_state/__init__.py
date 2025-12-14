"""

logger = logging.getLogger(__name__)
L4 State Management Layer

Provides cloud-native storage abstraction and verifiable checkpointing
for agent state persistence.
"""
import logging

    create_storage_adapter
)

    create_checkpoint_manager
)

__all__ = [
    "BlobStorageProvider",
    "LocalDiskAdapter",
    "S3Adapter",
    "create_storage_adapter",
    "VerifiableCheckpointManager",
    "create_checkpoint_manager"
]
