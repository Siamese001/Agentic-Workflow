# API Documentation: mcp_tool_types

**Target Audience**: developers, api_users

# mcp_tool_types API Documentation

**File**: `mcp_tool_types.py`
**Classes**: 3
**Functions**: 17

## Classes

- **MCPTool**
- **MCPToolResult**
- **MCPToolServer**

## Functions

- **get_mcp_server** -> MCPToolServer
- **register_default_tools** -> None
- **create_mcp_server** -> MCPToolServer
- **execute_tool_with_capability** -> MCPToolResult
- **execute_tool_calls** -> list[MCPToolResult]
- **to_openai_format** -> dict[str, Any]
- **to_anthropic_format** -> dict[str, Any]
- **__init__**
- **set_capability_enforcer** -> None
- **register_tool** -> None
- **register_function** -> None
- **get_tool** -> MCPTool | None
- **list_tools** -> list[str]
- **get_tools_for_provider** -> list[dict[str, Any]]
- **execute_tool** -> MCPToolResult
- **calculator** -> float
- **analyze_text** -> dict[str, Any]


## Class: MCPTool

**Description**: MCP tool definition.

### Methods

#### to_openai_format
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to OpenAI function calling format.

        Returns:
            OpenAI-compatible tool definition
        

#### to_anthropic_format
**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to Anthropic tool format.

        Returns:
            Anthropic-compatible tool definition
        



## Class: MCPToolResult

**Description**: Result from MCP tool execution.



## Class: MCPToolServer

**Description**: MCP tool server for managing and executing tools.

### Methods

#### __init__
**Parameters**: self, name
**Description**: Initialize MCP tool server.

        Args:
            name: Server name
            allow_legacy_capability_enforcer: If True, permits the legacy
                set_capability_enforcer() path.  Default False (fail-closed).
        

#### set_capability_enforcer
**Parameters**: self, enforcer
**Returns**: None
**Description**: Set the CapabilityEnforcer for this server.

        §Wave5.0.1: Single L2 chokepoint capability enforcement.
        §Wave5.0.4: Disabled by default.  Requires
        allow_legacy_capability_enforcer=True at construction time.

        Args:
            enforcer: CapabilityEnforcer instance (or None to clear)

        Raises:
            ValueError: If legacy capability enforcer is disabled (default).
        

#### register_tool
**Parameters**: self, tool
**Returns**: None
**Description**: Register a tool.

        Args:
            tool: MCP tool to register
        

#### register_function
**Parameters**: self, name, description, parameters, handler, requires_approval
**Returns**: None
**Description**: Register a function as an MCP tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for parameters
            handler: Function to execute
            requires_approval: Whether tool requires approval
        

#### get_tool
**Parameters**: self, name
**Returns**: MCPTool | None
**Description**: Get a tool by name.

        Args:
            name: Tool name

        Returns:
            MCPTool or None if not found
        

#### list_tools
**Parameters**: self
**Returns**: list[str]
**Description**: List all registered tool names.

        Returns:
            List of tool names
        

#### get_tools_for_provider
**Parameters**: self, Provider
**Returns**: list[dict[str, Any]]
**Description**: Get tools in Provider-specific format.

        Args:
            Provider: Provider name (openai, anthropic)

        Returns:
            List of tool definitions
        

#### execute_tool
**Parameters**: self, name, arguments
**Returns**: MCPToolResult
**Description**: Execute a tool.

        §Wave2.4: All tool calls pass through the LawSlotHandler enforcement
        gate before execution. The gate resolves applicable law slots,
        records an enforcement artifact, and may PASS/BLOCK/MODIFY.

        §Wave5.0.2: Explicit capability_token parameter for per-call
        propagation. Precedence: explicit token > legacy enforcer > DENY.

        Args:
            name: Tool name
            arguments: Tool arguments
            capability_token: Explicit CapabilityTokenArtifact for this call

        Returns:
            MCPToolResult with execution result

        Raises:
            ToolPolicyBlocked: If enforcement blocks the tool call
            PermissionError: If capability enforcement denies the call
        



## Function: get_mcp_server

**Parameters**: name
**Returns**: MCPToolServer
**Description**: Get or create global MCP tool server.

    Args:
        name: Server name

    Returns:
        MCPToolServer instance
    



## Function: register_default_tools

**Parameters**: server
**Returns**: None
**Description**: Register default MCP tools.

    Args:
        server: MCP tool server
    



## Function: create_mcp_server

**Parameters**: name, register_defaults
**Returns**: MCPToolServer
**Description**: Factory function to create MCP tool server.

    Args:
        name: Server name
        register_defaults: Whether to register default tools

    Returns:
        MCPToolServer instance
    



## Function: execute_tool_with_capability

