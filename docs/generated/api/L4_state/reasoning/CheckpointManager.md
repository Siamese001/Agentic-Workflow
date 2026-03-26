# API Documentation: CheckpointManager

**Target Audience**: developers, api_users

# CheckpointManager API Documentation

**File**: `CheckpointManager.py`
**Classes**: 3
**Functions**: 27

## Classes

- **Checkpoint**
- **RecoveryResult**
- **CheckpointManager** (inherits from SovereignBaseAgent)

## Functions

- **_get_write_gateway**
- **timeout** -> Callable
- **get_checkpoint_manager** -> CheckpointManagerAgent
- **get_sync_checkpoint_manager** -> CheckpointManagerAgent
- **get_autonomous_checkpoint_manager** -> CheckpointManagerAgent
- **to_dict** -> dict[str, Any]
- **from_dict** -> Checkpoint
- **decorator** -> Callable
- **__post_init__** -> None
- **create_checkpoint** -> str
- **_generate_checkpoint_id** -> str
- **_save_sync** -> str
- **_mirror_checkpoint_sync** -> bool
- **verify_integrity** -> bool
- **_attempt_recovery** -> bool
- **get_checkpoint** -> Checkpoint | None
- **get_latest_checkpoint** -> Checkpoint | None
- **list_checkpoints** -> list[dict[str, Any]]
- **rollback_to_checkpoint** -> RecoveryResult
- **_load_checkpoints** -> None
- **_save_index** -> None
- **_cleanup_old_checkpoints** -> None
- **_delete_checkpoint** -> bool
- **heal** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]
- **_run_self_tests** -> dict[str, Any]
- **wrapper** -> Any


## Class: Checkpoint

**Description**: Represents a state checkpoint with metadata.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert Checkpoint to dictionary for serialization.

#### from_dict
**Parameters**: cls, data
**Returns**: Checkpoint
**Description**: Create Checkpoint from dictionary.



## Class: RecoveryResult

**Description**: Result of a recovery operation.



## Class: CheckpointManager

**Description**: 
    Unified L4 Checkpoint Guardian.

    Handles synchronous legacy checkpoints and autonomous asynchronous mirroring.
    Consolidates CheckpointManagerAgent and AutonomousCheckpointManagerAgent.

    Modes:
        - SYNC: Traditional blocking saves (Legacy support)
        - ASYNC: Non-blocking background saves
        - AUTONOMOUS: Mirroring, drift detection, and auto-recovery

    Inherits from SovereignBaseAgent which provides:
        - HealerMixin: heal_repository() for self-repair
        - MCPHardenedMixin: Hardened MCP with retry/timeout
        - RedisCacheMixin: Short-term caching
        - PineconeVectorMixin: Long-term semantic memory
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the unified checkpoint manager.

#### create_checkpoint
**Parameters**: self, state_data, label, file_hashes, metadata
**Returns**: str
**Description**: 
        Create a checkpoint (synchronous entry point for backward compatibility).

        Args:
            state_data: State snapshot to persist
            label: Label for the checkpoint
            file_hashes: Optional file hashes for integrity verification
            metadata: Optional additional metadata

        Returns:
            Checkpoint ID
        

#### _generate_checkpoint_id
**Parameters**: self, label
**Returns**: str
**Description**: Generate a unique checkpoint ID.

#### _save_sync
**Parameters**: self, checkpoint_id, state_data, file_hashes, metadata
**Returns**: str
**Description**: 
        Synchronous save logic (migrated from legacy CheckpointManagerAgent).

        Args:
            checkpoint_id: Unique checkpoint identifier
            state_data: State snapshot to persist
            file_hashes: Optional file hashes
            metadata: Optional metadata

        Returns:
            Path to saved checkpoint file
        

#### _mirror_checkpoint_sync
**Parameters**: self, primary_path
**Returns**: bool
**Description**: 
        Synchronously mirror primary checkpoint to secondary storage.

        Args:
            primary_path: Path to primary checkpoint file

        Returns:
            True if mirroring succeeded
        

