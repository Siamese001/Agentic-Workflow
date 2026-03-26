# API Documentation: vllm_invariant_contract_types

**Target Audience**: developers, api_users

# vllm_invariant_contract_types API Documentation

**File**: `vllm_invariant_contract_types.py`
**Classes**: 3
**Functions**: 3

## Classes

- **InvariantId** (inherits from str, Enum)
- **InvariantSeverity** (inherits from str, Enum)
- **InvariantViolation**

## Functions

- **canonical_json** -> str
- **violation_hash** -> str
- **as_dict** -> dict[str, Any]


## Class: InvariantId

**Description**: Stable invariant identifiers for runtime enforcement.

**Inherits from**: str, Enum



## Class: InvariantSeverity

**Description**: Severity levels for invariant violations.

**Inherits from**: str, Enum



## Class: InvariantViolation

**Description**: Immutable invariant violation artifact with deterministic serialization.

    All fields are deterministic (no timestamps, no nondeterministic runtime state).
    Context dict is canonicalized with sorted keys for stable hashing.
    

### Methods

#### canonical_json
**Parameters**: self
**Returns**: str
**Description**: Returns canonical JSON representation with sorted keys.

#### violation_hash
**Parameters**: self
**Returns**: str
**Description**: Returns SHA256 hash of canonical JSON representation.

#### as_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Returns dict representation with stable key ordering.



## Function: canonical_json

**Parameters**: self
**Returns**: str
**Description**: Returns canonical JSON representation with sorted keys.



## Function: violation_hash

**Parameters**: self
**Returns**: str
**Description**: Returns SHA256 hash of canonical JSON representation.



## Function: as_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Returns dict representation with stable key ordering.



## Usage Examples

### Class Usage

```python
# Using InvariantId
invariantid = InvariantId()
```

```python
# Using InvariantSeverity
invariantseverity = InvariantSeverity()
```

```python
# Using InvariantViolation
invariantviolation = InvariantViolation()
invariantviolation.canonical_json()
invariantviolation.violation_hash()
```

### Function Usage

```python
# Using canonical_json
result = canonical_json()
```

```python
# Using violation_hash
result = violation_hash()
```

```python
# Using as_dict
result = as_dict()
```



---
**Generated**: 2026-03-26T09:39:04.032075
**Type**: api_reference
**Quality**: comprehensive
