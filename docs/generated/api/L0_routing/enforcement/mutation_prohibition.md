# API Documentation: mutation_prohibition

**Target Audience**: developers, api_users

# mutation_prohibition API Documentation

**File**: `mutation_prohibition.py`
**Classes**: 3
**Functions**: 16

## Classes

- **SourceMutationBlocked** (inherits from RuntimeError)
- **ProtectedRootBlockEvent**
- **ProtectedRootPolicy**

## Functions

- **get_default_protected_root_policy** -> ProtectedRootPolicy
- **_emit_block_event** -> None
- **_get_repo_root** -> Path
- **_get_immutable_roots** -> tuple[Path, ...]
- **enforce_protected_root** -> None
- **_is_override_active** -> bool
- **assert_no_persistent_write** -> None
- **safe_write_text** -> None
- **safe_write_bytes** -> None
- **safe_json_dump** -> None
- **safe_shutil_move** -> None
- **safe_shutil_rmtree** -> None
- **safe_os_remove** -> None
- **safe_os_rename** -> None
- **safe_open_write** -> Any
- **mutation_guard** -> Generator[None, None, None]


## Class: SourceMutationBlocked

**Description**: Raised when attempting to mutate a protected root directory.

**Inherits from**: RuntimeError



## Class: ProtectedRootBlockEvent

**Description**: Event record for blocked protected-root write attempts.



## Class: ProtectedRootPolicy

**Description**: Policy contract for protected-root enforcement.

    This defines which roots are immutable and where block events are logged.
    Pure dataclass with no side effects.
    



## Function: get_default_protected_root_policy

**Returns**: ProtectedRootPolicy
**Description**: Get the default protected-root policy (pure; constant return).

    Returns:
        ProtectedRootPolicy with canonical immutable roots and log path
    



## Function: _emit_block_event

**Parameters**: target, matched_root, log_path, ts_utc_override
**Returns**: None
**Description**: Emit a deterministic JSONL event for a blocked write attempt.

    Args:
        target: Normalized path that was blocked
        matched_root: Name of the immutable root that matched
        log_path: Path to JSONL log file
        ts_utc_override: Optional fixed timestamp for deterministic replay (tests only)

    Failures are swallowed to avoid masking the block exception.
    



## Function: _get_repo_root

**Returns**: Path
**Description**: Get repository root directory.



## Function: _get_immutable_roots

**Returns**: tuple[Path, ...]
**Description**: Get immutable root paths from default policy (for backward compatibility).



## Function: enforce_protected_root

**Parameters**: target_path
**Returns**: None
**Description**: Block writes to protected root directories unless explicitly overridden.

    Args:
        target_path: Path being written to
        allow_override: If True, bypass the protection (audited CLI override)
        policy: Optional policy override (for tests only). If None, uses default policy.

    Raises:
        SourceMutationBlocked: If target_path is under a protected root and override is disabled
    



## Function: _is_override_active

**Returns**: bool
**Description**: Check if the test-only mutation override env var is set.



## Function: assert_no_persistent_write

**Parameters**: layer, op, path, trace_id
**Returns**: None
**Description**: Fail-closed guard: raises PermissionError if layer is forbidden.

    Args:
        layer: Calling layer identifier (e.g. "L0", "L4", "L6").
        op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
        path: Optional target path for the write.
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If layer is in FORBIDDEN_WRITE_LAYERS and override inactive.
    



## Function: safe_write_text

**Parameters**: filepath, content
**Returns**: None
**Description**: Guarded Path.write_text replacement.



## Function: safe_write_bytes

**Parameters**: filepath, data
**Returns**: None
**Description**: Guarded Path.write_bytes replacement.



## Function: safe_json_dump

**Parameters**: obj, filepath
**Returns**: None
**Description**: Guarded json.dump-to-file replacement.



## Function: safe_shutil_move

**Parameters**: src, dst
**Returns**: None
**Description**: Guarded shutil.move replacement.



## Function: safe_shutil_rmtree

**Parameters**: target
**Returns**: None
**Description**: Guarded shutil.rmtree replacement.



## Function: safe_os_remove

**Parameters**: filepath
**Returns**: None
**Description**: Guarded os.remove replacement.



## Function: safe_os_rename

**Parameters**: src, dst
**Returns**: None
**Description**: Guarded os.rename replacement.



## Function: safe_open_write

**Parameters**: filepath, mode
**Returns**: Any
**Description**: Guarded open(..., 'w'/'a') replacement. Returns file handle.



## Function: mutation_guard

**Parameters**: layer
**Returns**: Generator[None, None, None]
**Description**: Context manager that asserts no mutation is in progress for the layer.

    Raises PermissionError on entry if layer is forbidden.
    Useful for wrapping code blocks that should never write.
    



## Usage Examples

### Class Usage

```python
# Using SourceMutationBlocked
sourcemutationblocked = SourceMutationBlocked()
```

```python
# Using ProtectedRootBlockEvent
protectedrootblockevent = ProtectedRootBlockEvent()
```

```python
# Using ProtectedRootPolicy
protectedrootpolicy = ProtectedRootPolicy()
```

### Function Usage

```python
# Using get_default_protected_root_policy
result = get_default_protected_root_policy()
```

```python
# Using _emit_block_event
result = _emit_block_event(target, matched_root)
```

```python
# Using _get_repo_root
result = _get_repo_root()
```



---
**Generated**: 2026-03-26T09:39:02.622982
**Type**: api_reference
**Quality**: comprehensive
