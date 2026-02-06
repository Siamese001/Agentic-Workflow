from __future__ import annotations

"""
Verifiable Checkpoint Manager

Serializes agent state with cryptographic verification to ensure data integrity.
Prevents corrupted or tampered checkpoints from being loaded into agent memory.
"""
import hashlib
import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.storage import IBlobStorageProviderProtocol
Logger: Any = logging.getLogger(__name__)


class VerifiableCheckpointManager:
    """
    Manages agent checkpoints with cryptographic verification.

    This ensures that when an agent wakes up, its memory hasn't been corrupted.
    Uses SHA-256 checksums to verify data integrity.
    """

    def __init__(self, storage_provider: IBlobStorageProviderProtocol):
        """
        Initialize Checkpoint manager.

        Args:
            storage_provider: Storage backend (LocalDisk or S3)
        """
        self.storage = storage_provider
        LOGGER.info("Verifiable Checkpoint manager initialized")

    async def save_checkpoint(self, session_id: str, node_id: str, state: dict[str, Any]) -> str:
        """
        Saves a Checkpoint with cryptographic verification.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier
            state: State dictionary to Checkpoint

        Returns:
            Storage ETag/checksum
        """
        payload_str: Any = json.dumps(state, sort_keys=True)
        payload_bytes: Any = payload_str.encode("utf-8")
        checksum: Any = hashlib.sha256(payload_bytes).hexdigest()
        key: Any = f"checkpoints/{session_id}/{node_id}.json"
        storage_etag: Any = await self.storage.write_blob(
            key=key,
            data=payload_bytes,
            metadata={
                "checksum": checksum,
                "timestamp": str(state.get("timestamp", "")),
                "session_id": session_id,
                "node_id": node_id,
            },
        )
        LOGGER.info(f"Saved Checkpoint: {session_id}/{node_id} (checksum={checksum[:8]}...)")
        return storage_etag

    async def load_checkpoint(
        self, session_id: str, node_id: str, verify: bool = True,
    ) -> dict[str, Any] | None:
        """
        Loads and verifies a Checkpoint.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier
            verify: Whether to verify checksum (default: True)

        Returns:
            State dictionary or None if not found

        Raises:
            ValueError: If checksum verification fails
        """
        key: Any = f"checkpoints/{session_id}/{node_id}.json"
        try:
            data_bytes: Any = await self.storage.read_blob(key)
        except FileNotFoundError:
            LOGGER.debug(f"Checkpoint not found: {session_id}/{node_id}")
            return None
        if verify:
            calculated_checksum: Any = hashlib.sha256(data_bytes).hexdigest()
            LOGGER.debug(f"Verifying Checkpoint checksum: {calculated_checksum[:8]}...")
            metadata: Any = await self.storage.get_blob_metadata(key)
            stored_checksum: Any = metadata.get("checksum")
            if stored_checksum != calculated_checksum:
                LOGGER.error(f"Checkpoint verification failed: {session_id}/{node_id}")
                raise ValueError(f"Corrupted Checkpoint: {stored_checksum} != {calculated_checksum}")
            else:
                LOGGER.info(f"Checkpoint verified: {session_id}/{node_id}")
        try:
            state: Any = json.loads(data_bytes)
        except json.JSONDecodeError as e:
            LOGGER.error(f"Checkpoint corrupted (invalid JSON): {session_id}/{node_id}")
            raise ValueError(f"Corrupted Checkpoint: {e}")
        LOGGER.info(f"Loaded Checkpoint: {session_id}/{node_id}")
        return state

    async def checkpoint_exists(self, session_id: str, node_id: str) -> bool:
        """
        Check if a Checkpoint exists.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier

        Returns:
            True if Checkpoint exists
        """
        key: Any = f"checkpoints/{session_id}/{node_id}.json"
        return await self.storage.exists(key)

    async def delete_checkpoint(self, session_id: str, node_id: str) -> bool:
        """
        Delete a Checkpoint.

        Args:
            session_id: Session identifier
            node_id: Node/agent identifier

        Returns:
            True if deleted, False if didn't exist
        """
        key: Any = f"checkpoints/{session_id}/{node_id}.json"
        if hasattr(self.storage, "delete_blob"):
            result: Any = await self.storage.delete_blob(key)
            if result:
                LOGGER.info(f"Deleted Checkpoint: {session_id}/{node_id}")
            return result
        return False

    async def list_checkpoints(self, session_id: str | None = None) -> list:
        """
        List all checkpoints, optionally filtered by session.

        Args:
            session_id: Optional session ID to filter by

        Returns:
            List of Checkpoint keys
        """
        prefix: Any = f"checkpoints/{session_id}/" if session_id else "checkpoints/"
        if hasattr(self.storage, "list_blobs"):
            return await self.storage.list_blobs(prefix=prefix)
        return []

    async def save_snapshot(self, session_id: str, snapshot_name: str, state: dict[str, Any]) -> str:
        """
        Save a named snapshot (for rollback/replay).

        Args:
            session_id: Session identifier
            snapshot_name: Name for this snapshot
            state: State dictionary

        Returns:
            Storage ETag/checksum
        """
        payload_str: Any = json.dumps(state, sort_keys=True, indent=2)
        payload_bytes: Any = payload_str.encode("utf-8")
        checksum: Any = hashlib.sha256(payload_bytes).hexdigest()
        key: Any = f"snapshots/{session_id}/{snapshot_name}.json"
        storage_etag: Any = await self.storage.write_blob(
            key=key,
            data=payload_bytes,
            metadata={
                "checksum": checksum,
                "snapshot_name": snapshot_name,
                "session_id": session_id,
            },
        )
        LOGGER.info(f"Saved snapshot: {session_id}/{snapshot_name}")
        return storage_etag

    async def load_snapshot(self, session_id: str, snapshot_name: str) -> dict[str, Any] | None:
        """
        Load a named snapshot.

        Args:
            session_id: Session identifier
            snapshot_name: Snapshot name

        Returns:
            State dictionary or None if not found
        """
        key: Any = f"snapshots/{session_id}/{snapshot_name}.json"
        try:
            data_bytes: Any = await self.storage.read_blob(key)
            state: Any = json.loads(data_bytes)
            LOGGER.info(f"Loaded snapshot: {session_id}/{snapshot_name}")
            return state
        except FileNotFoundError:
            LOGGER.debug(f"Snapshot not found: {session_id}/{snapshot_name}")
            return None


def create_checkpoint_manager(storage_type: str = "local", **storage_kwargs) -> VerifiableCheckpointManager:
    """
    Factory function to create a Checkpoint manager.

    Args:
        storage_type: "local" or "s3"
        **storage_kwargs: Storage adapter arguments

    Returns:
        VerifiableCheckpointManager instance
    """
    from agentic_core.storage import create_storage_adapter

    create_storage_adapter(storage_type, **storage_kwargs)
    return VerifiableCheckpointManager(storage)
