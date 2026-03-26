# API Documentation: artifact_validators_types

**Target Audience**: developers, api_users

# artifact_validators_types API Documentation

**File**: `artifact_validators_types.py`
**Classes**: 0
**Functions**: 16


## Functions

- **_to_raw_dict** -> dict[str, Any]
- **_require_str** -> None
- **_require_int** -> None
- **_require_sequence_of_str** -> None
- **_coerce_enum_to_str** -> None
- **_coerce_tuple_to_list** -> None
- **validate_result_artifact** -> dict[str, Any]
- **to_result_artifact_dict** -> dict[str, Any]
- **validate_healing_plan** -> dict[str, Any]
- **to_healing_plan_dict** -> dict[str, Any]
- **validate_incident_artifact** -> dict[str, Any]
- **to_incident_artifact_dict** -> dict[str, Any]
- **validate_stale_write_incident** -> dict[str, Any]
- **to_stale_write_incident_dict** -> dict[str, Any]
- **make_result_artifact_from_dataclass** -> dict[str, Any]
- **make_healing_plan_from_dataclass** -> dict[str, Any]


## Function: _to_raw_dict

**Parameters**: obj
**Returns**: dict[str, Any]
**Description**: Convert dataclass or dict-like to plain dict without mutating input.



## Function: _require_str

**Parameters**: d, key, artifact_name
**Returns**: None
**Description**: Require a non-empty string field.



## Function: _require_int

**Parameters**: d, key, artifact_name
**Returns**: None
**Description**: Require an integer field, optionally with minimum.



## Function: _require_sequence_of_str

**Parameters**: d, key, artifact_name
**Returns**: None
**Description**: Require a sequence of strings field.



## Function: _coerce_enum_to_str

**Parameters**: d, key
**Returns**: None
**Description**: If a field value has a .value attribute (Enum), replace with its string value.



## Function: _coerce_tuple_to_list

**Parameters**: d, key
**Returns**: None
**Description**: Convert tuple to list for JSON-schema alignment.



## Function: validate_result_artifact

**Parameters**: obj
**Returns**: dict[str, Any]
**Description**: Validate and normalize a ResultArtifact to TypedDict shape.

    Accepts dict or frozen dataclass. Returns plain dict.
    Raises ValueError on first missing/invalid required field.
    



## Function: to_result_artifact_dict

**Parameters**: x
**Returns**: dict[str, Any]
**Description**: Bridge adapter: convert dataclass or dict to plain dict (ResultArtifact shape).



## Function: validate_healing_plan

**Parameters**: obj
**Returns**: dict[str, Any]
**Description**: Validate and normalize a HealingPlan to TypedDict shape.

    Accepts dict or frozen dataclass. Returns plain dict.
    Raises ValueError on first missing/invalid required field.
    



## Function: to_healing_plan_dict

**Parameters**: x
**Returns**: dict[str, Any]
**Description**: Bridge adapter: convert dataclass or dict to plain dict (HealingPlan shape).



## Function: validate_incident_artifact

**Parameters**: obj
**Returns**: dict[str, Any]
**Description**: Validate and normalize an IncidentArtifact to TypedDict shape.



## Function: to_incident_artifact_dict

**Parameters**: x
**Returns**: dict[str, Any]
**Description**: Bridge adapter: convert dataclass or dict to plain dict (IncidentArtifact shape).



## Function: validate_stale_write_incident

**Parameters**: obj
**Returns**: dict[str, Any]
**Description**: Validate and normalize a StaleWriteIncident to TypedDict shape.



## Function: to_stale_write_incident_dict

**Parameters**: x
**Returns**: dict[str, Any]
**Description**: Bridge adapter: convert dataclass or dict to plain dict (StaleWriteIncident shape).



## Function: make_result_artifact_from_dataclass

**Parameters**: dc
**Returns**: dict[str, Any]
**Description**: Factory: validate a ResultArtifact dataclass and return TD-shaped dict.



## Function: make_healing_plan_from_dataclass

**Parameters**: dc
**Returns**: dict[str, Any]
**Description**: Factory: validate a HealingPlan dataclass and return TD-shaped dict.



## Usage Examples

### Function Usage

```python
# Using _to_raw_dict
result = _to_raw_dict(obj)
```

```python
# Using _require_str
result = _require_str(d, key)
```

```python
# Using _require_int
result = _require_int(d, key)
```



---
**Generated**: 2026-03-26T09:39:03.425924
**Type**: api_reference
**Quality**: comprehensive
