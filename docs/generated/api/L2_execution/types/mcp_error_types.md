# API Documentation: mcp_error_types

**Target Audience**: developers, api_users

# mcp_error_types API Documentation

**File**: `mcp_error_types.py`
**Classes**: 4
**Functions**: 3

## Classes

- **MCPError** (inherits from Exception)
- **MCPClientInitializationError** (inherits from MCPError)
- **MCPClientNotFoundError** (inherits from MCPError)
- **MCPProviderError** (inherits from MCPError)

## Functions

- **__init__**
- **__init__**
- **__init__**


## Class: MCPError

**Description**: Base exception for MCP-related errors.

**Inherits from**: Exception



## Class: MCPClientInitializationError

**Description**: Raised when an MCP client fails to initialize.

**Inherits from**: MCPError

### Methods

#### __init__
**Parameters**: self, message, client_name, Provider



## Class: MCPClientNotFoundError

**Description**: Raised when a requested MCP client is not found in registry.

**Inherits from**: MCPError

### Methods

#### __init__
**Parameters**: self, message, client_name



## Class: MCPProviderError

**Description**: Raised when an MCP Provider encounters an error.

**Inherits from**: MCPError

### Methods

#### __init__
**Parameters**: self, message, Provider



## Function: __init__

**Parameters**: self, message, client_name, Provider


## Function: __init__

**Parameters**: self, message, client_name


## Function: __init__

**Parameters**: self, message, Provider


## Usage Examples

### Class Usage

```python
# Using MCPError
mcperror = MCPError()
```

```python
# Using MCPClientInitializationError
mcpclientinitializationerror = MCPClientInitializationError()
```

```python
# Using MCPClientNotFoundError
mcpclientnotfounderror = MCPClientNotFoundError()
```

### Function Usage

```python
# Using __init__
result = __init__(message, client_name)
```

```python
# Using __init__
result = __init__(message, client_name)
```

```python
# Using __init__
result = __init__(message, Provider)
```



---
**Generated**: 2026-03-26T09:39:03.981308
**Type**: api_reference
**Quality**: comprehensive
