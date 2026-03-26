# API Documentation: sovereign_redis_orchestrator

**Target Audience**: developers, api_users

# sovereign_redis_orchestrator API Documentation

**File**: `sovereign_redis_orchestrator.py`
**Classes**: 1
**Functions**: 13

## Classes

- **SovereignRedisOrchestrator** (inherits from SovereignBaseAgent)

## Functions

- **get_sovereign_redis_orchestrator** -> SovereignRedisOrchestrator
- **__init__** -> None
- **_get_mcp** -> Any
- **_mcp_call** -> Any
- **_create_connection** -> redis.Redis
- **get** -> Any
- **set** -> Any
- **delete** -> bool
- **exists** -> bool
- **clear** -> Any
- **get_connection_info** -> dict
- **heal_repository** -> Dict[str, int]
- **heal** -> dict[str, Any]


## Class: SovereignRedisOrchestrator

**Description**: Brief description of functionality and purpose.

**Inherits from**: SovereignBaseAgent

### Methods

#### __init__
**Parameters**: self
**Returns**: None
**Description**: Initialize the instance.

#### _get_mcp
**Parameters**: self
**Returns**: Any
**Description**: Lazy-init MCPConnectionManager when REDIS_MCP_ENABLED.

#### _mcp_call
**Parameters**: self, tool, args
**Returns**: Any
**Description**: Synchronous wrapper around async MCP call_tool.

#### _create_connection
**Parameters**: self
**Returns**: redis.Redis
**Description**: Version-agnostic connection factory

#### get
**Parameters**: self, key
**Returns**: Any
**Description**: Execute get operation (MCP-routed when REDIS_MCP_ENABLED).

#### set
**Parameters**: self, key, value
**Returns**: Any
**Description**: Execute set operation (MCP-routed when REDIS_MCP_ENABLED).

#### delete
**Parameters**: self, key
**Returns**: bool
**Description**: Delete a key from Redis (MCP-routed when REDIS_MCP_ENABLED).

#### exists
**Parameters**: self, key
**Returns**: bool
**Description**: Check if key exists in Redis.

#### clear
**Parameters**: self
**Returns**: Any
**Description**: Clear all data from Redis.

#### get_connection_info
**Parameters**: self
**Returns**: dict
**Description**: Get information about the current connection state.

#### heal_repository
**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: Dict[str, int]
**Description**: L2 execution agent - operational only.

#### heal
**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SovereignRedisOrchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Function: get_sovereign_redis_orchestrator

**Returns**: SovereignRedisOrchestrator
**Description**: Factory function to get sovereign redis orchestrator instance.



## Function: __init__

**Parameters**: self
**Returns**: None
**Description**: Initialize the instance.



## Function: _get_mcp

**Parameters**: self
**Returns**: Any
**Description**: Lazy-init MCPConnectionManager when REDIS_MCP_ENABLED.



## Function: _mcp_call

**Parameters**: self, tool, args
**Returns**: Any
**Description**: Synchronous wrapper around async MCP call_tool.



## Function: _create_connection

**Parameters**: self
**Returns**: redis.Redis
**Description**: Version-agnostic connection factory



## Function: get

**Parameters**: self, key
**Returns**: Any
**Description**: Execute get operation (MCP-routed when REDIS_MCP_ENABLED).



## Function: set

**Parameters**: self, key, value
**Returns**: Any
**Description**: Execute set operation (MCP-routed when REDIS_MCP_ENABLED).



## Function: delete

**Parameters**: self, key
**Returns**: bool
**Description**: Delete a key from Redis (MCP-routed when REDIS_MCP_ENABLED).



## Function: exists

**Parameters**: self, key
**Returns**: bool
**Description**: Check if key exists in Redis.



## Function: clear

**Parameters**: self
**Returns**: Any
**Description**: Clear all data from Redis.



## Function: get_connection_info

**Parameters**: self
**Returns**: dict
**Description**: Get information about the current connection state.



## Function: heal_repository

**Parameters**: self, dry_run, execute, depth, max_depth, _call_path
**Returns**: Dict[str, int]
**Description**: L2 execution agent - operational only.



## Function: heal

**Parameters**: self, violation
**Returns**: dict[str, Any]
**Description**: 
        Heal violations detected by SovereignRedisOrchestrator.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        



## Usage Examples

### Class Usage

```python
# Using SovereignRedisOrchestrator
sovereignredisorchestrator = SovereignRedisOrchestrator()
sovereignredisorchestrator.get()
sovereignredisorchestrator.set()
```

### Function Usage

```python
# Using get_sovereign_redis_orchestrator
result = get_sovereign_redis_orchestrator()
```

```python
# Using __init__
result = __init__()
```

```python
# Using _get_mcp
result = _get_mcp()
```



---
**Generated**: 2026-03-26T09:39:04.232296
**Type**: api_reference
**Quality**: comprehensive
