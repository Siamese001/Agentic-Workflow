# API Documentation: StateManagementAgent

**Target Audience**: developers, api_users

# StateManagementAgent API Documentation

**File**: `StateManagementAgent.py`
**Classes**: 3
**Functions**: 31

## Classes

- **StateEntry**
- **IntegrityReport**
- **StateManagementAgent** (inherits from WriteGovernorMixin, SovereignBaseAgent)

## Functions

- **get_state_manager** -> StateManagementAgent
- **get_manifest_manager** -> StateManagementAgent
- **get_memory_manager** -> StateManagementAgent
- **get_state_guardian** -> StateManagementAgent
- **to_dict** -> dict[str, Any]
- **from_dict** -> StateEntry
- **to_dict** -> dict[str, Any]
- **__post_init__** -> None
- **_ensure_infrastructure** -> None
- **manifest_path** -> Path
- **manifest_path** -> None
- **manifest_backup** -> Path
- **manifest_backup** -> None
- **_load_manifest** -> None
- **_save_manifest** -> None
- **_write_manifest_raw** -> None
- **_read_manifest_raw** -> dict[str, Any]
- **set_state** -> str
- **_mcp8_mirror_set** -> None
- **get_state** -> Any | None
- **delete_state** -> bool
- **list_states** -> list[str]
- **validate_and_sync** -> IntegrityReport
- **repair_integrity** -> dict[str, int]
- **perform_cleanup** -> dict[str, int]
- **register_callback** -> None
- **unregister_callback** -> None
- **_notify_registry_update** -> None
- **heal** -> dict[str, Any]
- **heal_repository** -> dict[str, Any]
- **_run_self_tests** -> dict[str, Any]


## Class: StateEntry

**Description**: Represents a single entry in the state manifest.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.

#### from_dict
**Parameters**: cls, data
**Returns**: StateEntry
**Description**: Create from dictionary.



## Class: IntegrityReport

**Description**: Report from integrity check.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]



## Class: StateManagementAgent

**Description**: 
    Unified L4 State Controller.

    Manages the manifest inventory, physical memory cleanup, and integrity guardianship.
    Consolidates ManifestManager, MemoryManager, and AutonomousStateGuardian.

    Features:
    - Atomic state transactions (manifest + physical storage)
    - Continuous integrity monitoring via heartbeat
    - Ghost/orphan detection and resolution
    - Resource synchronization with registry agents
    - Automatic cleanup with configurable retention

    Inherits from SovereignBaseAgent which provides:
        - HealerMixin: heal_repository() for self-repair
        - MCPHardenedMixin: Hardened MCP with retry/timeout
        - RedisCacheMixin: Short-term caching
        - PineconeVectorMixin: Long-term semantic memory
    

**Inherits from**: WriteGovernorMixin, SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the unified state management agent.

#### _ensure_infrastructure
**Parameters**: self
**Returns**: None
**Description**: Ensure directories exist and manifest is initialized.

#### manifest_path
**Parameters**: self
**Returns**: Path

#### manifest_path
**Parameters**: self, value
**Returns**: None

#### manifest_backup
**Parameters**: self
**Returns**: Path

#### manifest_backup
**Parameters**: self, value
**Returns**: None

#### _load_manifest
**Parameters**: self
**Returns**: None
**Description**: Load manifest from disk into memory.

#### _save_manifest
**Parameters**: self
**Returns**: None
**Description**: Save manifest to disk with backup.

#### _write_manifest_raw
**Parameters**: self, data
**Returns**: None
**Description**: Write raw manifest data to disk.

#### _read_manifest_raw
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Read raw manifest data from disk.

#### set_state
**Parameters**: self, key, data, metadata
**Returns**: str
**Description**: 
        Atomically set state data with manifest tracking.

        Args:
            key: Unique key for the state entry
            data: Data to persist (will be JSON serialized)
            metadata: Optional metadata

        Returns:
            File path where data was stored
        

#### _mcp8_mirror_set
**Parameters**: self, key, data
**Returns**: None
**Description**: Mirror state to MCP memory server (mcp8) for cross-session persistence.

        Non-blocking — failures are logged but never propagate to callers.
        L4 file-based state remains the authoritative source of truth.
        

#### get_state
**Parameters**: self, key
**Returns**: Any | None
**Description**: 
        Get state data by key.

        Args:
            key: State entry key

        Returns:
            Deserialized data or None if not found
        

#### delete_state
**Parameters**: self, key
**Returns**: bool
**Description**: 
        Atomically delete state data and manifest entry.

        Args:
            key: State entry key

        Returns:
            True if deleted, False if not found
        

#### list_states
**Parameters**: self, prefix
**Returns**: list[str]
**Description**: 
        List all state keys, optionally filtered by prefix.

        Args:
            prefix: Optional key prefix filter

        Returns:
            List of state keys
        

#### validate_and_sync
**Parameters**: self
**Returns**: IntegrityReport
**Description**: 
        Synchronize manifest with physical disk state.
        Detects ghosts (unmapped files) and orphans (missing files).

        Returns:
            IntegrityReport with findings
        

#### repair_integrity
**Parameters**: self, report
**Returns**: dict[str, int]
**Description**: 
        Repair integrity issues found in validation.

        Args:
            report: Optional pre-computed integrity report

        Returns:
            Dictionary with repair counts
        

#### perform_cleanup
**Parameters**: self, retention_days
**Returns**: dict[str, int]
**Description**: 
        Prune old state data based on retention policy.

        Args:
            retention_days: Days to retain (default: self.retention_days)

        Returns:
            Dictionary with cleanup counts
        

#### register_callback
**Parameters**: self, callback
**Returns**: None
**Description**: 
        Register a callback for state change notifications.

        Args:
            callback: Function(key, action) to call on state changes
        

