# API Documentation: deterministic_replay

**Target Audience**: developers, api_users

# deterministic_replay API Documentation

**File**: `deterministic_replay.py`
**Classes**: 5
**Functions**: 8

## Classes

- **ReplayMetrics**
- **ReplayCommand**
- **ReplayResult**
- **ReplayRecord**
- **ComparisonResult**

## Functions

- **_hash_command_result** -> str
- **_filter_env_vars** -> dict[str, str]
- **_truncate_if_needed** -> tuple[str, bool]
- **run_and_record** -> ReplayRecord
- **record_to_json** -> str
- **record_from_json** -> ReplayRecord
- **_normalize_output** -> str
- **replay_and_compare** -> ComparisonResult


## Class: ReplayMetrics

**Description**: Deterministic performance metrics for replay operations.



## Class: ReplayCommand

**Description**: Immutable command definition for replay.



## Class: ReplayResult

**Description**: Immutable result of a command execution.



## Class: ReplayRecord

**Description**: Immutable record of command executions for replay.



## Class: ComparisonResult

**Description**: Result of replay comparison.



## Function: _hash_command_result

**Parameters**: command, result
**Returns**: str
**Description**: Compute SHA256 hash of command and result for integrity verification.



## Function: _filter_env_vars

**Returns**: dict[str, str]
**Description**: Filter environment variables to only allowlisted keys.



## Function: _truncate_if_needed

**Parameters**: text, max_bytes
**Returns**: tuple[str, bool]
**Description**: Truncate text if it exceeds max_bytes deterministically.

    Args:
        text: Text to potentially truncate
        max_bytes: Maximum allowed bytes

    Returns:
        Tuple of (truncated_text, was_truncated)
    



## Function: run_and_record

**Parameters**: commands
**Returns**: ReplayRecord
**Description**: Execute commands and record results deterministically.

    Args:
        commands: List of commands to execute

    Returns:
        ReplayRecord with commands, results, and per-command hashes

    Raises:
        RuntimeError: If any argv0 contains pwsh/powershell
    



## Function: record_to_json

**Parameters**: record
**Returns**: str
**Description**: Serialize ReplayRecord to deterministic JSON.

    Returns:
        JSON string with sorted keys and stable formatting
    



## Function: record_from_json

**Parameters**: json_str
**Returns**: ReplayRecord
**Description**: Deserialize JSON string to ReplayRecord.



## Function: _normalize_output

**Parameters**: output
**Returns**: str
**Description**: Normalize output by stripping timestamps and absolute paths.



## Function: replay_and_compare

**Parameters**: record
**Returns**: ComparisonResult
**Description**: Replay commands and compare with original results.

    Args:
        record: Original record to replay

    Returns:
        ComparisonResult with match status and any mismatches
    



## Usage Examples

### Class Usage

```python
# Using ReplayMetrics
replaymetrics = ReplayMetrics()
```

```python
# Using ReplayCommand
replaycommand = ReplayCommand()
```

```python
# Using ReplayResult
replayresult = ReplayResult()
```

### Function Usage

```python
# Using _hash_command_result
result = _hash_command_result(command, result)
```

```python
# Using _filter_env_vars
result = _filter_env_vars()
```

```python
# Using _truncate_if_needed
result = _truncate_if_needed(text, max_bytes)
```



---
**Generated**: 2026-03-26T09:39:04.349339
**Type**: api_reference
**Quality**: comprehensive
