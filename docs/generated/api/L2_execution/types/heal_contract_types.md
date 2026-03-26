# API Documentation: heal_contract_types

**Target Audience**: developers, api_users

# heal_contract_types API Documentation

**File**: `heal_contract_types.py`
**Classes**: 3
**Functions**: 12

## Classes

- **HealStatus** (inherits from str, Enum)
- **HealCheckResult**
- **CombinedHealResult**

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
- **_validate_pattern** -> None
- **_validate_object** -> None


## Class: HealStatus

**Description**: Per-check heal outcome status.

**Inherits from**: str, Enum



## Class: HealCheckResult

**Description**: Immutable result of a single heal check.

    Attributes:
        check_id: Identifier of the check that was healed.
        status: Outcome of the healing attempt.
        changes_made: Sorted repo-relative paths or human-readable actions.
        rollback_info: Optional rollback instructions.
        notes: Optional free-text notes.
        needs_llm_escalation: True only when the healer explicitly determines
            LLM-tier escalation is required (e.g. complex rewrite needed).
            Must NOT be set for policy-blocked, permission, or N/A failures.
        escalation_hint: Structured hint for tier routing, e.g.
            "failure_type=code_edit_required blast_radius=0.7".
            Ignored unless needs_llm_escalation is True.
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: changes_made sorted.



## Class: CombinedHealResult

**Description**: Immutable aggregate of all heal check results for a plan execution.

    Attributes:
        tool_id: Constant identifier for the tool that produced the result.
        plan_name: Name of the execution plan used.
        results: Sorted tuple of HealCheckResult objects.
        approved_by: Sorted tuple of approval tokens/ids.
        created_utc: ISO-8601 timestamp (required, no auto-now).
    

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: results sorted by check_id, approved_by sorted.

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
    and path patterns. Does NOT require jsonschema library.

    Returns list of validation errors (empty = valid).
    



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: changes_made sorted.



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Deterministic dict: results sorted by check_id, approved_by sorted.



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


## Function: _validate_pattern

**Parameters**: value, pattern, path
**Returns**: None


## Function: _validate_object

**Parameters**: obj, obj_schema, path
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using HealStatus
healstatus = HealStatus()
```

```python
# Using HealCheckResult
healcheckresult = HealCheckResult()
healcheckresult.to_dict()
```

```python
# Using CombinedHealResult
combinedhealresult = CombinedHealResult()
combinedhealresult.to_dict()
combinedhealresult.to_json()
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
**Generated**: 2026-03-26T09:39:03.966773
**Type**: api_reference
**Quality**: comprehensive
