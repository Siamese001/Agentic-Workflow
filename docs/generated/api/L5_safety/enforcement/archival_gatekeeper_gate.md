# API Documentation: archival_gatekeeper_gate

**Target Audience**: developers, api_users

# archival_gatekeeper_gate API Documentation

**File**: `archival_gatekeeper_gate.py`
**Classes**: 3
**Functions**: 19

## Classes

- **ArchivalOperation** (inherits from Enum)
- **ArchivalResult**
- **ArchivalGatekeeper**

## Functions

- **to_dict** -> dict[str, Any]
- **__init__**
- **get_instance** -> ArchivalGatekeeper
- **reset_instance** -> None
- **_get_archive_path** -> Path
- **_log_operation** -> None
- **_validate_path** -> str | None
- **_is_batch_mode** -> bool
- **_request_approval** -> bool
- **set_l4_ledger_hook** -> None
- **_notify_l4_ledger** -> None
- **set_input_function** -> None
- **set_require_approval** -> None
- **safe_move** -> ArchivalResult
- **safe_archive** -> ArchivalResult
- **safe_delete** -> ArchivalResult
- **get_audit_log** -> list[dict[str, Any]]
- **get_operation_count** -> int
- **restore_from_archive** -> ArchivalResult


## Class: ArchivalOperation

**Description**: Types of archival operations.

**Inherits from**: Enum



## Class: ArchivalResult

**Description**: Result of an archival operation.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for logging/serialization.



## Class: ArchivalGatekeeper

**Description**: 
    Singleton service for all destructive file operations.

    This gatekeeper ensures:
    - All file moves/deletes/archives go through a single point
    - Every operation is logged with full audit trail
    - 'Delete' operations are soft deletes (move to archive)
    - Hard deletes are banned to prevent data loss

    Thread-safe singleton implementation.
    

### Methods

#### __init__
**Parameters**: self, project_root
**Description**: 
        Initialize the gatekeeper.

        NOTE: Use get_instance() instead of direct instantiation.

        Args:
            project_root: Root directory of the project
        

#### get_instance
**Parameters**: cls, project_root
**Returns**: ArchivalGatekeeper
**Description**: 
        Get the singleton instance of ArchivalGatekeeper.

        Args:
            project_root: Root directory (required on first call)

        Returns:
            The singleton ArchivalGatekeeper instance

        Raises:
            ValueError: If project_root not provided on first call
        

#### reset_instance
**Parameters**: cls
**Returns**: None
**Description**: Reset the singleton instance (primarily for testing).

#### _get_archive_path
**Parameters**: self, source_path
**Returns**: Path
**Description**: 
        Generate archive path for a file.

        Structure: .archive/{YYYY-MM-DD}/{original_relative_path}

        Args:
            source_path: Original file path

        Returns:
            Path in archive directory
        

#### _log_operation
**Parameters**: self, result
**Returns**: None
**Description**: 
        Log operation to audit log (JSONL format).

        Thread-safe: Uses _log_lock to prevent log corruption from concurrent writes.

        Args:
            result: The operation result to log
        

#### _validate_path
**Parameters**: self, path, operation, allow_archive
**Returns**: str | None
**Description**: 
        Validate a path before operation.

        Args:
            path: Path to validate
            operation: Name of operation for error message
            allow_archive: If True, allow operations on archive directory (for restore)

        Returns:
            Error message if invalid, None if valid
        

#### _is_batch_mode
**Parameters**: self
**Returns**: bool
**Description**: 
        Check if batch mode is enabled via environment variable.

        [PHASE 33j] Checks both ARCHIVE_BATCH_ACCEPT and SOVEREIGN_AUTO_APPROVE.
        When either is set to "1", all operations are auto-approved without prompts.

        Returns:
            True if batch mode is enabled
        

#### _request_approval
**Parameters**: self, result
**Returns**: bool
**Description**: 
        Request user approval for a destructive operation.

        Displays operation details and waits for (y/n) input.
        Auto-approves if ARCHIVE_BATCH_ACCEPT=1 is set.

        Args:
            result: The pending operation result (pre-populated with details)

        Returns:
            True if approved, False if denied
        

#### set_l4_ledger_hook
**Parameters**: self, hook
**Returns**: None
**Description**: 
        Register a callback for L4 Ledger integration.

        The hook will be called after each operation with the full result,
        allowing the L4 Ledger to capture before/after state.

        Args:
            hook: Callable that receives ArchivalResult
        

