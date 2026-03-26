# API Documentation: blast_radius_controls_types

**Target Audience**: developers, api_users

# blast_radius_controls_types API Documentation

**File**: `blast_radius_controls_types.py`
**Classes**: 2
**Functions**: 6

## Classes

- **BlastRadiusExceeded** (inherits from RuntimeError)
- **BlastRadiusControls**

## Functions

- **__post_init__** -> None
- **check_state_diff** -> None
- **check_file_write** -> None
- **check_compute** -> None
- **check_parallel_branches** -> None
- **check_tool_call_rate** -> None


## Class: BlastRadiusExceeded

**Description**: Raised when an execution trace exceeds a blast-radius limit.

**Inherits from**: RuntimeError



## Class: BlastRadiusControls

**Description**: Immutable per-trace resource caps.

    Fields
    ------
    max_state_diff_bytes : int
        Maximum size (bytes) of the state diff produced by a single execution.
    max_file_write_bytes : int
        Maximum total bytes written to the filesystem per trace.
    max_compute_ms : int
        Maximum cumulative wall-clock milliseconds per trace.
    max_parallel_branches : int
        Maximum number of simultaneous sub-branches per trace.
    max_tool_calls_per_minute : int
        Rate limit: tool calls per rolling 60-second window.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### check_state_diff
**Parameters**: self, diff_bytes
**Returns**: None

#### check_file_write
**Parameters**: self, total_written_bytes
**Returns**: None

#### check_compute
**Parameters**: self, elapsed_ms
**Returns**: None

#### check_parallel_branches
**Parameters**: self, active_branches
**Returns**: None

#### check_tool_call_rate
**Parameters**: self, calls_in_window
**Returns**: None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: check_state_diff

**Parameters**: self, diff_bytes
**Returns**: None


## Function: check_file_write

**Parameters**: self, total_written_bytes
**Returns**: None


## Function: check_compute

**Parameters**: self, elapsed_ms
**Returns**: None


## Function: check_parallel_branches

**Parameters**: self, active_branches
**Returns**: None


## Function: check_tool_call_rate

**Parameters**: self, calls_in_window
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using BlastRadiusExceeded
blastradiusexceeded = BlastRadiusExceeded()
```

```python
# Using BlastRadiusControls
blastradiuscontrols = BlastRadiusControls()
blastradiuscontrols.check_state_diff()
blastradiuscontrols.check_file_write()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```

```python
# Using check_state_diff
result = check_state_diff(diff_bytes)
```

```python
# Using check_file_write
result = check_file_write(total_written_bytes)
```



---
**Generated**: 2026-03-26T09:39:03.942822
**Type**: api_reference
**Quality**: comprehensive
