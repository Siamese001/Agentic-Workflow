# API Documentation: negative_control_harness

**Target Audience**: developers, api_users

# negative_control_harness API Documentation

**File**: `negative_control_harness.py`
**Classes**: 0
**Functions**: 6


## Functions

- **is_tamper_active** -> bool
- **get_config_surface** -> dict[str, Any]
- **hash_config_surface** -> str
- **assert_digest_differs** -> None
- **assert_digest_stable** -> None
- **_canonical_json_bytes** -> bytes


## Function: is_tamper_active

**Returns**: bool
**Description**: Return True iff W_HARDEN_NEGCTRL_TAMPER == '1' in the environment.



## Function: get_config_surface

**Returns**: dict[str, Any]
**Description**: Return the embedding/meta-learning config surface.

    If W_HARDEN_NEGCTRL_TAMPER=1 the surface is modified with known-bad
    values so the resulting digest differs from the clean run.
    



## Function: hash_config_surface

**Parameters**: surface
**Returns**: str
**Description**: Return SHA-256 hex of the canonical config surface dict.



## Function: assert_digest_differs

**Parameters**: clean_digest, tampered_digest
**Returns**: None
**Description**: Assert that *clean_digest* != *tampered_digest*.

    Raises:
        AssertionError: if the two digests are identical (tamper not detected).
    



## Function: assert_digest_stable

**Parameters**: digest1, digest2
**Returns**: None
**Description**: Assert that *digest1* == *digest2* (two independent clean runs).

    Raises:
        AssertionError: if the two digests differ (non-determinism detected).
    



## Function: _canonical_json_bytes

**Parameters**: data
**Returns**: bytes


## Usage Examples

### Function Usage

```python
# Using is_tamper_active
result = is_tamper_active()
```

```python
# Using get_config_surface
result = get_config_surface()
```

```python
# Using hash_config_surface
result = hash_config_surface(surface)
```



---
**Generated**: 2026-03-26T09:39:03.671507
**Type**: api_reference
**Quality**: comprehensive
