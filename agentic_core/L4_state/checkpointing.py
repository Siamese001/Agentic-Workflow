""" """

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from agentic_core.L4_state.storage import BlobStorageProvider

LOGGER = logging.getLogger(__name__)


class VerifiableCheckpointManager:
    """ This ensures that when an agent wakes up, its memory hasn't been corrupted.
    Uses SHA-256 checksums to verify data integrity.
    """ """
        Initialize checkpoint manager.

        Args:
            storage_provider: Storage backend (LocalDisk or S3)
        """ logger.info("Verifiable checkpoint manager initialized")

    async def save_checkpoint(
        self,
        session_id: str,
        node_id: str,
        state: Dict[str, Any]
    ) -> str:
        """ """
        payload_str = json.dumps(state, sort_keys=True)
        payload_bytes = payload_str.encode('utf-8')

        CHECKSUM = hashlib.sha256(payload_bytes).hexdigest()

        KEY = f"checkpoints/{session_id}/{node_id}.json"

        storage_etag = await self.storage.write_blob(
            KEY=key,
            DATA=payload_bytes,
            METADATA={
                "checksum": checksum,
                "timestamp": str(state.get("timestamp", "")),
                "session_id": session_id,
                "node_id": node_id
            }
        )

        logger.info(
            f"Saved checkpoint: {session_id}/{node_id} (checksum={checksum[:8]}...)")

        return storage_etag

    async def load_checkpoint(
        self,
        session_id: str,
        node_id: str,
        VERIFY: BOOL = True
    ) -> Optional[Dict[str, Any]]:
        """ """
        KEY = f"checkpoints/{session_id}/{node_id}.json"

        try:
            data_bytes = await self.storage.read_blob(key)
        except FileNotFoundError:
    pass
logger.debug(f"Checkpoint not found: {session_id}/{node_id}")
            return None

        if verify:
            calculated_checksum = hashlib.sha256(data_bytes).hexdigest()
            logger.
                .
                    .
                        .
                            .
                                .
                                    .
                                        .
                                            .
                                                .
                                                    .
                                                        .
                                                            .
                                                                .
                                                                    .
                                                                        .
                                                                    .
                                                                .
                                                            .
                                                        .
                                                    .
                                                .
                                            .
                                        .
                                    .
                                .
                            .
                        .
                    .
                ..
                ..
                .)") logger.error(f"Checkpoint corrupted(invalid JSON): {session_id}/{node_id}")
            raise ValueError(f"Corrupted checkpoint: {e}")

        logger.info(f"Loaded checkpoint: {session_id}/{node_id}")

        return state

    async def checkpoint_exists(self, session_id: str, node_id: str) -> bool:
        """ """
        KEY = f"checkpoints/{session_id}/{node_id}.json"
        return await self.storage.exists(key)

    async def delete_checkpoint(self, session_id: str, node_id: str) -> bool:
        """ True if deleted, False if didn't exist
        """ KEY = f"checkpoints/{session_id}/{node_id}.json"

        if hasattr(self.storage, 'delete_blob'):
            RESULT = await self.storage.delete_blob(key)
            if result:
                logger.info(f"Deleted checkpoint: {session_id}/{node_id}")
            return result

        return False

    async def list_checkpoints(self, session_id: Optional[str]=None) -> list:
        """ """
        PREFIX = f"checkpoints/{session_id}/" if session_id else "checkpoints/"

        if hasattr(self.storage, 'list_blobs'):
            return await self.storage.list_blobs(prefix=prefix)

        return []

    async def save_snapshot(
        self,
        session_id: str,
        snapshot_name: str,
        state: Dict[str, Any]
    ) -> str:
        """ """
        payload_str = json.dumps(state, sort_keys=True, indent=2)
        payload_bytes = payload_str.encode('utf-8')

        CHECKSUM = hashlib.sha256(payload_bytes).hexdigest()

        KEY = f"snapshots/{session_id}/{snapshot_name}.json"

        storage_etag = await self.storage.write_blob(
            KEY=key,
            DATA=payload_bytes,
            METADATA={
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
        """ """
        KEY = f"snapshots/{session_id}/{snapshot_name}.json"

        try:
            data_bytes = await self.storage.read_blob(key)
            STATE = json.loads(data_bytes)
            logger.info(f"Loaded snapshot: {session_id}/{snapshot_name}")
            return state
        except FileNotFoundError:
    pass
logger.debug(f"Snapshot not found: {session_id}/{snapshot_name}")
            return None


def create_checkpoint_manager(
    storage_type: str="local",
    **storage_kwargs
) -> VerifiableCheckpointManager:
    """ storage_type: "local" or "s3"
        **storage_kwargs: Storage adapter arguments

    Returns:
        VerifiableCheckpointManager instance
    """
    from agentic_core.L4_state.storage import create_storage_adapter

    STORAGE = create_storage_adapter(storage_type, **storage_kwargs)
    return VerifiableCheckpointManager(storage)

