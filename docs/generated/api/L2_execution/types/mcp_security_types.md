# API Documentation: mcp_security_types

**Target Audience**: developers, api_users

# mcp_security_types API Documentation

**File**: `mcp_security_types.py`
**Classes**: 3
**Functions**: 7

## Classes

- **MCPSecurityViolation**
- **MCPSecurityResult**
- **MCPSecurityGuardrail**

## Functions

- **__init__**
- **_is_tool_allowed** -> bool
- **_check_arguments** -> list[MCPSecurityViolation]
- **_sanitize_arguments** -> dict[str, Any]
- **add_to_whitelist** -> None
- **remove_from_whitelist** -> None
- **get_statistics** -> dict[str, Any]


## Class: MCPSecurityViolation

**Description**: MCP security violation.



## Class: MCPSecurityResult

**Description**: Result of MCP security check.



## Class: MCPSecurityGuardrail

**Description**: 
    Consolidated MCP Security Guardrail.

    Provides unified MCP protection with:
    - Tool whitelist validation
    - Argument sanitization
    - Response validation
    - Audit logging
    

### Methods

#### __init__
**Parameters**: self
**Description**: Initialize MCP security guardrail.

#### _is_tool_allowed
**Parameters**: self, tool_name
**Returns**: bool
**Description**: Check if tool is in whitelist.

#### _check_arguments
**Parameters**: self, tool_name, args
**Returns**: list[MCPSecurityViolation]
**Description**: Check arguments for dangerous patterns.

#### _sanitize_arguments
**Parameters**: self, args
**Returns**: dict[str, Any]
**Description**: Sanitize arguments by removing dangerous patterns.

#### add_to_whitelist
**Parameters**: self, tool_name
**Returns**: None
**Description**: Add tool to whitelist.

#### remove_from_whitelist
**Parameters**: self, tool_name
**Returns**: None
**Description**: Remove tool from whitelist.

#### get_statistics
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get MCP security statistics.



## Function: __init__

**Parameters**: self
**Description**: Initialize MCP security guardrail.



## Function: _is_tool_allowed

**Parameters**: self, tool_name
**Returns**: bool
**Description**: Check if tool is in whitelist.



## Function: _check_arguments

**Parameters**: self, tool_name, args
**Returns**: list[MCPSecurityViolation]
**Description**: Check arguments for dangerous patterns.



## Function: _sanitize_arguments

**Parameters**: self, args
**Returns**: dict[str, Any]
**Description**: Sanitize arguments by removing dangerous patterns.



## Function: add_to_whitelist

**Parameters**: self, tool_name
**Returns**: None
**Description**: Add tool to whitelist.



## Function: remove_from_whitelist

**Parameters**: self, tool_name
**Returns**: None
**Description**: Remove tool from whitelist.



## Function: get_statistics

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Get MCP security statistics.



## Usage Examples

### Class Usage

```python
# Using MCPSecurityViolation
mcpsecurityviolation = MCPSecurityViolation()
```

```python
# Using MCPSecurityResult
mcpsecurityresult = MCPSecurityResult()
```

```python
# Using MCPSecurityGuardrail
mcpsecurityguardrail = MCPSecurityGuardrail()
mcpsecurityguardrail.add_to_whitelist()
mcpsecurityguardrail.remove_from_whitelist()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using _is_tool_allowed
result = _is_tool_allowed(tool_name)
```

```python
# Using _check_arguments
result = _check_arguments(tool_name, args)
```



---
**Generated**: 2026-03-26T09:39:03.984867
**Type**: api_reference
**Quality**: comprehensive
