# API Documentation: action_node

**Target Audience**: developers, api_users

# action_node API Documentation

**File**: `action_node.py`
**Classes**: 1
**Functions**: 9

## Classes

- **ActionNode**

## Functions

- **_invoke_authorize_and_execute**
- **_make_execution_context**
- **__init__**
- **act** -> dict[str, Any]
- **act_simple** -> dict[str, Any]
- **_select_tools** -> list[dict[str, Any]]
- **_execute_tools** -> list[dict[str, Any]]
- **_format_output** -> str
- **get_statistics** -> dict[str, Any]


## Class: ActionNode

**Description**: 
    Sub-atomic action node - tool execution and output generation.

    Responsibilities:
    - Select appropriate tools
    - Execute tools
    - Format output
    - Handle execution errors
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize action node.

#### act
**Parameters**: self, reasoning
**Returns**: dict[str, Any]
**Description**: 
        Execute action based on reasoning.

        Args:
            reasoning: Reasoning result from ReasoningNode

        Returns:
            Action result with output and metadata
        

#### act_simple
**Parameters**: self, perceived
**Returns**: dict[str, Any]
**Description**: 
        Simple action for low-complexity intents (lazy evaluation).

        Args:
            perceived: Perceived state

        Returns:
            Simple action result
        

#### _select_tools
**Parameters**: self, plan
**Returns**: list[dict[str, Any]]
**Description**: 
        Select tools based on execution plan.

        Args:
            plan: Execution plan from ReasoningNode

        Returns:
            List of selected tools
        

#### _execute_tools
**Parameters**: self, tools, reasoning
**Returns**: list[dict[str, Any]]
**Description**: 
        Execute selected tools.

        Args:
            tools: Selected tools
            reasoning: Reasoning context

        Returns:
            Tool execution results
        

#### _format_output
**Parameters**: self, results, reasoning
**Returns**: str
**Description**: 
        Format final output from tool results.

        Args:
            results: Tool execution results
            reasoning: Reasoning context

        Returns:
            Formatted output string
        

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get action statistics.



## Function: _invoke_authorize_and_execute

**Parameters**: execution_context, target_callable, capability_token, payload


## Function: _make_execution_context

**Parameters**: run_id, capability_token, policy_hash, payload, target, action_class


## Function: __init__

**Parameters**: self
**Description**: Initialize action node.



## Function: act

**Parameters**: self, reasoning
**Returns**: dict[str, Any]
**Description**: 
        Execute action based on reasoning.

        Args:
            reasoning: Reasoning result from ReasoningNode

        Returns:
            Action result with output and metadata
        



## Function: act_simple

**Parameters**: self, perceived
**Returns**: dict[str, Any]
**Description**: 
        Simple action for low-complexity intents (lazy evaluation).

        Args:
            perceived: Perceived state

        Returns:
            Simple action result
        



## Function: _select_tools

**Parameters**: self, plan
**Returns**: list[dict[str, Any]]
**Description**: 
        Select tools based on execution plan.

        Args:
            plan: Execution plan from ReasoningNode

        Returns:
            List of selected tools
        



## Function: _execute_tools

**Parameters**: self, tools, reasoning
**Returns**: list[dict[str, Any]]
**Description**: 
        Execute selected tools.

        Args:
            tools: Selected tools
            reasoning: Reasoning context

        Returns:
            Tool execution results
        



## Function: _format_output

**Parameters**: self, results, reasoning
**Returns**: str
**Description**: 
        Format final output from tool results.

        Args:
            results: Tool execution results
            reasoning: Reasoning context

        Returns:
            Formatted output string
        



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get action statistics.



## Usage Examples

### Class Usage

```python
# Using ActionNode
actionnode = ActionNode()
actionnode.act()
actionnode.act_simple()
```

### Function Usage

```python
# Using _invoke_authorize_and_execute
result = _invoke_authorize_and_execute(execution_context, target_callable)
```

```python
# Using _make_execution_context
result = _make_execution_context(run_id, capability_token)
```

```python
# Using __init__
result = __init__()
```



---
**Generated**: 2026-03-26T09:39:03.752382
**Type**: api_reference
**Quality**: comprehensive
