# API Documentation: root_hygiene_validator

**Target Audience**: developers, api_users

# root_hygiene_validator API Documentation

**File**: `root_hygiene_validator.py`
**Classes**: 1
**Functions**: 2

## Classes

- **RootHygieneValidatorAgent**

## Functions

- **__init__** -> None
- **scan_root_violations** -> dict[str, Any]


## Class: RootHygieneValidatorAgent

**Description**: L5 Certify-only validator for root directory hygiene violations.

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### scan_root_violations
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Delegate to RootHygieneAgent.scan_root_violations (read-only).



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: scan_root_violations

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Delegate to RootHygieneAgent.scan_root_violations (read-only).



## Usage Examples

### Class Usage

```python
# Using RootHygieneValidatorAgent
roothygienevalidatoragent = RootHygieneValidatorAgent()
roothygienevalidatoragent.scan_root_violations()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using scan_root_violations
result = scan_root_violations()
```



---
**Generated**: 2026-03-26T09:39:05.380735
**Type**: api_reference
**Quality**: comprehensive
