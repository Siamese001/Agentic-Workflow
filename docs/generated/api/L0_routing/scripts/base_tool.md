# API Documentation: base_tool

**Target Audience**: developers, api_users

# base_tool API Documentation

**File**: `base_tool.py`
**Classes**: 4
**Functions**: 4

## Classes

- **BaseTool** (inherits from BaseModel, ABC)
- **FunctionalTool** (inherits from BaseTool)
- **ToolRegistry**
- **Config**

## Functions

- **__init__**
- **register**
- **get** -> BaseTool | None
- **list_tools** -> str


## Class: BaseTool

**Description**: 
    Abstract base class for all executable tools.
    

**Inherits from**: BaseModel, ABC



## Class: FunctionalTool

**Description**: 
    Wrapper to turn a Python function into a Tool.
    

**Inherits from**: BaseTool



## Class: ToolRegistry

**Description**: 
    Manager for the agent's available toolkit.
    

### Methods

#### __init__
**Parameters**: self

#### register
**Parameters**: self, tool

#### get
**Parameters**: self, name
**Returns**: BaseTool | None

#### list_tools
**Parameters**: self
**Returns**: str



## Class: Config



## Function: __init__

**Parameters**: self


## Function: register

**Parameters**: self, tool


## Function: get

**Parameters**: self, name
**Returns**: BaseTool | None


## Function: list_tools

**Parameters**: self
**Returns**: str


## Usage Examples

### Class Usage

```python
# Using BaseTool
basetool = BaseTool()
```

```python
# Using FunctionalTool
functionaltool = FunctionalTool()
```

```python
# Using ToolRegistry
toolregistry = ToolRegistry()
toolregistry.register()
toolregistry.get()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using register
result = register(tool)
```

```python
# Using get
result = get(name)
```



---
**Generated**: 2026-03-26T09:39:02.761368
**Type**: api_reference
**Quality**: comprehensive
