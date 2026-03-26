# API Documentation: canonicalize

**Target Audience**: developers, api_users

# canonicalize API Documentation

**File**: `canonicalize.py`
**Classes**: 0
**Functions**: 1


## Functions

- **canonical_bytes** -> bytes


## Function: canonical_bytes

**Parameters**: obj
**Returns**: bytes
**Description**: Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    



## Usage Examples

### Function Usage

```python
# Using canonical_bytes
result = canonical_bytes(obj)
```



---
**Generated**: 2026-03-26T09:39:03.660068
**Type**: api_reference
**Quality**: comprehensive
