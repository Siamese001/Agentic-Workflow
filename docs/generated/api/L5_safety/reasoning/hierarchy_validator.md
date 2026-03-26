# API Documentation: hierarchy_validator

**Target Audience**: developers, api_users

# hierarchy_validator API Documentation

**File**: `hierarchy_validator.py`
**Classes**: 1
**Functions**: 2

## Classes

- **HierarchyValidatorAgent**

## Functions

- **__init__** -> None
- **scan_root_violations** -> dict[str, Any]


## Class: HierarchyValidatorAgent

**Description**: L5 Certify-only validator for hierarchy/territory root violations.

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### scan_root_violations
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Delegate to HierarchyAgent.scan_root_violations (read-only).



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: scan_root_violations

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Delegate to HierarchyAgent.scan_root_violations (read-only).



## Usage Examples

### Class Usage

```python
# Using HierarchyValidatorAgent
hierarchyvalidatoragent = HierarchyValidatorAgent()
hierarchyvalidatoragent.scan_root_violations()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using scan_root_violations
result = scan_root_violations(target_territory)
```



---
**Generated**: 2026-03-26T09:39:05.270433
**Type**: api_reference
**Quality**: comprehensive
