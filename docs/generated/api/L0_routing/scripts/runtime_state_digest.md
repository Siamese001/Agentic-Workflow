# API Documentation: runtime_state_digest

**Target Audience**: developers, api_users

# runtime_state_digest API Documentation

**File**: `runtime_state_digest.py`
**Classes**: 0
**Functions**: 9


## Functions

- **_get_nested** -> Any
- **_set_nested** -> None
- **_sort_key** -> tuple[str, ...]
- **runtime_state_digest_view** -> dict[str, Any]
- **compute_runtime_state_digest** -> str
- **detect_unexcluded_volatile_fields** -> list[str]
- **_is_volatile_key** -> bool
- **_is_volatile_value** -> bool
- **_walk** -> None


## Function: _get_nested

**Parameters**: obj, dot_path
**Returns**: Any
**Description**: Resolve a dot-separated path into *obj*; return None if missing.



## Function: _set_nested

**Parameters**: obj, dot_path, value
**Returns**: None
**Description**: Set a value at a dot-separated path inside *obj* (in-place).



## Function: _sort_key

**Parameters**: item, keys
**Returns**: tuple[str, ...]
**Description**: Build a stable sort key from dict *item* using *keys*.



## Function: runtime_state_digest_view

**Parameters**: state
**Returns**: dict[str, Any]
**Description**: Return a deep copy of *state* with:
    - excluded fields removed,
    - unordered scan-result lists deterministically sorted,
    - schema version injected.

    - MUST NOT mutate the input.
    - MUST NOT reorder ORDERED lists (events, completed_agents).
    



## Function: compute_runtime_state_digest

**Parameters**: state
**Returns**: str
**Description**: SHA-256 hex digest over the canonical bytes of the digest view.

    Canonicalization is delegated to
    ``agentic_core.utils.canonical_serializer_util.canonical_hash``
    (file: agentic_core/utils/canonical_serializer_util.py:66).
    



## Function: detect_unexcluded_volatile_fields

**Parameters**: state
**Returns**: list[str]
**Description**: Traverse *state* and return JSON-path strings for any field that:
    - has a key matching a VOLATILE_FIELD_PATTERNS substring, OR
    - has an ISO-datetime string value,
    AND is NOT already covered by EXCLUDE_PATHS.

    O(n) traversal. Does not mutate input.
    



## Function: _is_volatile_key

**Parameters**: key
**Returns**: bool


## Function: _is_volatile_value

**Parameters**: val
**Returns**: bool


## Function: _walk

**Parameters**: obj, path
**Returns**: None


## Usage Examples

### Function Usage

```python
# Using _get_nested
result = _get_nested(obj, dot_path)
```

```python
# Using _set_nested
result = _set_nested(obj, dot_path)
```

```python
# Using _sort_key
result = _sort_key(item, keys)
```



---
**Generated**: 2026-03-26T09:39:03.191989
**Type**: api_reference
**Quality**: comprehensive