**Parameters**: server, name, arguments
**Returns**: MCPToolResult
**Description**: §Wave5.0.3 — Integration seam: issue token + execute tool in one call.

    Mints a CapabilityTokenArtifact via issue_capability_token and passes
    it to server.execute_tool using the explicit capability_token parameter.
    No enforcement logic here — enforcement remains solely in execute_tool.

    Args:
        server: MCPToolServer instance
        name: Tool name
        arguments: Tool arguments
        semantic_clock: SemanticClockSnapshot for token issuance
        subject_kind: Subject type (e.g. "agent")
        subject_id: Subject identifier
        issued_by: Issuer identity
        permissions: Permission code values (e.g. ["TOOL:READ"])
        allowed_paths: Allowed resource path prefixes
        max_tool_calls: Maximum invocations for this token
        policy_config_hash: Optional policy config hash

    Returns:
        MCPToolResult from execute_tool
    



## Function: execute_tool_calls

**Parameters**: server, tool_calls
**Returns**: list[MCPToolResult]
**Description**: Execute multiple tool calls.

    §Wave5.0.2: capability_token is propagated to each server.execute_tool call.

    Args:
        server: MCP tool server
        tool_calls: List of tool call definitions
        capability_token: Explicit CapabilityTokenArtifact for all calls

    Returns:
        List of MCPToolResult
    



## Function: to_openai_format

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to OpenAI function calling format.

        Returns:
            OpenAI-compatible tool definition
        



## Function: to_anthropic_format

**Parameters**: self
**Returns**: dict[str, Any]
**Description**: Convert to Anthropic tool format.

        Returns:
            Anthropic-compatible tool definition
        



## Function: __init__

**Parameters**: self, name
**Description**: Initialize MCP tool server.

        Args:
            name: Server name
            allow_legacy_capability_enforcer: If True, permits the legacy
                set_capability_enforcer() path.  Default False (fail-closed).
        



## Function: set_capability_enforcer

**Parameters**: self, enforcer
**Returns**: None
**Description**: Set the CapabilityEnforcer for this server.

        §Wave5.0.1: Single L2 chokepoint capability enforcement.
        §Wave5.0.4: Disabled by default.  Requires
        allow_legacy_capability_enforcer=True at construction time.

        Args:
            enforcer: CapabilityEnforcer instance (or None to clear)

        Raises:
            ValueError: If legacy capability enforcer is disabled (default).
        



## Function: register_tool

**Parameters**: self, tool
**Returns**: None
**Description**: Register a tool.

        Args:
            tool: MCP tool to register
        



## Function: register_function

**Parameters**: self, name, description, parameters, handler, requires_approval
**Returns**: None
**Description**: Register a function as an MCP tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for parameters
            handler: Function to execute
            requires_approval: Whether tool requires approval
        



## Function: get_tool

**Parameters**: self, name
**Returns**: MCPTool | None
**Description**: Get a tool by name.

        Args:
            name: Tool name

        Returns:
            MCPTool or None if not found
        



## Function: list_tools

**Parameters**: self
**Returns**: list[str]
**Description**: List all registered tool names.

        Returns:
            List of tool names
        



## Function: get_tools_for_provider

**Parameters**: self, Provider
**Returns**: list[dict[str, Any]]
**Description**: Get tools in Provider-specific format.

        Args:
            Provider: Provider name (openai, anthropic)

        Returns:
            List of tool definitions
        



## Function: execute_tool

**Parameters**: self, name, arguments
**Returns**: MCPToolResult
**Description**: Execute a tool.

        §Wave2.4: All tool calls pass through the LawSlotHandler enforcement
        gate before execution. The gate resolves applicable law slots,
        records an enforcement artifact, and may PASS/BLOCK/MODIFY.

        §Wave5.0.2: Explicit capability_token parameter for per-call
        propagation. Precedence: explicit token > legacy enforcer > DENY.

        Args:
            name: Tool name
            arguments: Tool arguments
            capability_token: Explicit CapabilityTokenArtifact for this call

        Returns:
            MCPToolResult with execution result

        Raises:
            ToolPolicyBlocked: If enforcement blocks the tool call
            PermissionError: If capability enforcement denies the call
        



## Function: calculator

**Parameters**: operation, a, b
**Returns**: float
**Description**: Perform basic arithmetic operations.



## Function: analyze_text

**Parameters**: text
**Returns**: dict[str, Any]
**Description**: Analyze text and return statistics.



## Usage Examples

### Class Usage

```python
# Using MCPTool
mcptool = MCPTool()
mcptool.to_openai_format()
mcptool.to_anthropic_format()
```

```python
# Using MCPToolResult
mcptoolresult = MCPToolResult()
```

```python
# Using MCPToolServer
mcptoolserver = MCPToolServer()
mcptoolserver.set_capability_enforcer()
mcptoolserver.register_tool()
```

### Function Usage

```python
# Using get_mcp_server
result = get_mcp_server(name)
```

```python
# Using register_default_tools
result = register_default_tools(server)
```

```python
# Using create_mcp_server
result = create_mcp_server(name, register_defaults)
```



---
**Generated**: 2026-03-26T09:39:03.988525
**Type**: api_reference
**Quality**: comprehensive