#### verify_integrity
**Parameters**: self, checkpoint_id
**Returns**: bool
**Description**: 
        Verify checkpoint integrity by comparing primary and mirror hashes.

        Args:
            checkpoint_id: Checkpoint ID to verify

        Returns:
            True if checkpoint is valid
        

#### _attempt_recovery
**Parameters**: self, checkpoint_id
**Returns**: bool
**Description**: 
        Auto-recovery: Restore primary from mirror if primary is missing/corrupt.

        Args:
            checkpoint_id: Checkpoint ID to recover

        Returns:
            True if recovery succeeded
        

#### get_checkpoint
**Parameters**: self, checkpoint_id
**Returns**: Checkpoint | None
**Description**: 
        Retrieve a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID to retrieve

        Returns:
            Checkpoint object or None if not found
        

#### get_latest_checkpoint
**Parameters**: self
**Returns**: Checkpoint | None
**Description**: Get the most recent checkpoint.

#### list_checkpoints
**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: List all available checkpoints.

#### rollback_to_checkpoint
**Parameters**: self, checkpoint_id
**Returns**: RecoveryResult
**Description**: 
        Rollback state to a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to rollback to

        Returns:
            RecoveryResult with operation details
        

#### _load_checkpoints
**Parameters**: self
**Returns**: None
**Description**: Load existing checkpoints from disk.

#### _save_index
**Parameters**: self
**Returns**: None
**Description**: Save checkpoint index to disk.

#### _cleanup_old_checkpoints
**Parameters**: self
**Returns**: None
**Description**: Remove old checkpoints beyond max_checkpoints limit.

#### _delete_checkpoint
**Parameters**: self, checkpoint_id
**Returns**: bool
**Description**: Delete a checkpoint from disk and memory.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        IHealerProtocol compliance method for checkpoint violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Repository-wide checkpoint healing.

        Args:
            dry_run: If True, only report issues without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)

        Returns:
            Dictionary with healing results
        

#### _run_self_tests
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Run internal self-tests for the unified checkpoint manager.



## Function: _get_write_gateway

**Description**: Get UWG instance - L4 may only use, not import tools.



## Function: timeout

**Parameters**: seconds
**Returns**: Callable
**Description**: Timeout decorator for long-running operations.



## Function: get_checkpoint_manager

**Parameters**: mode, storage_path
**Returns**: CheckpointManagerAgent
**Description**: 
    Factory function to get CheckpointManagerAgent instance.

    Args:
        mode: Operating mode (SYNC, ASYNC, AUTONOMOUS)
        storage_path: Optional custom storage path

    Returns:
        CheckpointManagerAgent instance
    



## Function: get_sync_checkpoint_manager

**Parameters**: storage_path
**Returns**: CheckpointManagerAgent
**Description**: Get a synchronous checkpoint manager (legacy compatibility).



## Function: get_autonomous_checkpoint_manager

**Parameters**: storage_path
**Returns**: CheckpointManagerAgent
**Description**: Get an autonomous checkpoint manager with mirroring.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert Checkpoint to dictionary for serialization.



## Function: from_dict

**Parameters**: cls, data
**Returns**: Checkpoint
**Description**: Create Checkpoint from dictionary.



## Function: decorator

**Parameters**: func
**Returns**: Callable


## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the unified checkpoint manager.



## Function: create_checkpoint

**Parameters**: self, state_data, label, file_hashes, metadata
**Returns**: str
**Description**: 
        Create a checkpoint (synchronous entry point for backward compatibility).

        Args:
            state_data: State snapshot to persist
            label: Label for the checkpoint
            file_hashes: Optional file hashes for integrity verification
            metadata: Optional additional metadata

        Returns:
            Checkpoint ID
        



## Function: _generate_checkpoint_id

