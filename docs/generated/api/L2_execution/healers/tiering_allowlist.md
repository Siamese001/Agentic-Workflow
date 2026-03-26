# API Documentation: tiering_allowlist

**Target Audience**: developers, api_users

# tiering_allowlist API Documentation

**File**: `tiering_allowlist.py`
**Classes**: 0
**Functions**: 3


## Functions

- **_validate_allowlist_sovereignty** -> None
- **is_tiering_allowed** -> bool
- **is_tiering_allowed_by_path** -> bool


## Function: _validate_allowlist_sovereignty

**Returns**: None
**Description**: Validate allowlist invariants at module import time.



## Function: is_tiering_allowed

**Parameters**: agent_name
**Returns**: bool
**Description**: Check if agent is in compile-time frozen allowlist.

    Args:
        agent_name: Agent name to check

    Returns:
        True if agent is in TIERING_ALLOWLIST, False otherwise
    



## Function: is_tiering_allowed_by_path

**Parameters**: file_path
**Returns**: bool
**Description**: Check if a file path is in the compile-time frozen allowlist.

    Args:
        file_path: File path to check

    Returns:
        True if file path is in TIERING_ALLOWLIST, False otherwise
    



## Usage Examples

### Function Usage

```python
# Using _validate_allowlist_sovereignty
result = _validate_allowlist_sovereignty()
```

```python
# Using is_tiering_allowed
result = is_tiering_allowed(agent_name)
```

```python
# Using is_tiering_allowed_by_path
result = is_tiering_allowed_by_path(file_path)
```



---
**Generated**: 2026-03-26T09:39:03.849353
**Type**: api_reference
**Quality**: comprehensive
