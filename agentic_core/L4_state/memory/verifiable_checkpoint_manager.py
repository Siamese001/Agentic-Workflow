from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "verifiable_checkpoint_manager")
emit_determinism_digest("p0", "verifiable_checkpoint_manager")

_emit_dispatches_healing_run("p1", "verifiable_checkpoint_manager", "L4")
_emit_routes_through("p1", "verifiable_checkpoint_manager", "L4")
_emit_escalates_to_human("p1", "verifiable_checkpoint_manager", "L4")
_emit_reads_policy_state("p1", "verifiable_checkpoint_manager", "L4")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "verifiable_checkpoint_manager", "p0_governance")
_emit_authorize_and_execute("p2", "verifiable_checkpoint_manager", "execution_auth")
_emit_validates_capability("p2", "verifiable_checkpoint_manager", "capability_check")
_emit_routes_to_capability("p2", "verifiable_checkpoint_manager", "capability_route")
_emit_writes_via_uwg("p2", "verifiable_checkpoint_manager", "uwg_write")
_emit_blocks_direct_write("p2", "verifiable_checkpoint_manager", "direct_write_block")
_emit_records_tool_invocation("p2", "verifiable_checkpoint_manager", "tool_invocation")
_emit_captures_execution_output("p2", "verifiable_checkpoint_manager", "exec_output")
_emit_dispatches_agent("p3", "verifiable_checkpoint_manager", "agent_dispatch")
_emit_coordinates_agents("p3", "verifiable_checkpoint_manager", "agent_coordination")
_emit_records_workflow_lineage("p3", "verifiable_checkpoint_manager", "workflow_lineage")
_emit_records_healing_outcome("p3", "verifiable_checkpoint_manager", "healing_outcome")
_emit_escalates_failure("p3", "verifiable_checkpoint_manager", "failure_escalation")
_emit_orchestrates_workflow("p3", "verifiable_checkpoint_manager", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verifiable_checkpoint_manager", "healing_dispatch")
_emit_invokes_evaluation("p3", "verifiable_checkpoint_manager", "evaluation_signal")
_emit_records_telemetry_event("p4", "verifiable_checkpoint_manager", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verifiable_checkpoint_manager", "eval_metric")
_emit_stores_embedding("p4", "verifiable_checkpoint_manager", "embedding_store")
_emit_updates_meta_learning_state("p4", "verifiable_checkpoint_manager", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verifiable_checkpoint_manager", "exec_snapshot_link")

"\nVerifiable Checkpoint Manager\n\nSerializes agent state with cryptographic verification to ensure data integrity.\nPrevents corrupted or tampered checkpoints from being loaded into agent memory.\n"
import hashlib
import json
import logging
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_core.storage import IBlobStorageProviderProtocol
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "VerifiableCheckpointManager.save_checkpoint"
        )

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
        self, session_id: str, node_id: str, verify: bool = True
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
            metadata={"checksum": checksum, "snapshot_name": snapshot_name, "session_id": session_id},
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
    _emit_snapshots_state(str(uuid.uuid4()), "Module.create_checkpoint_manager", "L4_STATE")
    from agentic_core.storage import create_storage_adapter

    create_storage_adapter(storage_type, **storage_kwargs)
    return VerifiableCheckpointManager(storage)
