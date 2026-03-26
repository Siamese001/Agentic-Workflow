# API Documentation: manifest_hash_validator

**Target Audience**: developers, api_users

# manifest_hash_validator API Documentation

**File**: `manifest_hash_validator.py`
**Classes**: 1
**Functions**: 2

## Classes

- **ManifestHashError** (inherits from Exception)

## Functions

- **_get_active_configs**
- **validate_manifest_hashes** -> None


## Class: ManifestHashError

**Description**: Raised when manifest is missing or has mismatched config hashes.

**Inherits from**: Exception



## Function: _get_active_configs



## Function: validate_manifest_hashes

**Parameters**: manifest
**Returns**: None
**Description**: 
    L2.0 gate: reject manifest if any required config hash is missing
    or does not match the L4 SSOT active config.

    Args:
        manifest: Any object with hash attributes, or a dict.

    Raises:
        ManifestHashError: on missing field or hash mismatch.
    



## Usage Examples

### Class Usage

```python
# Using ManifestHashError
manifesthasherror = ManifestHashError()
```

### Function Usage

```python
# Using _get_active_configs
result = _get_active_configs()
```

```python
# Using validate_manifest_hashes
result = validate_manifest_hashes(manifest)
```



---
**Generated**: 2026-03-26T09:39:03.713944
**Type**: api_reference
**Quality**: comprehensive
