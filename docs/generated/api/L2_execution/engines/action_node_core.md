# API Documentation: action_node_core

**Target Audience**: developers, api_users

# action_node_core API Documentation

**File**: `action_node_core.py`
**Classes**: 1
**Functions**: 3

## Classes

- **ActionNodeCore**

## Functions

- **__init__**
- **execute_plan** -> dict[str, Any]
- **_execute_single_step** -> dict[str, Any]


## Class: ActionNodeCore

**Description**: 
    Core execution logic for ActionNode.
    Handles plan parsing and step orchestration.
    

### Methods

#### __init__
**Parameters**: self, work_dir, allowed_tools
**Description**: 
        Initialize core executor.

        Args:
            work_dir (str): Working directory path
            allowed_tools (Dict[str, Any]): Map of tool names to implementations
        

#### execute_plan
**Parameters**: self, plan
**Returns**: dict[str, Any]
**Description**: 
        Executes a full plan sequence from the Cognitive Node.

        Args:
            plan (Dict[str, Any]): A dictionary representing the plan,
                                   expected to contain 'goal' and 'steps'.

        Returns:
            Dict[str, Any]: A dictionary containing the overall status and results
                            of each executed step.
        

#### _execute_single_step
**Parameters**: self, step
**Returns**: dict[str, Any]
**Description**: 
        Parses a single step, validates the tool, and executes it.

        Args:
            step (Dict[str, Any]): A dictionary representing a single action step,
                                   expected to contain 'action' and 'params'.

        Returns:
            Dict[str, Any]: A dictionary containing the step number, status, and output.
        



## Function: __init__

**Parameters**: self, work_dir, allowed_tools
**Description**: 
        Initialize core executor.

        Args:
            work_dir (str): Working directory path
            allowed_tools (Dict[str, Any]): Map of tool names to implementations
        



## Function: execute_plan

**Parameters**: self, plan
**Returns**: dict[str, Any]
**Description**: 
        Executes a full plan sequence from the Cognitive Node.

        Args:
            plan (Dict[str, Any]): A dictionary representing the plan,
                                   expected to contain 'goal' and 'steps'.

        Returns:
            Dict[str, Any]: A dictionary containing the overall status and results
                            of each executed step.
        



## Function: _execute_single_step

**Parameters**: self, step
**Returns**: dict[str, Any]
**Description**: 
        Parses a single step, validates the tool, and executes it.

        Args:
            step (Dict[str, Any]): A dictionary representing a single action step,
                                   expected to contain 'action' and 'params'.

        Returns:
            Dict[str, Any]: A dictionary containing the step number, status, and output.
        



## Usage Examples

### Class Usage

```python
# Using ActionNodeCore
actionnodecore = ActionNodeCore()
actionnodecore.execute_plan()
```

### Function Usage

```python
# Using __init__
result = __init__(work_dir, allowed_tools)
```

```python
# Using execute_plan
result = execute_plan(plan)
```

```python
# Using _execute_single_step
result = _execute_single_step(step)
```



---
**Generated**: 2026-03-26T09:39:03.755361
**Type**: api_reference
**Quality**: comprehensive
