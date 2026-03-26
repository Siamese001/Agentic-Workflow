# API Documentation: base_tool_script

**Target Audience**: developers, api_users

# base_tool_script API Documentation

**File**: `base_tool_script.py`
**Classes**: 2
**Functions**: 11

## Classes

- **BaseTool**
- **tool_registry**

## Functions

- **__init__**
- **execute** -> Any
- **is_enabled** -> bool
- **enable** -> None
- **disable** -> None
- **__init__**
- **register** -> None
- **unregister** -> None
- **get** -> BaseTool | None
- **list_tools** -> list[str]
- **execute** -> Any


## Class: BaseTool

**Description**: Base class for all tools in the registry.

### Methods

#### __init__
**Parameters**: self, name, description

#### execute
**Parameters**: self
**Returns**: Any
**Description**: Execute the tool. Override in subclasses.

#### is_enabled
**Parameters**: self
**Returns**: bool
**Description**: Check if tool is enabled.

#### enable
**Parameters**: self
**Returns**: None
**Description**: Enable the tool.

#### disable
**Parameters**: self
**Returns**: None
**Description**: Disable the tool.



## Class: tool_registry

**Description**: Registry for managing tools.

### Methods

#### __init__
**Parameters**: self

#### register
**Parameters**: self, tool
**Returns**: None
**Description**: Register a tool.

#### unregister
**Parameters**: self, name
**Returns**: None
**Description**: Unregister a tool by name.

#### get
**Parameters**: self, name
**Returns**: BaseTool | None
**Description**: Get a tool by name.

#### list_tools
**Parameters**: self
**Returns**: list[str]
**Description**: List all registered tool names.

#### execute
**Parameters**: self, name
**Returns**: Any
**Description**: Execute a tool by name.



## Function: __init__

**Parameters**: self, name, description


## Function: execute

**Parameters**: self
**Returns**: Any
**Description**: Execute the tool. Override in subclasses.



## Function: is_enabled

**Parameters**: self
**Returns**: bool
**Description**: Check if tool is enabled.



## Function: enable

**Parameters**: self
**Returns**: None
**Description**: Enable the tool.



## Function: disable

**Parameters**: self
**Returns**: None
**Description**: Disable the tool.



## Function: __init__

**Parameters**: self


## Function: register

**Parameters**: self, tool
**Returns**: None
**Description**: Register a tool.



## Function: unregister

**Parameters**: self, name
**Returns**: None
**Description**: Unregister a tool by name.



## Function: get

**Parameters**: self, name
**Returns**: BaseTool | None
**Description**: Get a tool by name.



## Function: list_tools

**Parameters**: self
**Returns**: list[str]
**Description**: List all registered tool names.



## Function: execute

**Parameters**: self, name
**Returns**: Any
**Description**: Execute a tool by name.



## Usage Examples

### Class Usage

```python
# Using BaseTool
basetool = BaseTool()
basetool.execute()
basetool.is_enabled()
```

```python
# Using tool_registry
tool_registry = tool_registry()
tool_registry.register()
tool_registry.unregister()
```

### Function Usage

```python
# Using __init__
result = __init__(name, description)
```

```python
# Using execute
result = execute()
```

```python
# Using is_enabled
result = is_enabled()
```



---
**Generated**: 2026-03-26T09:39:02.763369
**Type**: api_reference
**Quality**: comprehensive
