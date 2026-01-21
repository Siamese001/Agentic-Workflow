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
        Logger.info(f"MCP tool server initialized: {name}")

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

    def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> MCPToolResult:
        """Execute a tool.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            MCPToolResult with execution result
        """
        tool = self.get_tool(name)

        if not tool:
            return MCPToolResult(
                tool_name=name,
                success=False,
                result=None,
                error=f"Tool not found: {name}",
            )

        try:
            result = tool.handler(**arguments)

            return MCPToolResult(
                tool_name=name,
                success=True,
                result=result,
            )

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
            "divide": lambda x, y: x / y if y != 0 else float('inf'),
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
        sentences = text.split('.')

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


def execute_tool_calls(
    server: MCPToolServer,
    tool_calls: list[dict[str, Any]],
) -> list[MCPToolResult]:
    """Execute multiple tool calls.

    Args:
        server: MCP tool server
        tool_calls: List of tool call definitions

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

            result = server.execute_tool(name, arguments)
            results.append(result)

    return results
