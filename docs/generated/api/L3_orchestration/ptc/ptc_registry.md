# API Documentation: ptc_registry

**Target Audience**: developers, api_users

# ptc_registry API Documentation

**File**: `ptc_registry.py`
**Classes**: 1
**Functions**: 10

## Classes

- **ToolRegistry**

## Functions

- **get_global_registry** -> ToolRegistry
- **register_tool** -> None
- **get_tool** -> tuple[ToolSpec, Callable]
- **list_tools** -> list[ToolSpec]
- **__init__** -> None
- **register** -> None
- **get** -> tuple[ToolSpec, Callable]
- **list** -> builtins.list[ToolSpec]
- **has** -> bool
- **count** -> int


## Class: ToolRegistry

**Description**: Deterministic registry for tools.

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize empty registry.

#### register
**Parameters**: self, spec, handler
**Returns**: None
**Description**: Register a tool with specification and handler.

        Args:
            spec: Tool specification
            handler: Handler function

        Raises:
            ValueError: If tool_id already exists or validation fails
        

#### get
**Parameters**: self, tool_id
**Returns**: tuple[ToolSpec, Callable]
**Description**: Get tool specification and handler.

        Args:
            tool_id: Tool identifier

        Returns:
            Tuple of (spec, handler)

        Raises:
            ValueError: If tool_id not found
        

#### list
**Parameters**: self
**Returns**: builtins.list[ToolSpec]
**Description**: List all registered tool specifications.

        Returns:
            List of ToolSpec objects sorted by tool_id
        

#### has
**Parameters**: self, tool_id
**Returns**: bool
**Description**: Check if tool is registered.

        Args:
            tool_id: Tool identifier

        Returns:
            True if tool exists
        

#### count
**Parameters**: self
**Returns**: int
**Description**: Get number of registered tools.

        Returns:
            Number of tools
        



## Function: get_global_registry

**Returns**: ToolRegistry
**Description**: Get the global tool registry.

    Returns:
        Global ToolRegistry instance
    



## Function: register_tool

**Parameters**: spec, handler
**Returns**: None
**Description**: Register a tool in the global registry.

    Args:
        spec: Tool specification
        handler: Handler function
    



## Function: get_tool

**Parameters**: tool_id
**Returns**: tuple[ToolSpec, Callable]
**Description**: Get tool from global registry.

    Args:
        tool_id: Tool identifier

    Returns:
        Tuple of (spec, handler)
    



## Function: list_tools

**Returns**: list[ToolSpec]
**Description**: List all tools in global registry.

    Returns:
        List of ToolSpec objects
    



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize empty registry.



## Function: register

**Parameters**: self, spec, handler
**Returns**: None
**Description**: Register a tool with specification and handler.

        Args:
            spec: Tool specification
            handler: Handler function

        Raises:
            ValueError: If tool_id already exists or validation fails
        



## Function: get

**Parameters**: self, tool_id
**Returns**: tuple[ToolSpec, Callable]
**Description**: Get tool specification and handler.

        Args:
            tool_id: Tool identifier

        Returns:
            Tuple of (spec, handler)

        Raises:
            ValueError: If tool_id not found
        



## Function: list

**Parameters**: self
**Returns**: builtins.list[ToolSpec]
**Description**: List all registered tool specifications.

        Returns:
            List of ToolSpec objects sorted by tool_id
        



## Function: has

**Parameters**: self, tool_id
**Returns**: bool
**Description**: Check if tool is registered.

        Args:
            tool_id: Tool identifier

        Returns:
            True if tool exists
        



## Function: count

**Parameters**: self
**Returns**: int
**Description**: Get number of registered tools.

        Returns:
            Number of tools
        



## Usage Examples

### Class Usage

```python
# Using ToolRegistry
toolregistry = ToolRegistry()
toolregistry.register()
toolregistry.get()
```

### Function Usage

```python
# Using get_global_registry
result = get_global_registry()
```

```python
# Using register_tool
result = register_tool(spec, handler)
```

```python
# Using get_tool
result = get_tool(tool_id)
```



---
**Generated**: 2026-03-26T09:39:04.244257
**Type**: api_reference
**Quality**: comprehensive
