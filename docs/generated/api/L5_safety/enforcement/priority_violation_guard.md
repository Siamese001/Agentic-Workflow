# API Documentation: priority_violation_guard

**Target Audience**: developers, api_users

# priority_violation_guard API Documentation

**File**: `priority_violation_guard.py`
**Classes**: 2
**Functions**: 11

## Classes

- **OptimizationPriority** (inherits from Enum)
- **PriorityViolationGuard**

## Functions

- **get_priority_violation_guard** -> PriorityViolationGuard
- **reset_priority_violation_guard** -> None
- **__init__** -> None
- **can_start_operation** -> tuple[bool, str]
- **start_operation** -> bool
- **end_operation** -> bool
- **get_active_operations** -> list[tuple[str, OptimizationPriority]]
- **get_violations** -> list[dict[str, any]]
- **clear_violations** -> None
- **reset** -> None
- **get_stack_summary** -> dict[str, any]


## Class: OptimizationPriority

**Description**: Priority levels for optimization operations.

    Higher numeric values = higher priority.
    Operations must respect priority ordering.
    

**Inherits from**: Enum



## Class: PriorityViolationGuard

**Description**: Enforces priority constraints on optimization operations.

    Maintains a stack of active operations and validates that
    new operations respect priority constraints.
    

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the priority violation guard.

#### can_start_operation
**Parameters**: self, operation_id, priority, required_priority
**Returns**: tuple[bool, str]
**Description**: Check if an operation can start based on priority constraints.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            (can_start, reason) tuple
        

#### start_operation
**Parameters**: self, operation_id, priority, required_priority
**Returns**: bool
**Description**: Start an operation if priority constraints are satisfied.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            True if operation started, False otherwise.
        

#### end_operation
**Parameters**: self, operation_id
**Returns**: bool
**Description**: End an operation and remove it from the stack.

        Args:
            operation_id: Unique identifier for the operation.

        Returns:
            True if operation was found and removed, False otherwise.
        

#### get_active_operations
**Parameters**: self
**Returns**: list[tuple[str, OptimizationPriority]]
**Description**: Get the current stack of active operations.

        Returns:
            List of (operation_id, priority) tuples.
        

#### get_violations
**Parameters**: self
**Returns**: list[dict[str, any]]
**Description**: Get all priority violations.

        Returns:
            List of violation dictionaries.
        

#### clear_violations
**Parameters**: self
**Returns**: None
**Description**: Clear all recorded violations.

#### reset
**Parameters**: self
**Returns**: None
**Description**: Reset the guard (for testing).

#### get_stack_summary
**Parameters**: self
**Returns**: dict[str, any]
**Description**: Get a summary of the current operation stack.

        Returns:
            Dictionary with stack statistics.
        



## Function: get_priority_violation_guard

**Returns**: PriorityViolationGuard
**Description**: Get the global priority violation guard instance.

    Returns:
        The global PriorityViolationGuard instance.
    



## Function: reset_priority_violation_guard

**Returns**: None
**Description**: Reset the global priority violation guard (for testing).



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the priority violation guard.



## Function: can_start_operation

**Parameters**: self, operation_id, priority, required_priority
**Returns**: tuple[bool, str]
**Description**: Check if an operation can start based on priority constraints.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            (can_start, reason) tuple
        



## Function: start_operation

**Parameters**: self, operation_id, priority, required_priority
**Returns**: bool
**Description**: Start an operation if priority constraints are satisfied.

        Args:
            operation_id: Unique identifier for the operation.
            priority: Priority of the operation.
            required_priority: Minimum priority required for this operation.

        Returns:
            True if operation started, False otherwise.
        



## Function: end_operation

**Parameters**: self, operation_id
**Returns**: bool
**Description**: End an operation and remove it from the stack.

        Args:
            operation_id: Unique identifier for the operation.

        Returns:
            True if operation was found and removed, False otherwise.
        



## Function: get_active_operations

**Parameters**: self
**Returns**: list[tuple[str, OptimizationPriority]]
**Description**: Get the current stack of active operations.

        Returns:
            List of (operation_id, priority) tuples.
        



## Function: get_violations

**Parameters**: self
**Returns**: list[dict[str, any]]
**Description**: Get all priority violations.

        Returns:
            List of violation dictionaries.
        



## Function: clear_violations

**Parameters**: self
**Returns**: None
**Description**: Clear all recorded violations.



## Function: reset

**Parameters**: self
**Returns**: None
**Description**: Reset the guard (for testing).



## Function: get_stack_summary

**Parameters**: self
**Returns**: dict[str, any]
**Description**: Get a summary of the current operation stack.

        Returns:
            Dictionary with stack statistics.
        



## Usage Examples

### Class Usage

```python
# Using OptimizationPriority
optimizationpriority = OptimizationPriority()
```

```python
# Using PriorityViolationGuard
priorityviolationguard = PriorityViolationGuard()
priorityviolationguard.can_start_operation()
priorityviolationguard.start_operation()
```

### Function Usage

```python
# Using get_priority_violation_guard
result = get_priority_violation_guard()
```

```python
# Using reset_priority_violation_guard
result = reset_priority_violation_guard()
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:04.902409
**Type**: api_reference
**Quality**: comprehensive
