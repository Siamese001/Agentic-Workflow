# API Documentation: SovereignMCPGatewayAgent

**Target Audience**: developers, api_users

# SovereignMCPGatewayAgent API Documentation

**File**: `SovereignMCPGatewayAgent.py`
**Classes**: 1
**Functions**: 4

## Classes

- **SovereignMCPGateway** (inherits from SovereignBaseAgent)

## Functions

- **get_mcp_gateway** -> SovereignMCPGateway
- **__new__**
- **_audit** -> None
- **heal**


## Class: SovereignMCPGateway

**Description**: 
    Unified MCP Gateway - Single point of truth for all MCP operations.

    [PHASE 3 MIGRATION] Absorbed from:
    - llm_router_mcp_client.py
    - knowledge_graph_sovereign_graph_client.py
    - archive_client.py
    - caching_redis_mcp_client.py (redirects to RedisSovereignAgent)
    

**Inherits from**: SovereignBaseAgent

### Methods

#### __new__
**Parameters**: cls
**Description**: Singleton constructor.

#### _audit
**Parameters**: self, operation, success, latency_ms
**Returns**: None
**Description**: [PHASE 3] Record MCP operation to audit plane.

#### heal
**Parameters**: self, violation



## Function: get_mcp_gateway

**Returns**: SovereignMCPGateway
**Description**: Get or create the global MCP gateway.



## Function: __new__

**Parameters**: cls
**Description**: Singleton constructor.



## Function: _audit

**Parameters**: self, operation, success, latency_ms
**Returns**: None
**Description**: [PHASE 3] Record MCP operation to audit plane.



## Function: heal

**Parameters**: self, violation


## Usage Examples

### Class Usage

```python
# Using SovereignMCPGateway
sovereignmcpgateway = SovereignMCPGateway()
sovereignmcpgateway.heal()
```

### Function Usage

```python
# Using get_mcp_gateway
result = get_mcp_gateway()
```

```python
# Using __new__
result = __new__(cls)
```

```python
# Using _audit
result = _audit(operation, success)
```



---
**Generated**: 2026-03-26T09:39:03.872892
**Type**: api_reference
**Quality**: comprehensive