#### _notify_l4_ledger
**Parameters**: self, result
**Returns**: None
**Description**: 
        Notify L4 Ledger of an operation (if hook is registered).

        This captures the "before" and "after" state as mandated by
        the Rationalization Report.

        Args:
            result: The completed operation result
        

#### set_input_function
**Parameters**: self, func
**Returns**: None
**Description**: 
        Set a custom input function (for testing).

        Args:
            func: Function that takes a prompt string and returns user input
        

#### set_require_approval
**Parameters**: self, require
**Returns**: None
**Description**: 
        Enable or disable approval requirement.

        Args:
            require: If True, require user approval for operations
        

#### safe_move
**Parameters**: self, source, destination, requester_agent, reason, create_parents, overwrite
**Returns**: ArchivalResult
**Description**: 
        Safely move a file or directory.

        Args:
            source: Source path
            destination: Destination path
            requester_agent: Name of the agent requesting the operation
            reason: Reason for the move
            create_parents: Create parent directories if needed
            overwrite: If False (default), fail if destination exists. Prevents silent overwrites.

        Returns:
            ArchivalResult with operation details
        

#### safe_archive
**Parameters**: self, source, requester_agent, reason
**Returns**: ArchivalResult
**Description**: 
        Safely archive a file or directory.

        Moves the file to: .archive/{YYYY-MM-DD}/{original_relative_path}

        Args:
            source: Source path to archive
            requester_agent: Name of the agent requesting the operation
            reason: Reason for archiving

        Returns:
            ArchivalResult with operation details
        

#### safe_delete
**Parameters**: self, source, requester_agent, reason
**Returns**: ArchivalResult
**Description**: 
        Safely 'delete' a file or directory.

        NOTE: This is a SOFT DELETE - the file is moved to archive, not permanently deleted.
        Hard deletes are banned to prevent data loss.

        Args:
            source: Source path to delete
            requester_agent: Name of the agent requesting the operation
            reason: Reason for deletion

        Returns:
            ArchivalResult with operation details
        

#### get_audit_log
**Parameters**: self, limit
**Returns**: list[dict[str, Any]]
**Description**: 
        Get recent entries from the audit log.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries (most recent first)
        

#### get_operation_count
**Parameters**: self
**Returns**: int
**Description**: Get total number of operations performed.

#### restore_from_archive
**Parameters**: self, archived_path, requester_agent, reason
**Returns**: ArchivalResult
**Description**: 
        Restore a file from the archive to its original location.

        Args:
            archived_path: Path to the archived file
            requester_agent: Name of the agent requesting the restore
            reason: Reason for restoration

        Returns:
            ArchivalResult with operation details
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for logging/serialization.



## Function: __init__

**Parameters**: self, project_root
**Description**: 
        Initialize the gatekeeper.

        NOTE: Use get_instance() instead of direct instantiation.

        Args:
            project_root: Root directory of the project
        



## Function: get_instance

**Parameters**: cls, project_root
**Returns**: ArchivalGatekeeper
**Description**: 
        Get the singleton instance of ArchivalGatekeeper.

        Args:
            project_root: Root directory (required on first call)

        Returns:
            The singleton ArchivalGatekeeper instance

        Raises:
            ValueError: If project_root not provided on first call
        



## Function: reset_instance

**Parameters**: cls
**Returns**: None
**Description**: Reset the singleton instance (primarily for testing).



## Function: _get_archive_path

**Parameters**: self, source_path
**Returns**: Path
**Description**: 
        Generate archive path for a file.

        Structure: .archive/{YYYY-MM-DD}/{original_relative_path}

        Args:
            source_path: Original file path

        Returns:
            Path in archive directory
        



## Function: _log_operation

**Parameters**: self, result
**Returns**: None
**Description**: 
        Log operation to audit log (JSONL format).

        Thread-safe: Uses _log_lock to prevent log corruption from concurrent writes.

        Args:
            result: The operation result to log
        



## Function: _validate_path

**Parameters**: self, path, operation, allow_archive
**Returns**: str | None
**Description**: 
        Validate a path before operation.

        Args:
            path: Path to validate
            operation: Name of operation for error message
            allow_archive: If True, allow operations on archive directory (for restore)

        Returns:
            Error message if invalid, None if valid
        



