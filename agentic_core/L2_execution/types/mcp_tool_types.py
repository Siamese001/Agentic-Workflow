from __future__ import annotations

"""MCP Tool Server Integration.

Provides MCP (Model Context Protocol) tool server integration
for external tool access and context providers.

Phase 1C - SDK Integration Layer
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L0_maintenance.enforcement.v15_runtime_guard import (
    v15_runtime_guard,
)

Logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """MCP tool definition."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable
    requires_approval: bool = False

    def to_openai_format(self) -> dict[str, Any]:
        """Convert to OpenAI function calling format.

        Returns:
            OpenAI-compatible tool definition
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        """Convert to Anthropic tool format.

        Returns:
            Anthropic-compatible tool definition
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


@dataclass
class MCPToolResult:
    """Result from MCP tool execution."""

    tool_name: str
    success: bool
    result: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class MCPToolServer:
    """MCP tool server for managing and executing tools."""

    def __init__(self, name: str = "agentic-workflow-tools"):
        """Initialize MCP tool server.

        Args:
            name: Server name
        """
        self.name = name
        self._tools: dict[str, MCPTool] = {}
        self._capability_enforcer: Any | None = None
        Logger.info(f"MCP tool server initialized: {name}")

    def set_capability_enforcer(self, enforcer: Any) -> None:
        """Set the CapabilityEnforcer for this server.

        §Wave5.0.1: Single L2 chokepoint capability enforcement.
        When set, every execute_tool call validates against the token.

        Args:
            enforcer: CapabilityEnforcer instance (or None to clear)
        """
        self._capability_enforcer = enforcer

    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool.

        Args:
            tool: MCP tool to register
        """
        self._tools[tool.name] = tool
        Logger.info(f"Registered MCP tool: {tool.name}")

    def register_function(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable,
        requires_approval: bool = False,
    ) -> None:
        """Register a function as an MCP tool.

        Args:
            name: Tool name
            description: Tool description
            parameters: JSON schema for parameters
            handler: Function to execute
            requires_approval: Whether tool requires approval
        """
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
            requires_approval=requires_approval,
        )
        self.register_tool(tool)

    def get_tool(self, name: str) -> MCPTool | None:
        """Get a tool by name.

        Args:
            name: Tool name

        Returns:
            MCPTool or None if not found
        """
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_tools_for_provider(
        self,
        Provider: str = "openai",
    ) -> list[dict[str, Any]]:
        """Get tools in Provider-specific format.

        Args:
            Provider: Provider name (openai, anthropic)

        Returns:
            List of tool definitions
        """
        tools = []

        for tool in self._tools.values():
            if Provider == "anthropic":
                tools.append(tool.to_anthropic_format())
            else:
                tools.append(tool.to_openai_format())

        return tools

    @v15_runtime_guard("B.execute_tool.mcp_tool_types")
    def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        capability_token: Any | None = None,
    ) -> MCPToolResult:
        """Execute a tool.

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
        """
        tool = self.get_tool(name)

        if not tool:
            return MCPToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=f"Tool not found: {name}",
            )

        # §Wave5.0.2 — Capability token enforcement gate (before LawSlotHandler)
        # Precedence: explicit token > legacy enforcer > DENY
        from agentic_core.L2_execution.types.capability_token_types import (
            PERMISSION_CODES,
            CapabilityEnforcer,
            build_capability_decision,
        )

        required_perm = PERMISSION_CODES["TOOL_READ"]
        resource_path = f"tool/{name}"

        if capability_token is not None:
            # §Wave5.0.2 path: per-call enforcer from explicit token
            enforcer_local = CapabilityEnforcer(capability_token)
            enforcer_local.check(
                tool_name=name,
                action="execute",
                requested_resource=resource_path,
                required_permission=required_perm,
                semantic_clock=capability_token.semantic_clock,
            )
        elif self._capability_enforcer is not None:
            # §Wave5.0.1 legacy path: server-level enforcer
            enforcer_legacy: CapabilityEnforcer = self._capability_enforcer
            enforcer_legacy.check(
                tool_name=name,
                action="execute",
                requested_resource=resource_path,
                required_permission=required_perm,
                semantic_clock=enforcer_legacy.token.semantic_clock,
            )
        else:
            # §Wave5.0.2 fail-closed: no token provided → deterministic DENY
            from agentic_core.L0_maintenance.types.v15_p2_types import (
                SemanticClockSnapshot,
            )

            deny_clock = SemanticClockSnapshot(tick=0, vector_clock={})
            build_capability_decision(
                semantic_clock=deny_clock,
                tool_name=name,
                action="execute",
                requested_resource=resource_path,
                decision="DENY",
                deny_reason="NO_TOKEN_PROVIDED",
                capability_trace_id="NONE",
            )
            raise PermissionError("CAPABILITY_DENIED:NO_TOKEN_PROVIDED")

        # §Wave2.4 — LawSlotHandler enforcement gate
        from agentic_core.L2_execution.enforcement.tool_policy_enforcer import (
            _stable_args_hash,
            get_tool_policy_enforcer,
        )
        from agentic_core.L2_execution.types.tool_enforcement_types import (
            LawSlotOutcome,
            ToolPolicyBlocked,
        )

        enforcer = get_tool_policy_enforcer()
        original_hash = _stable_args_hash(arguments)
        outcome, new_args, rationale, applied_slots = enforcer.enforce(
            name,
            arguments,
        )

        modified_hash = _stable_args_hash(new_args) if outcome == LawSlotOutcome.MODIFY else ""

        artifact = enforcer.build_artifact(
            tool_name=name,
            outcome=outcome,
            applied_slots=applied_slots,
            rationale=rationale,
            original_args_hash=original_hash,
            modified_args_hash=modified_hash,
        )

        # Emit enforcement artifact via TelemetryEmitter
        try:
            from agentic_core.L0_maintenance.types.v15_contracts import TelemetryEmitter

            emitter = TelemetryEmitter()
            emitter.emit_typed_artifact("TOOL_ENFORCEMENT", artifact)
        # guardian: allow-silent-swallow
        except Exception as _emit_exc:
            Logger.error(
                "§Wave2.4 ToolEnforcementArtifact emission failed: %s",
                _emit_exc,
            )

        if outcome == LawSlotOutcome.BLOCK:
            raise ToolPolicyBlocked(name, rationale, artifact)

        # Use potentially modified args
        effective_args = new_args if outcome == LawSlotOutcome.MODIFY else arguments

        try:
            result = tool.handler(**effective_args)

            return MCPToolResult(
                tool_name=name,
                success=True,
                result=result,
            )

        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Tool execution failed for {name}: {e}")

            return MCPToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=str(e),
            )


# Global MCP tool server instance
_MCP_SERVER: MCPToolServer | None = None


def get_mcp_server(name: str = "agentic-workflow-tools") -> MCPToolServer:
    """Get or create global MCP tool server.

    Args:
        name: Server name

    Returns:
        MCPToolServer instance
    """
    global _MCP_SERVER

    if _MCP_SERVER is None:
        _MCP_SERVER = MCPToolServer(name)

    return _MCP_SERVER


def register_default_tools(server: MCPToolServer) -> None:
    """Register default MCP tools.

    Args:
        server: MCP tool server
    """

    # Calculator tool
    def calculator(operation: str, a: float, b: float) -> float:
        """Perform basic arithmetic operations."""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else float("inf"),
        }

        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")

        return operations[operation](a, b)

    server.register_function(
        name="calculator",
        description="Perform basic arithmetic operations (add, subtract, multiply, divide)",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The arithmetic operation to perform",
                },
                "a": {
                    "type": "number",
                    "description": "First operand",
                },
                "b": {
                    "type": "number",
                    "description": "Second operand",
                },
            },
            "required": ["operation", "a", "b"],
        },
        handler=calculator,
    )

    # Text analysis tool
    def analyze_text(text: str) -> dict[str, Any]:
        """Analyze text and return statistics."""
        words = text.split()
        sentences = text.split(".")

        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        }

    server.register_function(
        name="analyze_text",
        description="Analyze text and return statistics (character count, word count, etc.)",
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze",
                },
            },
            "required": ["text"],
        },
        handler=analyze_text,
    )

    Logger.info("Registered default MCP tools")


def create_mcp_server(
    name: str = "agentic-workflow-tools",
    register_defaults: bool = True,
) -> MCPToolServer:
    """Factory function to create MCP tool server.

    Args:
        name: Server name
        register_defaults: Whether to register default tools

    Returns:
        MCPToolServer instance
    """
    server = MCPToolServer(name)

    if register_defaults:
        register_default_tools(server)

    return server


def execute_tool_with_capability(
    server: MCPToolServer,
    name: str,
    arguments: dict[str, Any],
    *,
    semantic_clock: Any,
    subject_kind: str,
    subject_id: str,
    issued_by: str,
    permissions: list[str],
    allowed_paths: list[str],
    max_tool_calls: int,
    policy_config_hash: str | None = None,
) -> MCPToolResult:
    """§Wave5.0.3 — Integration seam: issue token + execute tool in one call.

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
    """
    from agentic_core.L2_execution.types.capability_token_types import (
        issue_capability_token,
    )

    token = issue_capability_token(
        semantic_clock=semantic_clock,
        subject_kind=subject_kind,
        subject_id=subject_id,
        issued_by=issued_by,
        permissions=permissions,
        allowed_paths=allowed_paths,
        max_tool_calls=max_tool_calls,
        policy_config_hash=policy_config_hash,
    )

    return server.execute_tool(name, arguments, capability_token=token)


def execute_tool_calls(
    server: MCPToolServer,
    tool_calls: list[dict[str, Any]],
    *,
    capability_token: Any | None = None,
) -> list[MCPToolResult]:
    """Execute multiple tool calls.

    §Wave5.0.2: capability_token is propagated to each server.execute_tool call.

    Args:
        server: MCP tool server
        tool_calls: List of tool call definitions
        capability_token: Explicit CapabilityTokenArtifact for all calls

    Returns:
        List of MCPToolResult
    """
    results = []

    for tool_call in tool_calls:
        if "function" in tool_call:
            function = tool_call["function"]
            name = function.get("name")
            arguments = function.get("arguments", {})

            if isinstance(arguments, str):
                import json

                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            result = server.execute_tool(
                name,
                arguments,
                capability_token=capability_token,
            )
            results.append(result)

    return results
