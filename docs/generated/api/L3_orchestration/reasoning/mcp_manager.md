# API Documentation: mcp_manager

**Target Audience**: developers, api_users

# mcp_manager API Documentation

**File**: `mcp_manager.py`
**Classes**: 1
**Functions**: 3

## Classes

- **MCPConnectionManager**

## Functions

- **_resolve_tool** -> Any
- **load_mcp_config** -> dict[str, Any]
- **__init__**


## Class: MCPConnectionManager

**Description**: 
    Concrete implementation of the MCPConnectionManager Protocol.

    Routes call_tool() to live Windsurf MCP tool functions.
    All calls are resilient: errors are logged, None is returned on failure.
    

### Methods

#### __init__
**Parameters**: self, config



## Function: _resolve_tool

**Parameters**: tool_name
**Returns**: Any
**Description**: Resolve a logical tool name to a callable, or None if unavailable.



## Function: load_mcp_config

**Parameters**: config_path
**Returns**: dict[str, Any]
**Description**: 
    Load MCP configuration from a YAML or JSON file.

    Falls back to empty config dict if file is missing or unparseable.
    



## Function: __init__

**Parameters**: self, config


## Usage Examples

### Class Usage

```python
# Using MCPConnectionManager
mcpconnectionmanager = MCPConnectionManager()
```

### Function Usage

```python
# Using _resolve_tool
result = _resolve_tool(tool_name)
```

```python
# Using load_mcp_config
result = load_mcp_config(config_path)
```

```python
# Using __init__
result = __init__(config)
```



---
**Generated**: 2026-03-26T09:39:04.286900
**Type**: api_reference
**Quality**: comprehensive
