# API Documentation: SurgicalHealingAdapter

**Target Audience**: developers, api_users

# SurgicalHealingAdapter API Documentation

**File**: `SurgicalHealingAdapter.py`
**Classes**: 2
**Functions**: 6

## Classes

- **SurgicalHealingResult**
- **SurgicalHealingAdapter**

## Functions

- **to_dict** -> dict[str, Any]
- **__init__**
- **_infer_fix_type** -> str
- **create_context_from_detection** -> SurgicalContext | None
- **create_batch_context** -> SurgicalContext | None
- **apply_surgical_healing** -> SurgicalHealingResult


## Class: SurgicalHealingResult

**Description**: Result from a surgical healing operation.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Class: SurgicalHealingAdapter

**Description**: 
    Bridges legacy healing detection results to SurgicalContext for CST healing.

    Converts dictionaries produced by legacy heal_repository() detectors into
    structured SurgicalContext objects that can be processed by SurgicalCSTHealerMixin.
    

### Methods

#### __init__
**Parameters**: self, agent_name

#### _infer_fix_type
**Parameters**: self, constraint_type
**Returns**: str
**Description**: Infer the fix type from the constraint type string.

#### create_context_from_detection
**Parameters**: self, file_path, detection_result, detection_method
**Returns**: SurgicalContext | None
**Description**: 
        Create a SurgicalContext from a single detection result dict.

        Args:
            file_path: Path to the file to heal
            detection_result: Dict with keys: type, line, message, severity, etc.
            detection_method: Name of the detection method that found the violation

        Returns:
            SurgicalContext or None if file does not exist
        

#### create_batch_context
**Parameters**: self, file_path, detection_results, detection_method
**Returns**: SurgicalContext | None
**Description**: 
        Create a SurgicalContext from multiple detection result dicts.

        Args:
            file_path: Path to the file to heal
            detection_results: List of detection result dicts
            detection_method: Name of the detection method

        Returns:
            SurgicalContext or None if file does not exist
        

#### apply_surgical_healing
**Parameters**: self, context
**Returns**: SurgicalHealingResult
**Description**: 
        Apply surgical healing using the CST mixin.

        Args:
            context: SurgicalContext to heal, or None

        Returns:
            SurgicalHealingResult
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary representation.



## Function: __init__

**Parameters**: self, agent_name


## Function: _infer_fix_type

**Parameters**: self, constraint_type
**Returns**: str
**Description**: Infer the fix type from the constraint type string.



## Function: create_context_from_detection

**Parameters**: self, file_path, detection_result, detection_method
**Returns**: SurgicalContext | None
**Description**: 
        Create a SurgicalContext from a single detection result dict.

        Args:
            file_path: Path to the file to heal
            detection_result: Dict with keys: type, line, message, severity, etc.
            detection_method: Name of the detection method that found the violation

        Returns:
            SurgicalContext or None if file does not exist
        



## Function: create_batch_context

**Parameters**: self, file_path, detection_results, detection_method
**Returns**: SurgicalContext | None
**Description**: 
        Create a SurgicalContext from multiple detection result dicts.

        Args:
            file_path: Path to the file to heal
            detection_results: List of detection result dicts
            detection_method: Name of the detection method

        Returns:
            SurgicalContext or None if file does not exist
        



## Function: apply_surgical_healing

**Parameters**: self, context
**Returns**: SurgicalHealingResult
**Description**: 
        Apply surgical healing using the CST mixin.

        Args:
            context: SurgicalContext to heal, or None

        Returns:
            SurgicalHealingResult
        



## Usage Examples

### Class Usage

```python
# Using SurgicalHealingResult
surgicalhealingresult = SurgicalHealingResult()
surgicalhealingresult.to_dict()
```

```python
# Using SurgicalHealingAdapter
surgicalhealingadapter = SurgicalHealingAdapter()
surgicalhealingadapter.create_context_from_detection()
surgicalhealingadapter.create_batch_context()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using __init__
result = __init__(agent_name)
```

```python
# Using _infer_fix_type
result = _infer_fix_type(constraint_type)
```



---
**Generated**: 2026-03-26T09:39:04.960433
**Type**: api_reference
**Quality**: comprehensive
