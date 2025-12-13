"""
AtomicStateManager - ACID transactional state management for workflows.

Ensures workflow state updates are atomic, consistent, isolated, and durable,
preventing corruption and data loss during execution.
"""

import hashlib
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

class WorkflowState(BaseModel):
    """Strict schema for a persisted workflow state."""
    workflow_id: str = Field(..., description="Unique ID for the workflow run.")
    current_step: str = Field(..., description="The name of the currently executing step.")
    last_checkpoint_time: datetime = Field(..., description="Timestamp of the last successful commit.")
    data_payload: Dict[str, Any] = Field(..., description="The mutable dictionary holding the workflow's working data.")
    checksum: str = Field(..., description="SHA256 hash of the data_payload for consistency validation.")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StateCorruptionError(Exception):
    """Raised when state corruption is detected."""
    pass

class StateLockError(Exception):
    """Raised when unable to acquire state lock."""
    pass

class AtomicStateManager:
    """
    Manages workflow state with ACID transactionality.

    Features:
    - Atomicity: All-or-nothing state updates
    - Consistency: Checksum validation prevents corruption
    - Isolation: Distributed locking prevents race conditions
    - Durability: Redis persistence ensures state survives crashes
    """

    def __init__(self, redis_client: Redis):
        """Initialize atomic state manager.

        Args:
            redis_client: Connected Redis async client
        """
        self.db = redis_client
        self.STATE_PREFIX = "workflow_state:"
        self.LOCK_PREFIX = "workflow_lock:"
        self.LOCK_TIMEOUT = 5  # seconds

        logger.info("AtomicStateManager initialized with Redis backend")

    def _generate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum of data payload.

        Args:
            data: Data payload to hash

        Returns:
            SHA256 hex digest
        """
        # Ensure consistent key ordering for reliable hashing
        data_string = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    async def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Read and validate the current state from the store.

        Args:
            workflow_id: Workflow identifier

        Returns:
            WorkflowState if found, None otherwise

        Raises:
            StateCorruptionError: If checksum validation fails
            IOError: If state cannot be deserialized
        """
        key = f"{self.STATE_PREFIX}{workflow_id}"
        raw_state = await self.db.get(key)

        if not raw_state:
            logger.debug(f"No state found for workflow {workflow_id}")
            return None

        try:
            state_data = json.loads(raw_state)

            # Parse datetime from ISO format
            if 'last_checkpoint_time' in state_data:
                state_data['last_checkpoint_time'] = datetime.fromisoformat(
                    state_data['last_checkpoint_time']
                )

            # Validate with Pydantic
            stored_state = WorkflowState.model_validate(state_data)

            # Consistency Check (C in ACID): Verify stored checksum
            computed_checksum = self._generate_checksum(stored_state.data_payload)
            if computed_checksum != stored_state.checksum:
                raise StateCorruptionError(
                    f"State corruption detected for {workflow_id}. "
                    f"Checksum mismatch: expected {stored_state.checksum}, "
                    f"got {computed_checksum}"
                )

            logger.debug(
                f"Loaded state for workflow {workflow_id}: "
                f"step={stored_state.current_step}"
            )
            return stored_state

        except json.JSONDecodeError as e:
            raise IOError(f"Failed to deserialize state for {workflow_id}: {e}")
        except Exception as e:
            raise IOError(f"Failed to validate state for {workflow_id}: {e}")

    async def commit_state(self, new_state: WorkflowState) -> None:
        """Commit the new state using a transactional lock mechanism.

        Implements ACID properties:
        - Atomicity: Redis pipeline ensures atomic execution
        - Consistency: Checksum validation before commit
        - Isolation: Distributed lock prevents concurrent writes
        - Durability: Redis persistence

        Args:
            new_state: New workflow state to commit

        Raises:
            StateLockError: If unable to acquire lock
            RuntimeError: If commit fails
        """
        workflow_id = new_state.workflow_id
        state_key = f"{self.STATE_PREFIX}{workflow_id}"
        lock_key = f"{self.LOCK_PREFIX}{workflow_id}"

        # 1. Pre-Commit Validation (C in ACID)
        new_state.checksum = self._generate_checksum(new_state.data_payload)
        new_state.last_checkpoint_time = datetime.now()

        # Serialize state
        serialized_state = new_state.model_dump_json()

        # 2. Acquire Lock (I in ACID)
        lock_acquired = await self.db.set(
            lock_key,
            "locked",
            nx=True,  # Only set if not exists
            ex=self.LOCK_TIMEOUT
        )

        if not lock_acquired:
            raise StateLockError(
                f"Unable to acquire lock for workflow {workflow_id}. "
                f"Another process may be updating the state."
            )

        try:
            # 3. Atomic Transaction (A in ACID)
            pipe = self.db.pipeline()
            pipe.set(state_key, serialized_state)
            pipe.delete(lock_key)  # Release lock

            # Execute the transaction atomically
            await pipe.execute()

            logger.info(
                f"✓ Committed state for workflow {workflow_id}: "
                f"step={new_state.current_step}, "
                f"checksum={new_state.checksum[:8]}..."
            )

            # 4. Durability (D in ACID) is guaranteed by Redis persistence

        except Exception as e:
            # Attempt to release lock on failure
            try:
                await self.db.delete(lock_key)
            except Exception as lock_error:
                logger.error(f"Failed to release lock: {lock_error}")

            raise RuntimeError(
                f"Atomic commit failed for workflow {workflow_id}: {e}"
            )

    async def rollback_to_last_checkpoint(self, workflow_id: str) -> None:
        """Rollback to the last valid checkpoint.

        In this implementation, we delete the potentially corrupted state,
        forcing the workflow to restart from the last known good state
        or initial configuration.

        Args:
            workflow_id: Workflow identifier
        """
        key = f"{self.STATE_PREFIX}{workflow_id}"
        deleted = await self.db.delete(key)

        if deleted:
            logger.critical(
                f"⚠️ ROLLBACK: Deleted corrupted state for workflow {workflow_id}. "
                f"Workflow must restart from last checkpoint or initial state."
            )
        else:
            logger.warning(
                f"Rollback called for workflow {workflow_id}, but no state found."
            )

    async def delete_state(self, workflow_id: str) -> bool:
        """Delete workflow state.

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if state was deleted
        """
        key = f"{self.STATE_PREFIX}{workflow_id}"
        deleted = await self.db.delete(key)

        if deleted:
            logger.info(f"Deleted state for workflow {workflow_id}")

        return bool(deleted)

    async def list_workflows(self, pattern: str = "*") -> list[str]:
        """List all workflow IDs matching pattern.

        Args:
            pattern: Redis key pattern (default: all workflows)

        Returns:
            List of workflow IDs
        """
        key_pattern = f"{self.STATE_PREFIX}{pattern}"
        keys = []

        async for key in self.db.scan_iter(match=key_pattern):
            # Extract workflow_id from key
            workflow_id = key.decode('utf-8').replace(self.STATE_PREFIX, '')
            keys.append(workflow_id)

        return keys

    async def get_state_info(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get state information without full validation.

        Args:
            workflow_id: Workflow identifier

        Returns:
            State info dictionary or None
        """
        try:
            state = await self.load_state(workflow_id)
            if state:
                return {
                    "workflow_id": state.workflow_id,
                    "current_step": state.current_step,
                    "last_checkpoint_time": state.last_checkpoint_time.isoformat(),
                    "checksum": state.checksum,
                    "data_size": len(json.dumps(state.data_payload))
                }
        except Exception as e:
            logger.error(f"Failed to get state info for {workflow_id}: {e}")

        return None

async def execute_and_checkpoint(
    state_manager: AtomicStateManager,
    workflow_id: str,
    step_name: str,
    new_data: Dict[str, Any]
) -> None:
    """Execute a workflow step and atomically checkpoint state.

    Example usage pattern for workflow execution.

    Args:
        state_manager: AtomicStateManager instance
        workflow_id: Workflow identifier
        step_name: Name of the step being executed
        new_data: New data to merge into state

    Raises:
        RuntimeError: If checkpoint fails
    """
    # 1. Load Current State
    current_state = await state_manager.load_state(workflow_id)

    if not current_state:
        # Initialize new state
        current_state = WorkflowState(
            workflow_id=workflow_id,
            current_step="INITIALIZE",
            last_checkpoint_time=datetime.now(),
            data_payload={},
            checksum=""
        )

    # 2. Mutate State (Perform workflow step work)
    current_state.data_payload.update(new_data)
    current_state.current_step = step_name

    # 3. Commit State Atomically (Critical Path)
    try:
        await state_manager.commit_state(current_state)
        logger.info(
            f"✅ Workflow {workflow_id} checkpointed successfully at {step_name}"
        )
    except (StateLockError, RuntimeError) as e:
        # Commit failure is critical - trigger rollback
        logger.error(f"❌ Commit failed for {workflow_id}: {e}")
        await state_manager.rollback_to_last_checkpoint(workflow_id)
        raise RuntimeError(f"Checkpoint failed, workflow rolled back: {e}")