**Parameters**: self, label
**Returns**: str
**Description**: Generate a unique checkpoint ID.



## Function: _save_sync

**Parameters**: self, checkpoint_id, state_data, file_hashes, metadata
**Returns**: str
**Description**: 
        Synchronous save logic (migrated from legacy CheckpointManagerAgent).

        Args:
            checkpoint_id: Unique checkpoint identifier
            state_data: State snapshot to persist
            file_hashes: Optional file hashes
            metadata: Optional metadata

        Returns:
            Path to saved checkpoint file
        



## Function: _mirror_checkpoint_sync

**Parameters**: self, primary_path
**Returns**: bool
**Description**: 
        Synchronously mirror primary checkpoint to secondary storage.

        Args:
            primary_path: Path to primary checkpoint file

        Returns:
            True if mirroring succeeded
        



## Function: verify_integrity

**Parameters**: self, checkpoint_id
**Returns**: bool
**Description**: 
        Verify checkpoint integrity by comparing primary and mirror hashes.

        Args:
            checkpoint_id: Checkpoint ID to verify

        Returns:
            True if checkpoint is valid
        



## Function: _attempt_recovery

**Parameters**: self, checkpoint_id
**Returns**: bool
**Description**: 
        Auto-recovery: Restore primary from mirror if primary is missing/corrupt.

        Args:
            checkpoint_id: Checkpoint ID to recover

        Returns:
            True if recovery succeeded
        



## Function: get_checkpoint

**Parameters**: self, checkpoint_id
**Returns**: Checkpoint | None
**Description**: 
        Retrieve a checkpoint by ID.

        Args:
            checkpoint_id: Checkpoint ID to retrieve

        Returns:
            Checkpoint object or None if not found
        



## Function: get_latest_checkpoint

**Parameters**: self
**Returns**: Checkpoint | None
**Description**: Get the most recent checkpoint.



## Function: list_checkpoints

**Parameters**: self
**Returns**: list[dict[str, Any]]
**Description**: List all available checkpoints.



## Function: rollback_to_checkpoint

**Parameters**: self, checkpoint_id
**Returns**: RecoveryResult
**Description**: 
        Rollback state to a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to rollback to

        Returns:
            RecoveryResult with operation details
        



## Function: _load_checkpoints

**Parameters**: self
**Returns**: None
**Description**: Load existing checkpoints from disk.



## Function: _save_index

**Parameters**: self
**Returns**: None
**Description**: Save checkpoint index to disk.



## Function: _cleanup_old_checkpoints

**Parameters**: self
**Returns**: None
**Description**: Remove old checkpoints beyond max_checkpoints limit.



## Function: _delete_checkpoint

**Parameters**: self, checkpoint_id
**Returns**: bool
**Description**: Delete a checkpoint from disk and memory.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        IHealerProtocol compliance method for checkpoint violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Repository-wide checkpoint healing.

        Args:
            dry_run: If True, only report issues without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)

        Returns:
            Dictionary with healing results
        



## Function: _run_self_tests

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Run internal self-tests for the unified checkpoint manager.



## Function: wrapper

**Returns**: Any


## Usage Examples

### Class Usage

```python
# Using Checkpoint
checkpoint = Checkpoint()
checkpoint.to_dict()
checkpoint.from_dict()
```

```python
# Using RecoveryResult
recoveryresult = RecoveryResult()
```

```python
# Using CheckpointManager
checkpointmanager = CheckpointManager()
checkpointmanager.create_checkpoint()
checkpointmanager.verify_integrity()
```

### Function Usage

```python
# Using _get_write_gateway
result = _get_write_gateway()
```

```python
# Using timeout
result = timeout(seconds)
```

```python
# Using get_checkpoint_manager
result = get_checkpoint_manager(mode, storage_path)
```



---
**Generated**: 2026-03-26T09:39:04.616683
**Type**: api_reference
**Quality**: comprehensive