## Function: _is_batch_mode

**Parameters**: self
**Returns**: bool
**Description**: 
        Check if batch mode is enabled via environment variable.

        [PHASE 33j] Checks both ARCHIVE_BATCH_ACCEPT and SOVEREIGN_AUTO_APPROVE.
        When either is set to "1", all operations are auto-approved without prompts.

        Returns:
            True if batch mode is enabled
        



## Function: _request_approval

**Parameters**: self, result
**Returns**: bool
**Description**: 
        Request user approval for a destructive operation.

        Displays operation details and waits for (y/n) input.
        Auto-approves if ARCHIVE_BATCH_ACCEPT=1 is set.

        Args:
            result: The pending operation result (pre-populated with details)

        Returns:
            True if approved, False if denied
        



## Function: set_l4_ledger_hook

**Parameters**: self, hook
**Returns**: None
**Description**: 
        Register a callback for L4 Ledger integration.

        The hook will be called after each operation with the full result,
        allowing the L4 Ledger to capture before/after state.

        Args:
            hook: Callable that receives ArchivalResult
        



## Function: _notify_l4_ledger

**Parameters**: self, result
**Returns**: None
**Description**: 
        Notify L4 Ledger of an operation (if hook is registered).

        This captures the "before" and "after" state as mandated by
        the Rationalization Report.

        Args:
            result: The completed operation result
        



## Function: set_input_function

**Parameters**: self, func
**Returns**: None
**Description**: 
        Set a custom input function (for testing).

        Args:
            func: Function that takes a prompt string and returns user input
        



## Function: set_require_approval

**Parameters**: self, require
**Returns**: None
**Description**: 
        Enable or disable approval requirement.

        Args:
            require: If True, require user approval for operations
        



## Function: safe_move

**Parameters**: self, source, destination, requester_agent, reason, create_parents, overwrite
**Returns**: ArchivalResult
**Description**: 
        Safely move a file or directory.

        Args:
            source: Source path
            destination: Destination path
            requester_agent: Name of the agent requesting the operation
            reason: Reason for the move
            create_parents: Create parent directories if needed
            overwrite: If False (default), fail if destination exists. Prevents silent overwrites.

        Returns:
            ArchivalResult with operation details
        



## Function: safe_archive

**Parameters**: self, source, requester_agent, reason
**Returns**: ArchivalResult
**Description**: 
        Safely archive a file or directory.

        Moves the file to: .archive/{YYYY-MM-DD}/{original_relative_path}

        Args:
            source: Source path to archive
            requester_agent: Name of the agent requesting the operation
            reason: Reason for archiving

        Returns:
            ArchivalResult with operation details
        



## Function: safe_delete

**Parameters**: self, source, requester_agent, reason
**Returns**: ArchivalResult
**Description**: 
        Safely 'delete' a file or directory.

        NOTE: This is a SOFT DELETE - the file is moved to archive, not permanently deleted.
        Hard deletes are banned to prevent data loss.

        Args:
            source: Source path to delete
            requester_agent: Name of the agent requesting the operation
            reason: Reason for deletion

        Returns:
            ArchivalResult with operation details
        



## Function: get_audit_log

**Parameters**: self, limit
**Returns**: list[dict[str, Any]]
**Description**: 
        Get recent entries from the audit log.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries (most recent first)
        



## Function: get_operation_count

**Parameters**: self
**Returns**: int
**Description**: Get total number of operations performed.



## Function: restore_from_archive

**Parameters**: self, archived_path, requester_agent, reason
**Returns**: ArchivalResult
**Description**: 
        Restore a file from the archive to its original location.

        Args:
            archived_path: Path to the archived file
            requester_agent: Name of the agent requesting the restore
            reason: Reason for restoration

        Returns:
            ArchivalResult with operation details
        



## Usage Examples

### Class Usage

```python
# Using ArchivalOperation
archivaloperation = ArchivalOperation()
```

```python
# Using ArchivalResult
archivalresult = ArchivalResult()
archivalresult.to_dict()
```

```python
# Using ArchivalGatekeeper
archivalgatekeeper = ArchivalGatekeeper()
archivalgatekeeper.get_instance()
archivalgatekeeper.reset_instance()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using get_instance
result = get_instance(cls, project_root)
```



---
**Generated**: 2026-03-26T09:39:04.773389
**Type**: api_reference
**Quality**: comprehensive
