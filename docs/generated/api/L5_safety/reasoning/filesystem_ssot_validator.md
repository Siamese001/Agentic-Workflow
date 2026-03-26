# API Documentation: filesystem_ssot_validator

**Target Audience**: developers, api_users

# filesystem_ssot_validator API Documentation

**File**: `filesystem_ssot_validator.py`
**Classes**: 1
**Functions**: 4

## Classes

- **FilesystemSSOTValidatorAgent**

## Functions

- **__init__** -> None
- **scan** -> dict[str, Any]
- **to_check_dict** -> dict[str, Any]
- **run** -> dict[str, Any]


## Class: FilesystemSSOTValidatorAgent

**Description**: L5 Certify-only validator for filesystem SSOT drift.

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### scan
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Delegate to FilesystemSSOTReconcilerAgent.detect_root_drift(). Read-only.

#### to_check_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.

#### run
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: scan

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Delegate to FilesystemSSOTReconcilerAgent.detect_root_drift(). Read-only.



## Function: to_check_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.



## Function: run

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Usage Examples

### Class Usage

```python
# Using FilesystemSSOTValidatorAgent
filesystemssotvalidatoragent = FilesystemSSOTValidatorAgent()
filesystemssotvalidatoragent.scan()
filesystemssotvalidatoragent.to_check_dict()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using scan
result = scan()
```

```python
# Using to_check_dict
result = to_check_dict()
```



---
**Generated**: 2026-03-26T09:39:05.211485
**Type**: api_reference
**Quality**: comprehensive
