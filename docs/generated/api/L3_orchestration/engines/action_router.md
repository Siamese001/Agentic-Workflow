# API Documentation: action_router

**Target Audience**: developers, api_users

# action_router API Documentation

**File**: `action_router.py`
**Classes**: 1
**Functions**: 2

## Classes

- **ActionNode**

## Functions

- **__init__**
- **execute_plan** -> dict[str, Any]


## Class: ActionNode

**Description**: 
    The 'Hands' of the Agent.
    Responsibility: Execute the Cognitive Node's plan safely.
    Security: STRICT WHITELIST of allowed tools.
    

### Methods

#### __init__
**Parameters**: self, work_dir
**Description**: 
        Initializes the ActionNode with a specified working directory.

        Args:
            work_dir (str): The path to the workspace directory.
        

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
        



## Function: __init__

**Parameters**: self, work_dir
**Description**: 
        Initializes the ActionNode with a specified working directory.

        Args:
            work_dir (str): The path to the workspace directory.
        



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
        



## Usage Examples

### Class Usage

```python
# Using ActionNode
actionnode = ActionNode()
actionnode.execute_plan()
```

### Function Usage

```python
# Using __init__
result = __init__(work_dir)
```

```python
# Using execute_plan
result = execute_plan(plan)
```



---
**Generated**: 2026-03-26T09:39:04.129026
**Type**: api_reference
**Quality**: comprehensive
