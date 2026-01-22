"""Atomic State Manager with ACID guarantees.

Implements two-phase commit for workflow state persistence to ensure zero data loss.
Uses shadow files/keys for isolation and atomic swap operations.

Phase 3 - Atomic State Persistence
"""

import logging
import os
import time



logger = logging.getLogger(__name__)


class StatePersistenceError(Exception):
    """Raised when state persistence operations fail."""

    pass


class AtomicStateManager:
    """Atomic state manager with ACID guarantees.

    Implements two-phase commit protocol:
    1. ISOLATION: Write to shadow location
    2. ATOMIC SWAP: Replace active state with shadow
    3. CLEANUP: Remove shadow after successful commit

    This ensures that state is never corrupted - either the new state
    is fully committed or the old state remains intact.
    """

    def __init__(
        self,
        backend: BackendType = BackendType.FILE,
        storage_path: str | None = None,
        telemetry: SystemTelemetry | None = None,
    ):
        """Initialize atomic state manager.

        Args:
            backend: Storage backend type (FILE, REDIS, SQLITE)
            storage_path: Path for file storage (required for FILE backend)
            telemetry: Optional telemetry instance
        """
        self.backend = backend
        self.telemetry = telemetry or get_telemetry()

        # Initialize backend-specific storage
        if backend == BackendType.FILE:
            if not storage_path:
                storage_path = os.path.join(os.getcwd(), ".workflow_state")
            self.storage_path = Path(storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized FILE backend at: {self.storage_path}")
        elif backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")
        else:
            raise ValueError(f"Unknown backend type: {backend}")

    def checkpoint(
        self,
        workflow_id: str,
        new_state: WorkflowState,
    ) -> CheckpointMetadata:
        """Atomically checkpoint workflow state using two-phase commit.

        This method guarantees that either:
        - The new state is fully committed and becomes active, OR
        - The old state remains intact and unchanged

        There is no intermediate state where the checkpoint is partially written.

        Args:
            workflow_id: Unique workflow identifier
            new_state: New workflow state to checkpoint

        Returns:
            CheckpointMetadata with operation details

        Raises:
            StatePersistenceError: If checkpoint fails
        """
        start_time = time.time()
        checkpoint_id = f"{workflow_id}_{int(time.time() * 1000)}"

        try:
            # PHASE 1: ISOLATION - Write to shadow location
            logger.info(f"Starting atomic checkpoint for workflow: {workflow_id}")
            shadow_key = self._get_shadow_key(workflow_id)
            self._write_to_backend(shadow_key, new_state)
            logger.debug(f"Phase 1 complete: Shadow state written to {shadow_key}")

            # PHASE 2: ATOMIC SWAP - Replace active with shadow
            active_key = self._get_active_key(workflow_id)
            self._atomic_swap(shadow_key, active_key)
            logger.debug("Phase 2 complete: Atomic swap successful")

            # PHASE 3: CLEANUP - Transaction complete
            # Note: Shadow file is now the active file after rename
            # No cleanup needed for file backend

            # Calculate duration and log success
            duration_ms = (time.time() - start_time) * 1000

            metadata = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                workflow_id=workflow_id,
                k_node_index=new_state.current_k_node,
                k_node_name=new_state.get_last_execution().k_node_name
                if new_state.get_last_execution()
                else "init",
                success=True,
                duration_ms=duration_ms,
            )

            self.telemetry.log_success(
                component="atomic_state_manager",
                operation="checkpoint",
                latency_ms=duration_ms,
                metadata={
                    "workflow_id": workflow_id,
                    "checkpoint_id": checkpoint_id,
                    "k_node_index": new_state.current_k_node,
                },
            )

            logger.info(
                f"Atomic checkpoint complete for {workflow_id} "
                f"(K-Node {new_state.current_k_node}) in {duration_ms:.2f}ms"
            )

            return metadata

        except Exception as e:
            # ROLLBACK: If swap fails, old state remains intact
            duration_ms = (time.time() - start_time) * 1000

            logger.error(f"Atomic checkpoint failed for {workflow_id}: {e}")

            # Cleanup shadow file if it exists
            try:
                shadow_key = self._get_shadow_key(workflow_id)
                self._delete_from_backend(shadow_key)
                logger.debug("Cleaned up shadow state after failure")
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup shadow state: {cleanup_error}")

            metadata = CheckpointMetadata(
                checkpoint_id=checkpoint_id,
                workflow_id=workflow_id,
                k_node_index=new_state.current_k_node,
                k_node_name=new_state.get_last_execution().k_node_name
                if new_state.get_last_execution()
                else "init",
                success=False,
                error_message=str(e),
                duration_ms=duration_ms,
            )

            self.telemetry.log_failure(
                component="atomic_state_manager",
                operation="checkpoint",
                latency_ms=duration_ms,
                error_type=e.__class__.__name__,
                error_message=str(e),
                metadata={"workflow_id": workflow_id},
            )

            raise StatePersistenceError(f"Failed to commit state for {workflow_id}: {e}") from e

    def resume_workflow(self, workflow_id: str) -> WorkflowState | None:
        """Resume workflow from last valid checkpoint.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState if checkpoint exists, None otherwise
        """
        logger.info(f"Attempting to resume workflow: {workflow_id}")
        return self._load_state(workflow_id)

    def get_active_checkpoint(self, workflow_id: str) -> WorkflowState | None:
        """Get the current active checkpoint for a workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState if exists, None otherwise
        """
        return self._load_state(workflow_id)

    def delete_checkpoint(self, workflow_id: str) -> bool:
        """Delete checkpoint for a workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            True if deleted, False if not found
        """
        try:
            active_key = self._get_active_key(workflow_id)
            self._delete_from_backend(active_key)
            logger.info(f"Deleted checkpoint for workflow: {workflow_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to delete checkpoint for {workflow_id}: {e}")
            return False

    def list_checkpoints(self) -> dict[str, WorkflowState]:
        """List all available checkpoints.

        Returns:
            Dictionary mapping workflow_id to WorkflowState
        """
        checkpoints = {}

        if self.backend == BackendType.FILE:
            for file_path in self.storage_path.glob("*.json"):
                # Skip shadow files
                if file_path.stem.endswith("_shadow"):
                    continue

                workflow_id = file_path.stem
                try:
                    state = self._load_state(workflow_id)
                    if state:
                        checkpoints[workflow_id] = state
                except Exception as e:
                    logger.warning(f"Failed to load checkpoint {workflow_id}: {e}")

        return checkpoints

    # Backend-specific methods

    def _get_active_key(self, workflow_id: str) -> str:
        """Get the active storage key for a workflow."""
        if self.backend == BackendType.FILE:
            return str(self.storage_path / f"{workflow_id}.json")
        elif self.backend == BackendType.REDIS:
            return f"workflow:{workflow_id}"
        elif self.backend == BackendType.SQLITE:
            return workflow_id
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _get_shadow_key(self, workflow_id: str) -> str:
        """Get the shadow storage key for a workflow."""
        if self.backend == BackendType.FILE:
            return str(self.storage_path / f"{workflow_id}_shadow.json")
        elif self.backend == BackendType.REDIS:
            return f"workflow:{workflow_id}:shadow"
        elif self.backend == BackendType.SQLITE:
            return f"{workflow_id}_shadow"
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    def _write_to_backend(self, key: str, state: WorkflowState) -> None:
        """Write state to backend storage.

        Args:
            key: Storage key
            state: Workflow state to write
        """
        if self.backend == BackendType.FILE:
            # Write to file with fsync for durability
            file_path = Path(key)
            temp_path = file_path.with_suffix(".tmp")

            # Write to temp file first
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(state.to_json())
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk

            # Rename temp to final (atomic on POSIX)
            os.replace(temp_path, file_path)

        elif self.backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif self.backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")

    def _atomic_swap(self, shadow_key: str, active_key: str) -> None:
        """Atomically swap shadow state with active state.

        This is the critical operation that ensures atomicity.
        os.replace() is atomic on both POSIX and Windows.

        Args:
            shadow_key: Shadow storage key
            active_key: Active storage key
        """
        if self.backend == BackendType.FILE:
            # os.replace() is atomic on both POSIX and Windows
            # It will replace active_key if it exists
            os.replace(shadow_key, active_key)

        elif self.backend == BackendType.REDIS:
            # Redis RENAME is atomic
            raise NotImplementedError("Redis backend not yet implemented")
        elif self.backend == BackendType.SQLITE:
            # SQLite transaction with UPDATE
            raise NotImplementedError("SQLite backend not yet implemented")

    def _load_state(self, workflow_id: str) -> WorkflowState | None:
        """Load state from backend storage.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            WorkflowState if exists, None otherwise
        """
        try:
            active_key = self._get_active_key(workflow_id)

            if self.backend == BackendType.FILE:
                file_path = Path(active_key)
                if not file_path.exists():
                    logger.debug(f"No checkpoint found for workflow: {workflow_id}")
                    return None

                with open(file_path, encoding="utf-8") as f:
                    json_data = f.read()

                state = WorkflowState.from_json(json_data)
                logger.info(
                    f"Loaded checkpoint for {workflow_id} "
                    f"(K-Node {state.current_k_node}/{state.total_k_nodes})"
                )
                return state

            elif self.backend == BackendType.REDIS:
                raise NotImplementedError("Redis backend not yet implemented")
            elif self.backend == BackendType.SQLITE:
                raise NotImplementedError("SQLite backend not yet implemented")

        except Exception as e:
            logger.error(f"Failed to load state for {workflow_id}: {e}")
            raise StatePersistenceError(f"Failed to load state: {e}") from e

    def _delete_from_backend(self, key: str) -> None:
        """Delete state from backend storage.

        Args:
            key: Storage key
        """
        if self.backend == BackendType.FILE:
            file_path = Path(key)
            if file_path.exists():
                file_path.unlink()
        elif self.backend == BackendType.REDIS:
            raise NotImplementedError("Redis backend not yet implemented")
        elif self.backend == BackendType.SQLITE:
            raise NotImplementedError("SQLite backend not yet implemented")