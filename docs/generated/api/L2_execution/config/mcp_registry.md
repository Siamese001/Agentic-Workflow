# API Documentation: mcp_registry

**Target Audience**: developers, api_users

# mcp_registry API Documentation

**File**: `mcp_registry.py`
**Classes**: 2
**Functions**: 4

## Classes

- **McpServerMode** (inherits from str, Enum)
- **McpServerConfig** (inherits from BaseModel)

## Functions

- **get_mcp_registry** -> dict[str, McpServerConfig]
- **get_mcps_by_layer** -> list[McpServerConfig]
- **get_mcp_by_capability** -> list[McpServerConfig]
- **validate_mcp_registry** -> list[str]


## Class: McpServerMode

**Description**: Deployment mode for MCP servers.

**Inherits from**: str, Enum



## Class: McpServerConfig

**Description**: Configuration for a single MCP server integration.

**Inherits from**: BaseModel



## Function: get_mcp_registry

**Returns**: dict[str, McpServerConfig]
**Description**: Get the full MCP registry with conditional entries.



## Function: get_mcps_by_layer

**Parameters**: layer
**Returns**: list[McpServerConfig]
**Description**: Get all MCP servers assigned to a specific layer.



## Function: get_mcp_by_capability

**Parameters**: capability
**Returns**: list[McpServerConfig]
**Description**: Find MCP servers providing a specific capability.



## Function: validate_mcp_registry

**Returns**: list[str]
**Description**: Validate MCP registry for constitutional compliance.



## Usage Examples

### Class Usage

```python
# Using McpServerMode
mcpservermode = McpServerMode()
```

```python
# Using McpServerConfig
mcpserverconfig = McpServerConfig()
```

### Function Usage

```python
# Using get_mcp_registry
result = get_mcp_registry()
```

```python
# Using get_mcps_by_layer
result = get_mcps_by_layer(layer)
```

```python
# Using get_mcp_by_capability
result = get_mcp_by_capability(capability)
```



---
**Generated**: 2026-03-26T09:39:03.626478
**Type**: api_reference
**Quality**: comprehensive
