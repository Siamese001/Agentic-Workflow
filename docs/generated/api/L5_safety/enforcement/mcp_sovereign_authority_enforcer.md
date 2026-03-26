# API Documentation: mcp_sovereign_authority_enforcer

**Target Audience**: developers, api_users

# mcp_sovereign_authority_enforcer API Documentation

**File**: `mcp_sovereign_authority_enforcer.py`
**Classes**: 1
**Functions**: 4

## Classes

- **MCPSovereignAuthority**

## Functions

- **__init__**
- **is_authorized** -> bool
- **record_breach** -> Any
- **authorize_tool_call** -> None


## Class: MCPSovereignAuthority

**Description**: Monitors the health and authorization of the MCP nervous system.

### Methods

#### __init__
**Parameters**: self

#### is_authorized
**Parameters**: self
**Returns**: bool
**Description**: Sovereignty check: Kill connections if breaches exceed threshold.

#### record_breach
**Parameters**: self, error_msg
**Returns**: Any
**Description**: Log a tool failure or unauthorized access attempt.

#### authorize_tool_call
**Parameters**: self, tool_name, args
**Returns**: None
**Description**: L5 Audit: Log every physical tool call before execution.

        P1/L5: emits applies_guardrail, validated_by_safety_plane,
        references_policy_hash ADG edges on every tool call.
        



## Function: __init__

**Parameters**: self


## Function: is_authorized

**Parameters**: self
**Returns**: bool
**Description**: Sovereignty check: Kill connections if breaches exceed threshold.



## Function: record_breach

**Parameters**: self, error_msg
**Returns**: Any
**Description**: Log a tool failure or unauthorized access attempt.



## Function: authorize_tool_call

**Parameters**: self, tool_name, args
**Returns**: None
**Description**: L5 Audit: Log every physical tool call before execution.

        P1/L5: emits applies_guardrail, validated_by_safety_plane,
        references_policy_hash ADG edges on every tool call.
        



## Usage Examples

### Class Usage

```python
# Using MCPSovereignAuthority
mcpsovereignauthority = MCPSovereignAuthority()
mcpsovereignauthority.is_authorized()
mcpsovereignauthority.record_breach()
```

### Function Usage

```python
# Using __init__
result = __init__()
```

```python
# Using is_authorized
result = is_authorized()
```

```python
# Using record_breach
result = record_breach(error_msg)
```



---
**Generated**: 2026-03-26T09:39:04.869310
**Type**: api_reference
**Quality**: comprehensive
