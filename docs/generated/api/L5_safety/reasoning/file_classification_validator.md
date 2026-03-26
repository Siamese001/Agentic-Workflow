# API Documentation: file_classification_validator

**Target Audience**: developers, api_users

# file_classification_validator API Documentation

**File**: `file_classification_validator.py`
**Classes**: 1
**Functions**: 4

## Classes

- **FileClassificationValidatorAgent**

## Functions

- **__init__** -> None
- **scan** -> dict[str, Any]
- **to_check_dict** -> dict[str, Any]
- **run** -> dict[str, Any]


## Class: FileClassificationValidatorAgent

**Description**: L5 Certify-only validator for file classification compliance.

### Methods

#### __init__
**Parameters**: self, project_root
**Returns**: None

#### scan
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Run FileClassificationAgent in validate_only mode.

        Args:
            target_territory: Optional territory string to scope the scan.

        Returns:
            Dict with keys: scan_result, violations, stats, file_registry.
        

#### to_check_dict
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.

#### run
**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Function: __init__

**Parameters**: self, project_root
**Returns**: None


## Function: scan

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Run FileClassificationAgent in validate_only mode.

        Args:
            target_territory: Optional territory string to scope the scan.

        Returns:
            Dict with keys: scan_result, violations, stats, file_registry.
        



## Function: to_check_dict

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Return structured check dict for _invoke_healer dispatch.



## Function: run

**Parameters**: self, target_territory
**Returns**: dict[str, Any]
**Description**: Alias for to_check_dict for orchestrator compatibility.



## Usage Examples

### Class Usage

```python
# Using FileClassificationValidatorAgent
fileclassificationvalidatoragent = FileClassificationValidatorAgent()
fileclassificationvalidatoragent.scan()
fileclassificationvalidatoragent.to_check_dict()
```

### Function Usage

```python
# Using __init__
result = __init__(project_root)
```

```python
# Using scan
result = scan(target_territory)
```

```python
# Using to_check_dict
result = to_check_dict(target_territory)
```



---
**Generated**: 2026-03-26T09:39:05.213618
**Type**: api_reference
**Quality**: comprehensive
