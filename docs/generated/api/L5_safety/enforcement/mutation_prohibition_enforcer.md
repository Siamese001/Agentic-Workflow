# API Documentation: mutation_prohibition_enforcer

**Target Audience**: developers, api_users

# mutation_prohibition_enforcer API Documentation

**File**: `mutation_prohibition_enforcer.py`
**Classes**: 0
**Functions**: 11


## Functions

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

### Function Usage

```python
# Using _is_override_active
result = _is_override_active()
```

```python
# Using assert_no_persistent_write
result = assert_no_persistent_write(layer, op)
```

```python
# Using safe_write_text
result = safe_write_text(filepath, content)
```



---
**Generated**: 2026-03-26T09:39:04.883374
**Type**: api_reference
**Quality**: comprehensive