#### unregister_callback
**Parameters**: self, callback
**Returns**: None
**Description**: Unregister a callback.

#### _notify_registry_update
**Parameters**: self, key, action
**Returns**: None
**Description**: Notify all registered callbacks of a state change.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        IHealerProtocol compliance method for state management violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Repository-wide state healing.

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
**Description**: Run internal self-tests for the unified state management agent.



## Function: get_state_manager

**Parameters**: memory_root
**Returns**: StateManagementAgent
**Description**: 
    Factory function to get StateManagementAgent instance.

    Args:
        memory_root: Optional memory root path

    Returns:
        StateManagementAgent instance
    



## Function: get_manifest_manager

**Parameters**: memory_root
**Returns**: StateManagementAgent
**Description**: Get state manager (legacy ManifestManager compatibility).



## Function: get_memory_manager

**Parameters**: memory_root
**Returns**: StateManagementAgent
**Description**: Get state manager (legacy MemoryManager compatibility).



## Function: get_state_guardian

**Parameters**: memory_root
**Returns**: StateManagementAgent
**Description**: Get state manager (legacy StateGuardian compatibility).



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary for serialization.



## Function: from_dict

**Parameters**: cls, data
**Returns**: StateEntry
**Description**: Create from dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]


## Function: __post_init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the unified state management agent.



## Function: _ensure_infrastructure

**Parameters**: self
**Returns**: None
**Description**: Ensure directories exist and manifest is initialized.



## Function: manifest_path

**Parameters**: self
**Returns**: Path


## Function: manifest_path

**Parameters**: self, value
**Returns**: None


## Function: manifest_backup

**Parameters**: self
**Returns**: Path


## Function: manifest_backup

**Parameters**: self, value
**Returns**: None


## Function: _load_manifest

**Parameters**: self
**Returns**: None
**Description**: Load manifest from disk into memory.



## Function: _save_manifest

**Parameters**: self
**Returns**: None
**Description**: Save manifest to disk with backup.



## Function: _write_manifest_raw

**Parameters**: self, data
**Returns**: None
**Description**: Write raw manifest data to disk.



## Function: _read_manifest_raw

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Read raw manifest data from disk.



## Function: set_state

**Parameters**: self, key, data, metadata
**Returns**: str
**Description**: 
        Atomically set state data with manifest tracking.

        Args:
            key: Unique key for the state entry
            data: Data to persist (will be JSON serialized)
            metadata: Optional metadata

        Returns:
            File path where data was stored
        



## Function: _mcp8_mirror_set

**Parameters**: self, key, data
**Returns**: None
**Description**: Mirror state to MCP memory server (mcp8) for cross-session persistence.

        Non-blocking — failures are logged but never propagate to callers.
        L4 file-based state remains the authoritative source of truth.
        



## Function: get_state

**Parameters**: self, key
**Returns**: Any | None
**Description**: 
        Get state data by key.

        Args:
            key: State entry key

        Returns:
            Deserialized data or None if not found
        



## Function: delete_state

**Parameters**: self, key
**Returns**: bool
**Description**: 
        Atomically delete state data and manifest entry.

        Args:
            key: State entry key

        Returns:
            True if deleted, False if not found
        



## Function: list_states

**Parameters**: self, prefix
**Returns**: list[str]
**Description**: 
        List all state keys, optionally filtered by prefix.

        Args:
            prefix: Optional key prefix filter

        Returns:
            List of state keys
        



## Function: validate_and_sync

**Parameters**: self
**Returns**: IntegrityReport
**Description**: 
        Synchronize manifest with physical disk state.
        Detects ghosts (unmapped files) and orphans (missing files).

        Returns:
            IntegrityReport with findings
        



## Function: repair_integrity

**Parameters**: self, report
**Returns**: dict[str, int]
**Description**: 
        Repair integrity issues found in validation.

        Args:
            report: Optional pre-computed integrity report

        Returns:
            Dictionary with repair counts
        



## Function: perform_cleanup

**Parameters**: self, retention_days
**Returns**: dict[str, int]
**Description**: 
        Prune old state data based on retention policy.

        Args:
            retention_days: Days to retain (default: self.retention_days)

        Returns:
            Dictionary with cleanup counts
        



## Function: register_callback

**Parameters**: self, callback
**Returns**: None
**Description**: 
        Register a callback for state change notifications.

        Args:
            callback: Function(key, action) to call on state changes
        



## Function: unregister_callback

**Parameters**: self, callback
**Returns**: None
**Description**: Unregister a callback.



## Function: _notify_registry_update

**Parameters**: self, key, action
**Returns**: None
**Description**: Notify all registered callbacks of a state change.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        IHealerProtocol compliance method for state management violations.

        Args:
            violation: Dictionary containing violation details

        Returns:
            Dictionary with healing result following HEAL_RESULT_SCHEMA
        



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: dict[str, Any]
**Description**: 
        Repository-wide state healing.

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
**Description**: Run internal self-tests for the unified state management agent.



## Usage Examples

### Class Usage

```python
# Using StateEntry
stateentry = StateEntry()
stateentry.to_dict()
stateentry.from_dict()
```

```python
# Using IntegrityReport
integrityreport = IntegrityReport()
integrityreport.to_dict()
```

```python
# Using StateManagementAgent
statemanagementagent = StateManagementAgent()
statemanagementagent.manifest_path()
statemanagementagent.manifest_path()
```

### Function Usage

```python
# Using get_state_manager
result = get_state_manager(memory_root)
```

```python
# Using get_manifest_manager
result = get_manifest_manager(memory_root)
```

```python
# Using get_memory_manager
result = get_memory_manager(memory_root)
```



---
**Generated**: 2026-03-26T09:39:04.312590
**Type**: api_reference
**Quality**: comprehensive
