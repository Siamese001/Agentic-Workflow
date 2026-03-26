# API Documentation: mcp_client_types

**Target Audience**: developers, api_users

# mcp_client_types API Documentation

**File**: `mcp_client_types.py`
**Classes**: 4
**Functions**: 15

## Classes

- **MCPClient** (inherits from Protocol)
- **MCPClientSpec**
- **MCPClientStub**
- **MCPClientRegistry**

## Functions

- **__call__** -> dict[str, object]
- **resolved_module** -> str | None
- **resolved_class** -> str | None
- **validate** -> None
- **__init__**
- **__call__** -> dict[str, Any]
- **__repr__** -> str
- **__init__**
- **register** -> None
- **get** -> Any | None
- **get_spec** -> MCPClientSpec | None
- **has** -> bool
- **list_clients** -> list[str]
- **is_stub** -> bool
- **clear** -> None


## Class: MCPClient

**Description**: Protocol defining the MCP client interface.

    All MCP clients must implement this protocol for type safety.
    

**Inherits from**: Protocol

### Methods

#### __call__
**Parameters**: self
**Returns**: dict[str, object]
**Description**: Execute the client operation.

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            Dict with operation result
        



## Class: MCPClientSpec

**Description**: Typed representation of a configured MCP client.

    This is the canonical schema for MCP client configuration,
    enforcing strict typing and validation.

    Attributes:
        name: Unique client identifier
        provider: Provider type (redis, chromadb, openai, etc.)
        module: Optional explicit Python module path
        class_name: Optional explicit class name
        parameters: Client initialization parameters
        optional: Whether this client is optional (won't fail if unavailable)
    

### Methods

#### resolved_module
**Parameters**: self
**Returns**: str | None
**Description**: Return explicit module or provider-mapped default.

        Returns:
            Module path or None for stub
        

#### resolved_class
**Parameters**: self
**Returns**: str | None
**Description**: Return explicit class_name or provider-mapped default.

        Returns:
            Class name or None
        

#### validate
**Parameters**: self
**Returns**: None
**Description**: Validate the spec configuration.

        Raises:
            ValueError: If spec is invalid
        



## Class: MCPClientStub

**Description**: Safe fallback MCP client.

    All MCP tools using this stub will receive a structured response
    indicating the client is stubbed. This prevents runtime failures
    while maintaining type safety.
    

### Methods

#### __init__
**Parameters**: self, name, parameters
**Description**: Initialize stub client.

        Args:
            name: Client name
            parameters: Optional parameters (for logging/debugging)
        

#### __call__
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: All calls return a structured stub result.

        Returns:
            Dict with stub=True and error message
        

#### __repr__
**Parameters**: self
**Returns**: str
**Description**: String representation.



## Class: MCPClientRegistry

**Description**: Registry for managing MCP clients.

    Provides centralized access to all configured MCP clients
    with type-safe retrieval.
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize empty registry.

#### register
**Parameters**: self, name, client
**Returns**: None
**Description**: Register a client instance.

        Args:
            name: Client name
            client: Instantiated client
        

#### get
**Parameters**: self, name
**Returns**: Any | None
**Description**: Get a client by name.

        Args:
            name: Client name

        Returns:
            Client instance or None if not found
        

#### get_spec
**Parameters**: self, name
**Returns**: MCPClientSpec | None
**Description**: Get a client spec by name.

        Args:
            name: Client name

        Returns:
            Client spec or None if not found
        

#### has
**Parameters**: self, name
**Returns**: bool
**Description**: Check if a client exists.

        Args:
            name: Client name

        Returns:
            True if client exists
        

#### list_clients
**Parameters**: self
**Returns**: list[str]
**Description**: List all registered client names.

        Returns:
            List of client names
        

#### is_stub
**Parameters**: self, name
**Returns**: bool
**Description**: Check if a client is a stub.

        Args:
            name: Client name

        Returns:
            True if client is a stub
        

#### clear
**Parameters**: self
**Returns**: None
**Description**: Clear all registered clients.



## Function: __call__

**Parameters**: self
**Returns**: dict[str, object]
**Description**: Execute the client operation.

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            Dict with operation result
        



## Function: resolved_module

**Parameters**: self
**Returns**: str | None
**Description**: Return explicit module or provider-mapped default.

        Returns:
            Module path or None for stub
        



## Function: resolved_class

**Parameters**: self
**Returns**: str | None
**Description**: Return explicit class_name or provider-mapped default.

        Returns:
            Class name or None
        



## Function: validate

**Parameters**: self
**Returns**: None
**Description**: Validate the spec configuration.

        Raises:
            ValueError: If spec is invalid
        



## Function: __init__

**Parameters**: self, name, parameters
**Description**: Initialize stub client.

        Args:
            name: Client name
            parameters: Optional parameters (for logging/debugging)
        



## Function: __call__

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: All calls return a structured stub result.

        Returns:
            Dict with stub=True and error message
        



## Function: __repr__

**Parameters**: self
**Returns**: str
**Description**: String representation.



## Function: __init__

**Parameters**: self
**Description**: Initialize empty registry.



## Function: register

**Parameters**: self, name, client
**Returns**: None
**Description**: Register a client instance.

        Args:
            name: Client name
            client: Instantiated client
        



## Function: get

**Parameters**: self, name
**Returns**: Any | None
**Description**: Get a client by name.

        Args:
            name: Client name

        Returns:
            Client instance or None if not found
        



## Function: get_spec

**Parameters**: self, name
**Returns**: MCPClientSpec | None
**Description**: Get a client spec by name.

        Args:
            name: Client name

        Returns:
            Client spec or None if not found
        



## Function: has

**Parameters**: self, name
**Returns**: bool
**Description**: Check if a client exists.

        Args:
            name: Client name

        Returns:
            True if client exists
        



## Function: list_clients

**Parameters**: self
**Returns**: list[str]
**Description**: List all registered client names.

        Returns:
            List of client names
        



## Function: is_stub

**Parameters**: self, name
**Returns**: bool
**Description**: Check if a client is a stub.

        Args:
            name: Client name

        Returns:
            True if client is a stub
        



## Function: clear

**Parameters**: self
**Returns**: None
**Description**: Clear all registered clients.



## Usage Examples

### Class Usage

```python
# Using MCPClient
mcpclient = MCPClient()
```

```python
# Using MCPClientSpec
mcpclientspec = MCPClientSpec()
mcpclientspec.resolved_module()
mcpclientspec.resolved_class()
```

```python
# Using MCPClientStub
mcpclientstub = MCPClientStub()
```

### Function Usage

```python
# Using __call__
result = __call__()
```

```python
# Using resolved_module
result = resolved_module()
```

```python
# Using resolved_class
result = resolved_class()
```



---
**Generated**: 2026-03-26T09:39:03.978757
**Type**: api_reference
**Quality**: comprehensive
