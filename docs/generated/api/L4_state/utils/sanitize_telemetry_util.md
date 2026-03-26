# API Documentation: sanitize_telemetry_util

**Target Audience**: developers, api_users

# sanitize_telemetry_util API Documentation

**File**: `sanitize_telemetry_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **_is_traceback** -> bool
- **_extract_traceback_tail** -> str
- **sanitize_tool_output** -> str


## Function: _is_traceback

**Parameters**: output
**Returns**: bool
**Description**: Detect if output contains a Python traceback.



## Function: _extract_traceback_tail

**Parameters**: output, max_tail
**Returns**: str
**Description**: 
    Extract the meaningful tail of a traceback.

    Python tracebacks have the actual error at the END, so we need to
    preserve more of the tail when dealing with tracebacks.
    



## Function: sanitize_tool_output

**Parameters**: output, max_chars, head_size, tail_size
**Returns**: str
**Description**: 
    Sanitize tool output to prevent token overload.

    Args:
        output: The raw tool output string.
        max_chars: Maximum allowed characters before pruning.
        head_size: Number of characters to preserve from the start (default: 25% of max_chars).
        tail_size: Number of characters to preserve from the end (default: 25% of max_chars).

    Returns:
        Sanitized output string, pruned if necessary.

    Logic:
        1. If output is shorter than max_chars, return as-is.
        2. If longer, return Head + pruning marker + Tail.
        3. If output is a Python traceback, preserve the actual error (at the end).
    



## Usage Examples

### Function Usage

```python
# Using _is_traceback
result = _is_traceback(output)
```

```python
# Using _extract_traceback_tail
result = _extract_traceback_tail(output, max_tail)
```

```python
# Using sanitize_tool_output
result = sanitize_tool_output(output, max_chars)
```



---
**Generated**: 2026-03-26T09:39:04.679062
**Type**: api_reference
**Quality**: comprehensive
