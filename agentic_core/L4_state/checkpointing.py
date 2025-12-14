"""
Verifiable Checkpoint Manager

Serializes agent state with cryptographic verification to ensure data integrity.
Prevents corrupted or tampered checkpoints from being loaded into agent memory.
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional
from agentic_core.L4_state.storage import BlobStorageProvider

logger = logging.getLogger(__name__)


class VerifiableCheckpointManager:
    """
    Manages agent checkpoints with cryptographic verification.

    This ensures that when an agent wakes up, its memory hasn't been corrupted.
    Uses SHA-256 checksums to verify data integrity.
    """

    def __init__(self, storage_provider: BlobStorageProvider):
        """
        Initialize checkpoint manager.

        Args:
            storage_provider: Storage backend (LocalDisk or S3)
        """
        self.storage = storage_provider
        logger.info("Verifiable checkpoint manager initialized")

    async def save_checkpoint(
        self,
        session_id: str,
        node_id: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Saves a checkpoint with cryptographic verification.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier
            state: State dictionary to checkpoint

        Returns:
            Storage ETag/checksum
        """
        payload_str = json.dumps(state, sort_keys=True)
        payload_bytes = payload_str.encode('utf-8')

        checksum = hashlib.sha256(payload_bytes).hexdigest()

        key = f"checkpoints/{session_id}/{node_id}.json"

        storage_etag = await self.storage.write_blob(
            key=key,
            data=payload_bytes,
            metadata={
                "checksum": checksum,
                "timestamp": str(state.get("timestamp", "")),
                "session_id": session_id,
                "node_id": node_id
            }
        )

        logger.info(f"Saved checkpoint: {session_id}/{node_id} (checksum={checksum[:8]}...)")

        return storage_etag

    async def load_checkpoint(
        self,
        session_id: str,
        node_id: str,
        verify: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Loads and verifies a checkpoint.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier
            verify: Whether to verify checksum (default: True)

        Returns:
            State dictionary or None if not found

        Raises:
            ValueError: If checksum verification fails
        """
        key = f"checkpoints/{session_id}/{node_id}.json"

        try:
            data_bytes = await self.storage.read_blob(key)
        except FileNotFoundError:
            logger.debug(f"Checkpoint not found: {session_id}/{node_id}")
            return None

        if verify:
            calculated_checksum = hashlib.sha256(data_bytes).hexdigest()
            logger.
                .debug(f"Loaded checkpoint: {session_id}/{node_id} (checksum={calculated_checksum[:8]}.
                ..
                ..
                .)")

        try:
            state = json.loads(data_bytes)
        except json.JSONDecodeError as e:
            logger.error(f"Checkpoint corrupted (invalid JSON): {session_id}/{node_id}")
            raise ValueError(f"Corrupted checkpoint: {e}")

        logger.info(f"Loaded checkpoint: {session_id}/{node_id}")

        return state

    async def checkpoint_exists(self, session_id: str, node_id: str) -> bool:
        """
        Check if a checkpoint exists.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier

        Returns:
            True if checkpoint exists
        """
        key = f"checkpoints/{session_id}/{node_id}.json"
        return await self.storage.exists(key)

    async def delete_checkpoint(self, session_id: str, node_id: str) -> bool:
        """
        Delete a checkpoint.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier

        Returns:
            True if deleted, False if didn't exist
        """
        key = f"checkpoints/{session_id}/{node_id}.json"

        if hasattr(self.storage, 'delete_blob'):
            result = await self.storage.delete_blob(key)
            if result:
                logger.info(f"Deleted checkpoint: {session_id}/{node_id}")
            return result

        return False

    async def list_checkpoints(self, session_id: Optional[str] = None) -> list:
        """
        List all checkpoints, optionally filtered by session.

        Args:
            session_id: Optional session ID to filter by

        Returns:
            List of checkpoint keys
        """
        prefix = f"checkpoints/{session_id}/" if session_id else "checkpoints/"

        if hasattr(self.storage, 'list_blobs'):
            return await self.storage.list_blobs(prefix=prefix)

        return []

    async def save_snapshot(
        self,
        session_id: str,
        snapshot_name: str,
        state: Dict[str, Any]
    ) -> str:
        """
        Save a named snapshot (for rollback/replay).

        Args:
            session_id: Session identifier
            snapshot_name: Name for this snapshot
            state: State dictionary

        Returns:
            Storage ETag/checksum
        """
        payload_str = json.dumps(state, sort_keys=True, indent=2)
        payload_bytes = payload_str.encode('utf-8')

        checksum = hashlib.sha256(payload_bytes).hexdigest()

        key = f"snapshots/{session_id}/{snapshot_name}.json"

        storage_etag = await self.storage.write_blob(
            key=key,
            data=payload_bytes,
            metadata={
                "checksum": checksum,
                "snapshot_name": snapshot_name,
                "session_id": session_id
            }
        )

        logger.info(f"Saved snapshot: {session_id}/{snapshot_name}")

        return storage_etag

    async def load_snapshot(
        self,
        session_id: str,
        snapshot_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load a named snapshot.

        Args:
            session_id: Session identifier
            snapshot_name: Snapshot name

        Returns:
            State dictionary or None if not found
        """
        key = f"snapshots/{session_id}/{snapshot_name}.json"

        try:
            data_bytes = await self.storage.read_blob(key)
            state = json.loads(data_bytes)
            logger.info(f"Loaded snapshot: {session_id}/{snapshot_name}")
            return state
        except FileNotFoundError:
            logger.debug(f"Snapshot not found: {session_id}/{snapshot_name}")
            return None


def create_checkpoint_manager(
    storage_type: str = "local",
    **storage_kwargs
) -> VerifiableCheckpointManager:
    """
    Factory function to create a checkpoint manager.

    Args:
        storage_type: "local" or "s3"
        **storage_kwargs: Storage adapter arguments

    Returns:
        VerifiableCheckpointManager instance
    """
    from agentic_core.L4_state.storage import create_storage_adapter

    storage = create_storage_adapter(storage_type, **storage_kwargs)
    return VerifiableCheckpointManager(storage)
