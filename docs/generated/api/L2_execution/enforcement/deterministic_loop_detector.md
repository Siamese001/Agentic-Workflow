# API Documentation: deterministic_loop_detector

**Target Audience**: developers, api_users

# deterministic_loop_detector API Documentation

**File**: `deterministic_loop_detector.py`
**Classes**: 3
**Functions**: 5

## Classes

- **ToolBudgetExceededError** (inherits from Exception)
- **ToolBudget**
- **DeterministicLoopDetector**

## Functions

- **__init__**
- **__init__**
- **increment_and_check** -> None
- **get_current_step_count** -> int
- **reset_trace** -> None


## Class: ToolBudgetExceededError

**Description**: Raised when a tool execution exceeds its deterministic step budget.

**Inherits from**: Exception

### Methods

#### __init__
**Parameters**: self, tool_name, budget



## Class: ToolBudget

**Description**: Defines the deterministic execution budget for a tool.



## Class: DeterministicLoopDetector

**Description**: 
    A deterministic circuit-breaker to prevent infinite loops in tool execution.

    This detector enforces Guarantee #10 by using a step counter instead of
    wall-clock time, ensuring that loop detection is replayable and not subject
    to variations in machine performance.

    It is designed to be attached to the L2 Per-Tool-Call (PTC) execution context.
    

### Methods

#### __init__
**Parameters**: self

#### increment_and_check
**Parameters**: self, trace_id, tool_name, budget
**Returns**: None
**Description**: 
        Increments the execution counter for a given tool and checks against its budget.

        This method must be called once per logical step within a tool's execution.

        Args:
            trace_id: The unique identifier for the current execution trace.
            tool_name: The name of the tool being executed.
            budget: The deterministic budget for the tool.

        Raises:
            ToolBudgetExceededError: If the counter exceeds the tool's max_steps.
        

#### get_current_step_count
**Parameters**: self, trace_id, tool_name
**Returns**: int
**Description**: Returns the current step count for a tool within a trace.

#### reset_trace
**Parameters**: self, trace_id
**Returns**: None
**Description**: Resets all counters for a given trace_id (for testing or context closure).



## Function: __init__

**Parameters**: self, tool_name, budget


## Function: __init__

**Parameters**: self


## Function: increment_and_check

**Parameters**: self, trace_id, tool_name, budget
**Returns**: None
**Description**: 
        Increments the execution counter for a given tool and checks against its budget.

        This method must be called once per logical step within a tool's execution.

        Args:
            trace_id: The unique identifier for the current execution trace.
            tool_name: The name of the tool being executed.
            budget: The deterministic budget for the tool.

        Raises:
            ToolBudgetExceededError: If the counter exceeds the tool's max_steps.
        



## Function: get_current_step_count

**Parameters**: self, trace_id, tool_name
**Returns**: int
**Description**: Returns the current step count for a tool within a trace.



## Function: reset_trace

**Parameters**: self, trace_id
**Returns**: None
**Description**: Resets all counters for a given trace_id (for testing or context closure).



## Usage Examples

### Class Usage

```python
# Using ToolBudgetExceededError
toolbudgetexceedederror = ToolBudgetExceededError()
```

```python
# Using ToolBudget
toolbudget = ToolBudget()
```

```python
# Using DeterministicLoopDetector
deterministicloopdetector = DeterministicLoopDetector()
deterministicloopdetector.increment_and_check()
deterministicloopdetector.get_current_step_count()
```

### Function Usage

```python
# Using __init__
result = __init__(tool_name, budget)
```

```python
# Using __init__
result = __init__()
```

```python
# Using increment_and_check
result = increment_and_check(trace_id, tool_name)
```



---
**Generated**: 2026-03-26T09:39:03.686438
**Type**: api_reference
**Quality**: comprehensive
