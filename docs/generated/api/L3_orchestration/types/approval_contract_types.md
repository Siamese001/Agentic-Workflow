# API Documentation: approval_contract_types

**Target Audience**: developers, api_users

# approval_contract_types API Documentation

**File**: `approval_contract_types.py`
**Classes**: 3
**Functions**: 11

## Classes

- **ApprovalDecision** (inherits from str, Enum)
- **ApprovalRecord**
- **ApprovalBundle**

## Functions

- **check_schema_compatibility** -> list[str]
- **validate_against_json_schema** -> list[str]
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **__post_init__** -> None
- **to_dict** -> dict[str, Any]
- **to_json** -> str
- **validate** -> list[str]
- **_validate_type** -> None
- **_validate_enum** -> None
- **_validate_object** -> None


## Class: ApprovalDecision

**Description**: Decision outcome for an approval gate.

**Inherits from**: str, Enum



## Class: ApprovalRecord

**Description**: Immutable record of a single approval decision.

    Attributes:
        phase_name: Canonical phase name from PhaseSpec.
        guardian_id: Optional guardian ID (approval may be per-phase).
        check_ids: Sorted tuple of check IDs being approved (may be empty).
        decision: APPROVED or REJECTED.
        approver: Human identifier string.
        rationale: Optional free-text rationale.
        token: Opaque token ID referenced by L2.
        created_utc: ISO-8601 timestamp (required, no auto-now).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: check_ids sorted.



## Class: ApprovalBundle

**Description**: Immutable bundle of approval records for an execution plan.

    Attributes:
        records: Sorted tuple of ApprovalRecord objects (sorted by token).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: records sorted by token.

#### to_json
**Parameters**: self, indent
**Returns**: str
**Description**: Serialize to deterministic JSON string.

#### validate
**Parameters**: self
**Returns**: list[str]
**Description**: Validate against CONTRACT_JSON_SCHEMA. Returns list of errors (empty = valid).



## Function: check_schema_compatibility

**Parameters**: result_dict
**Returns**: list[str]
**Description**: Verify a serialized result dict has exactly the expected top-level keys.

    Returns list of incompatibility messages (empty = compatible).
    



## Function: validate_against_json_schema

**Parameters**: result_dict
**Returns**: list[str]
**Description**: Lightweight validation of result_dict against CONTRACT_JSON_SCHEMA.

    Validates: required fields, type constraints, enum values, additionalProperties,
    and minLength. Does NOT require jsonschema library.

    Returns list of validation errors (empty = valid).
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: check_ids sorted.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: records sorted by token.



## Function: to_json

**Parameters**: self, indent
**Returns**: str
**Description**: Serialize to deterministic JSON string.



## Function: validate

**Parameters**: self
**Returns**: list[str]
**Description**: Validate against CONTRACT_JSON_SCHEMA. Returns list of errors (empty = valid).



## Function: _validate_type

**Parameters**: value, type_spec, path
**Returns**: None


## Function: _validate_enum

**Parameters**: value, enum_values, path
**Returns**: None


## Function: _validate_object

**Parameters**: obj, obj_schema, path
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using ApprovalDecision
approvaldecision = ApprovalDecision()
```

```python
# Using ApprovalRecord
approvalrecord = ApprovalRecord()
approvalrecord.to_dict()
```

```python
# Using ApprovalBundle
approvalbundle = ApprovalBundle()
approvalbundle.to_dict()
approvalbundle.to_json()
```

### Function Usage

```python
# Using check_schema_compatibility
result = check_schema_compatibility(result_dict)
```

```python
# Using validate_against_json_schema
result = validate_against_json_schema(result_dict)
```

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:04.358532
**Type**: api_reference
**Quality**: comprehensive
