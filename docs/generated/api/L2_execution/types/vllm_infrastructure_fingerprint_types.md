# API Documentation: vllm_infrastructure_fingerprint_types

**Target Audience**: developers, api_users

# vllm_infrastructure_fingerprint_types API Documentation

**File**: `vllm_infrastructure_fingerprint_types.py`
**Classes**: 1
**Functions**: 6

## Classes

- **VLLMInfrastructureFingerprint**

## Functions

- **canonical_json** -> str
- **sha256_hex** -> str
- **as_dict** -> dict[str, str]
- **canonical_json** -> str
- **fingerprint_hash** -> str
- **deterministic_test_instance** -> VLLMInfrastructureFingerprint


## Class: VLLMInfrastructureFingerprint

**Description**: Pure-L2 infrastructure fingerprint for deterministic replay sealing.

### Methods

#### as_dict
**Parameters**: self
**Returns**: dict[str, str]
**Description**: Return fingerprint as plain dict (all strings).

#### canonical_json
**Parameters**: self
**Returns**: str
**Description**: 
        Return canonical JSON representation (stable key order, no whitespace).

        Used for deterministic hashing.
        

#### fingerprint_hash
**Parameters**: self
**Returns**: str
**Description**: 
        Compute SHA256 hash of the canonical JSON representation.

        Returns:
            64-character lowercase hex SHA256 digest.
        

#### deterministic_test_instance
**Parameters**: cls
**Returns**: VLLMInfrastructureFingerprint
**Description**: 
        Create a deterministic test instance with known values.

        Used by unit_min_deps tests to avoid runtime probing.
        



## Function: canonical_json

**Parameters**: obj
**Returns**: str
**Description**: 
    Deterministic JSON serialization with stable key order and minimal whitespace.

    Args:
        obj: JSON-serializable object.

    Returns:
        Canonical JSON string.
    



## Function: sha256_hex

**Parameters**: data
**Returns**: str
**Description**: 
    Compute SHA256 hex digest of string or bytes.

    Args:
        data: Input data.

    Returns:
        64-character lowercase hex SHA256 digest.
    



## Function: as_dict

**Parameters**: self
**Returns**: dict[str, str]
**Description**: Return fingerprint as plain dict (all strings).



## Function: canonical_json

**Parameters**: self
**Returns**: str
**Description**: 
        Return canonical JSON representation (stable key order, no whitespace).

        Used for deterministic hashing.
        



## Function: fingerprint_hash

**Parameters**: self
**Returns**: str
**Description**: 
        Compute SHA256 hash of the canonical JSON representation.

        Returns:
            64-character lowercase hex SHA256 digest.
        



## Function: deterministic_test_instance

**Parameters**: cls
**Returns**: VLLMInfrastructureFingerprint
**Description**: 
        Create a deterministic test instance with known values.

        Used by unit_min_deps tests to avoid runtime probing.
        



## Usage Examples

### Class Usage

```python
# Using VLLMInfrastructureFingerprint
vllminfrastructurefingerprint = VLLMInfrastructureFingerprint()
vllminfrastructurefingerprint.as_dict()
vllminfrastructurefingerprint.canonical_json()
```

### Function Usage

```python
# Using canonical_json
result = canonical_json(obj)
```

```python
# Using sha256_hex
result = sha256_hex(data)
```

```python
# Using as_dict
result = as_dict()
```



---
**Generated**: 2026-03-26T09:39:04.028977
**Type**: api_reference
**Quality**: comprehensive
