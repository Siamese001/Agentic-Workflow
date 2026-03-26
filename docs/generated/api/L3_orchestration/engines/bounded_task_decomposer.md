# API Documentation: bounded_task_decomposer

**Target Audience**: developers, api_users

# bounded_task_decomposer API Documentation

**File**: `bounded_task_decomposer.py`
**Classes**: 3
**Functions**: 2

## Classes

- **TaskBlastRadiusViolation** (inherits from Exception)
- **DecompositionPolicy**
- **DecompositionResult** (inherits from NamedTuple)

## Functions

- **decompose_task** -> DecompositionResult
- **__init__**


## Class: TaskBlastRadiusViolation

**Description**: Raised when a task exceeds its defined blast radius limits.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, message, violation_details



## Class: DecompositionPolicy

**Description**: Defines the blast radius limits for task decomposition.



## Class: DecompositionResult

**Description**: The result of a task decomposition operation.

**Inherits from**: NamedTuple



## Function: decompose_task

**Parameters**: task, policy
**Returns**: DecompositionResult
**Description**: 
    Decomposes a large task into smaller, bounded subtasks.

    This function enforces Guarantee #8 by ensuring that no single task is too
    large or complex, thus limiting its potential blast radius. It is a critical
    sovereign gate in L3, rejecting tasks that cannot be safely decomposed.

    Args:
        task: The task to be decomposed.
        policy: The decomposition policy defining the blast radius limits.

    Returns:
        A DecompositionResult containing the list of subtasks or a violation.
    



## Function: __init__

**Parameters**: self, message, violation_details


## Usage Examples

### Class Usage

```python
# Using TaskBlastRadiusViolation
taskblastradiusviolation = TaskBlastRadiusViolation()
```

```python
# Using DecompositionPolicy
decompositionpolicy = DecompositionPolicy()
```

```python
# Using DecompositionResult
decompositionresult = DecompositionResult()
```

### Function Usage

```python
# Using decompose_task
result = decompose_task(task, policy)
```

```python
# Using __init__
result = __init__(message, violation_details)
```



---
**Generated**: 2026-03-26T09:39:04.141875
**Type**: api_reference
**Quality**: comprehensive
