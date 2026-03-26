# API Documentation: action_capability

**Target Audience**: developers, api_users

# action_capability API Documentation

**File**: `action_capability.py`
**Classes**: 4
**Functions**: 5

## Classes

- **ActionCapability** (inherits from Enum)
- **ActionRequest**
- **ActionResult**
- **IActionPlane** (inherits from ABC)

## Functions

- **to_dict** -> dict[str, Any]
- **to_dict** -> dict[str, Any]
- **get_available_tools** -> list[str]
- **get_tool_schema** -> dict[str, Any]
- **get_capabilities** -> list[ActionCapability]


## Class: ActionCapability

**Description**: Capabilities provided by the action plane.

**Inherits from**: Enum



## Class: ActionRequest

**Description**: Request for action execution.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: ActionResult

**Description**: Result from action execution.

### Methods

#### to_dict
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Class: IActionPlane

**Description**: Interface for the Action Plane (Hands).

    The action plane is responsible for:
    - Tool Execution: Running external tools and APIs
    - Side Effects: Performing actions that change state
    - Resource Management: Managing connections and resources
    - Error Handling: Dealing with failures gracefully

    L2 Constraint: Side effects are allowed but must be:
    - Observable (logged/traced)
    - Reversible when possible
    - Protected by resilience middleware
    

**Inherits from**: ABC

### Methods

#### get_available_tools
**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available tools.

        Returns:
            List of tool names
        

#### get_tool_schema
**Parameters**: self, tool_name
**Returns**: dict[str, Any]
**Description**: Get schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool schema with parameters and types
        

#### get_capabilities
**Parameters**: self
**Returns**: list[ActionCapability]
**Description**: Get list of supported action capabilities.

        Returns:
            List of capabilities this plane supports
        



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: to_dict

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to dictionary.



## Function: get_available_tools

**Parameters**: self
**Returns**: list[str]
**Description**: Get list of available tools.

        Returns:
            List of tool names
        



## Function: get_tool_schema

**Parameters**: self, tool_name
**Returns**: dict[str, Any]
**Description**: Get schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool schema with parameters and types
        



## Function: get_capabilities

**Parameters**: self
**Returns**: list[ActionCapability]
**Description**: Get list of supported action capabilities.

        Returns:
            List of capabilities this plane supports
        



## Usage Examples

### Class Usage

```python
# Using ActionCapability
actioncapability = ActionCapability()
```

```python
# Using ActionRequest
actionrequest = ActionRequest()
actionrequest.to_dict()
```

```python
# Using ActionResult
actionresult = ActionResult()
actionresult.to_dict()
```

### Function Usage

```python
# Using to_dict
result = to_dict()
```

```python
# Using to_dict
result = to_dict()
```

```python
# Using get_available_tools
result = get_available_tools()
```



---
**Generated**: 2026-03-26T09:39:02.725882
**Type**: api_reference
**Quality**: comprehensive
