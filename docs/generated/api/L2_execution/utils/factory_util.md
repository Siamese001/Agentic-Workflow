# API Documentation: factory_util

**Target Audience**: developers, api_users

# factory_util API Documentation

**File**: `factory_util.py`
**Classes**: 0
**Functions**: 3


## Functions

- **parse_mcp_client_specs** -> list[MCPClientSpec]
- **instantiate_mcp_client** -> object
- **create_mcp_registry** -> MCPClientRegistry


## Function: parse_mcp_client_specs

**Parameters**: raw_specs
**Returns**: list[MCPClientSpec]
**Description**: Validate and normalize MCP client specifications.

    Args:
        raw_specs: List of raw spec dictionaries

    Returns:
        List of validated MCPClientSpec instances

    Raises:
        ValueError: If specs are invalid
    



## Function: instantiate_mcp_client

**Parameters**: spec
**Returns**: object
**Description**: Create an MCP client instance from a validated spec.

    Args:
        spec: Validated MCPClientSpec

    Returns:
        Instantiated client

    Raises:
        MCPClientInitializationError: If instantiation fails
    



## Function: create_mcp_registry

**Parameters**: specs, fail_on_error
**Returns**: MCPClientRegistry
**Description**: Create an MCP client registry from specifications.

    Args:
        specs: List of client specifications
        fail_on_error: If True, raise on any initialization error

    Returns:
        Populated MCPClientRegistry

    Raises:
        MCPClientInitializationError: If fail_on_error=True and init fails
    



## Usage Examples

### Function Usage

```python
# Using parse_mcp_client_specs
result = parse_mcp_client_specs(raw_specs)
```

```python
# Using instantiate_mcp_client
result = instantiate_mcp_client(spec)
```

```python
# Using create_mcp_registry
result = create_mcp_registry(specs, fail_on_error)
```



---
**Generated**: 2026-03-26T09:39:04.063180
**Type**: api_reference
**Quality**: comprehensive
