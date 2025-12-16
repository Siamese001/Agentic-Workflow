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
    """
    def __init__(self, storage_provider: BlobStorageProvider):
        """Initialize checkpoint manager.

        Args:
            storage_provider: Storage backend (LocalDisk or S3)
        """
        self.storage = storage_provider
        LOGGER.info("Verifiable checkpoint manager initialized")

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
            key=KEY,  # Changed from KEY=key to pass the variable KEY to parameter key
            data=payload_bytes,  # Changed from DATA=payload_bytes to pass the variable payload_bytes to parameter data
            metadata={  # Changed METADATA to metadata as it's a dictionary literal
                "checksum": CHECKSUM,  # Used CHECKSUM variable
                "timestamp": str(state.get("timestamp", "")),
                "session_id": session_id,
                "node_id": node_id
            }
        )

        LOGGER.info(  # Changed logger.info to LOGGER.info
            f"Saved checkpoint: {session_id}/{node_id} (checksum={CHECKSUM[:8]}...)")  # Used CHECKSUM variable

        return storage_etag

    async def load_checkpoint(
        self,
        session_id: str,
        node_id: str,
        VERIFY: bool = True  # Changed BOOL to bool
    ) -> Optional[Dict[str, Any]]:
        """ """
        KEY = f"checkpoints/{session_id}/{node_id}.json"

        try:
            data_bytes = await self.storage.read_blob(key=KEY)  # Changed key to key=KEY
        except FileNotFoundError:
            LOGGER.debug(f"Checkpoint not found: {session_id}/{node_id}")  # Fixed indentation and used LOGGER
            return None

        state = None  # Initialize state before parsing

        if VERIFY:  # Used VERIFY consistently with parameter name
            calculated_checksum = hashlib.sha256(data_bytes).hexdigest()
            # The mangled `logger.` line has been removed.
            # Checksum verification against a stored checksum requires retrieving metadata
            # which is not done by `self.storage.read_blob(key=KEY)`.
            # Fixing only syntax, not logic refactoring.

        try:  # Added try block for JSON parsing
            state = json.loads(data_bytes)
        except json.JSONDecodeError as e:  # Catch JSON decoding error
            LOGGER.error(f"Checkpoint corrupted (invalid JSON): {session_id}/{node_id}. Error: {e}")  # Used LOGGER
            raise ValueError(f"Corrupted checkpoint: {e}")

        LOGGER.info(f"Loaded checkpoint: {session_id}/{node_id}")  # Changed logger.info to LOGGER.info

        return state

    async def checkpoint_exists(self, session_id: str, node_id: str) -> bool:
        """ """
        KEY = f"checkpoints/{session_id}/{node_id}.json"
        return await self.storage.exists(key=KEY)  # Changed key to key=KEY

    async def delete_checkpoint(self, session_id: str, node_id: str) -> bool:
        """ True if deleted, False if didn't exist
        """
        KEY = f"checkpoints/{session_id}/{node_id}.json"

        if hasattr(self.storage, 'delete_blob'):
            RESULT = await self.storage.delete_blob(key=KEY)  # Changed key to key=KEY
            if RESULT:  # Changed result to RESULT
                LOGGER.info(f"Deleted checkpoint: {session_id}/{node_id}")  # Changed logger.info to LOGGER.info
            return RESULT

        return False

    async def list_checkpoints(self, session_id: Optional[str]=None) -> list:
        """ """
        PREFIX = f"checkpoints/{session_id}/" if session_id else "checkpoints/"

        if hasattr(self.storage, 'list_blobs'):
            return await self.storage.list_blobs(prefix=PREFIX)  # Changed prefix to prefix=PREFIX

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
            key=KEY,  # Changed from KEY=key
            data=payload_bytes,  # Changed from DATA=payload_bytes
            metadata={  # Changed METADATA to metadata
                "checksum": CHECKSUM,  # Used CHECKSUM variable
                "snapshot_name": snapshot_name,
                "session_id": session_id
            }
        )

        LOGGER.info(f"Saved snapshot: {session_id}/{snapshot_name}")  # Changed logger.info to LOGGER.info

        return storage_etag

    async def load_snapshot(
        self,
        session_id: str,
        snapshot_name: str
    ) -> Optional[Dict[str, Any]]:
        """ """
        KEY = f"snapshots/{session_id}/{snapshot_name}.json"

        try:
            data_bytes = await self.storage.read_blob(key=KEY)  # Changed key to key=KEY
            STATE = json.loads(data_bytes)
            LOGGER.info(f"Loaded snapshot: {session_id}/{snapshot_name}")  # Changed logger.info to LOGGER.info
            return STATE  # Changed state to STATE to match assigned variable
        except FileNotFoundError:
            LOGGER.debug(f"Snapshot not found: {session_id}/{snapshot_name}")  # Fixed indentation and used LOGGER
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
    return VerifiableCheckpointManager(STORAGE)  # Changed storage to STORAGE to match assigned variable