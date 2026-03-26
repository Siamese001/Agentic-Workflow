# API Documentation: ml_pattern_record_types

**Target Audience**: developers, api_users

# ml_pattern_record_types API Documentation

**File**: `ml_pattern_record_types.py`
**Classes**: 2
**Functions**: 8

## Classes

- **PatternCompatibilityError** (inherits from Exception)
- **MLPatternRecord**

## Functions

- **_sha256** -> str
- **enforce_pattern_compatibility** -> None
- **__init__** -> None
- **__post_init__** -> None
- **canonical_bytes** -> bytes
- **compute_domain_hash** -> str
- **compute_record_hash** -> str
- **build** -> MLPatternRecord


## Class: PatternCompatibilityError

**Description**: 
    Raised when a retrieved pattern is incompatible with the active config.

    Violation codes:
        DOMAIN_HASH_MISMATCH   — pattern domain does not match query domain
        POLICY_HASH_MISMATCH   — pattern policy_hash != active PolicyConfig hash
        MODEL_HASH_MISMATCH    — pattern model_hash != active ModelConfig hash
    

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, violation_code, message
**Returns**: None



## Class: MLPatternRecord

**Description**: 
    Versioned healing pattern record stored in L4.

    Required fields:
        schema_version  — int, incremented on breaking schema changes
        domain_id       — str, e.g. "agentic_core", "apps_lic", "apps_rg"
        domain_hash     — sha256 of domain_id (deterministic domain binding)
        policy_hash     — sha256 of active PolicyConfig.canonical_bytes()
        model_hash      — sha256 of active ModelConfig.canonical_bytes()
        pattern_id      — str, unique identifier for this pattern
        payload         — dict, the actual healing strategy/pattern data
        record_hash     — sha256 of canonical_bytes() excluding record_hash
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### canonical_bytes
**Parameters**: self
**Returns**: bytes
**Description**: Deterministic serialization excluding record_hash.

#### compute_domain_hash
**Parameters**: domain_id
**Returns**: str

#### compute_record_hash
**Parameters**: schema_version, domain_id, domain_hash, policy_hash, model_hash, pattern_id, payload
**Returns**: str

#### build
**Parameters**: cls, domain_id, policy_hash, model_hash, pattern_id, payload, schema_version
**Returns**: MLPatternRecord
**Description**: Factory: compute domain_hash and record_hash automatically.



## Function: _sha256

**Parameters**: data
**Returns**: str


## Function: enforce_pattern_compatibility

**Parameters**: record, query_domain_id, active_policy_hash, active_model_hash
**Returns**: None
**Description**: 
    Enforce domain isolation + policy/model hash compatibility.

    Raises PatternCompatibilityError deterministically on any mismatch.
    No silent fallback.
    



## Function: __init__

**Parameters**: self, violation_code, message
**Returns**: None


## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: canonical_bytes

**Parameters**: self
**Returns**: bytes
**Description**: Deterministic serialization excluding record_hash.



## Function: compute_domain_hash

**Parameters**: domain_id
**Returns**: str


## Function: compute_record_hash

**Parameters**: schema_version, domain_id, domain_hash, policy_hash, model_hash, pattern_id, payload
**Returns**: str


## Function: build

**Parameters**: cls, domain_id, policy_hash, model_hash, pattern_id, payload, schema_version
**Returns**: MLPatternRecord
**Description**: Factory: compute domain_hash and record_hash automatically.



## Usage Examples

### Class Usage

```python
# Using PatternCompatibilityError
patterncompatibilityerror = PatternCompatibilityError()
```

```python
# Using MLPatternRecord
mlpatternrecord = MLPatternRecord()
mlpatternrecord.canonical_bytes()
mlpatternrecord.compute_domain_hash()
```

### Function Usage

```python
# Using _sha256
result = _sha256(data)
```

```python
# Using enforce_pattern_compatibility
result = enforce_pattern_compatibility(record, query_domain_id)
```

```python
# Using __init__
result = __init__(violation_code, message)
```



---
**Generated**: 2026-03-26T09:39:03.991144
**Type**: api_reference
**Quality**: comprehensive
