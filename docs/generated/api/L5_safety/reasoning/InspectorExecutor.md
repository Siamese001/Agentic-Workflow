# API Documentation: InspectorExecutor

**Target Audience**: developers, api_users

# InspectorExecutor API Documentation

**File**: `InspectorExecutor.py`
**Classes**: 1
**Functions**: 1

## Classes

- **InspectorExecutor** (inherits from InspectionCapability, SovereignBaseAgent)

## Functions

- **__post_init__** -> None


## Class: InspectorExecutor

**Description**: Parameterized inspector that dispatches to domain-specific check logic.

    Usage:
        inspector = InspectorExecutor(inspector_type="dag_runtime")
    

**Inherits from**: InspectionCapability, SovereignBaseAgent

### Methods

#### __post_init__
**Parameters**: self
**Returns**: None



## Function: __post_init__

**Parameters**: self
**Returns**: None


## Usage Examples

### Class Usage

```python
# Using InspectorExecutor
inspectorexecutor = InspectorExecutor()
```

### Function Usage

```python
# Using __post_init__
result = __post_init__()
```



---
**Generated**: 2026-03-26T09:39:05.277040
**Type**: api_reference
**Quality**: comprehensive
