# API Documentation: function_tool

**Target Audience**: developers, api_users

# function_tool API Documentation

**File**: `function_tool.py`
**Classes**: 1
**Functions**: 2

## Classes

- **FunctionTool** (inherits from BaseTool)

## Functions

- **__init__**
- **execute** -> Any


## Class: FunctionTool

**Description**: A tool that wraps a callable function.

**Inherits from**: BaseTool

### Methods

#### __init__
**Parameters**: self, name, func, description

#### execute
**Parameters**: self
**Returns**: Any
**Description**: Execute the wrapped function.



## Function: __init__

**Parameters**: self, name, func, description


## Function: execute

**Parameters**: self
**Returns**: Any
**Description**: Execute the wrapped function.



## Usage Examples

### Class Usage

```python
# Using FunctionTool
functiontool = FunctionTool()
functiontool.execute()
```

### Function Usage

```python
# Using __init__
result = __init__(name, func)
```

```python
# Using execute
result = execute()
```



---
**Generated**: 2026-03-26T09:39:03.153513
**Type**: api_reference
**Quality**: comprehensive
