"""Comprehensive test suite for MCP Tool Server Integration.

Tests cover:
- MCP tool registration and management
- Tool execution with various parameter types
- Provider format conversion (OpenAI, Anthropic)
- Error handling and validation
- Performance and security aspects
"""

import pytest
import asyncio
import json
import sys
import os
from typing import Any, Dict, List
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import mcp_tools directly to avoid problematic __init__.py imports
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_tools", os.path.join(os.path.dirname(__file__), '..', '..', '..', 'runtime', 'shared', 'mcp_tools.py'))
mcp_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_tools)

# Extract the classes we need
MCPTool = mcp_tools.MCPTool
MCPToolResult = mcp_tools.MCPToolResult
MCPToolServer = mcp_tools.MCPToolServer
get_mcp_server = mcp_tools.get_mcp_server
register_default_tools = mcp_tools.register_default_tools
create_mcp_server = mcp_tools.create_mcp_server
execute_tool_calls = mcp_tools.execute_tool_calls


class TestMCPTool:
    """Test MCPTool class functionality."""

    def test_mcp_tool_creation(self):
        """Test creating an MCP tool."""
        def dummy_handler(x: int) -> int:
            return x * 2

        tool = MCPTool(
            name="double",
            description="Doubles a number",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Number to double"}
                },
                "required": ["x"]
            },
            handler=dummy_handler,
            requires_approval=False
        )

        assert tool.name == "double"
        assert tool.description == "Doubles a number"
        assert tool.requires_approval is False
        assert callable(tool.handler)

    def test_to_openai_format(self):
        """Test conversion to OpenAI function format."""
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            parameters={"type": "object", "properties": {}},
            handler=lambda: None
        )

        openai_format = tool.to_openai_format()
        
        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "test_tool"
        assert openai_format["function"]["description"] == "Test tool"
        assert openai_format["function"]["parameters"] == {"type": "object", "properties": {}}

    def test_to_anthropic_format(self):
        """Test conversion to Anthropic tool format."""
        tool = MCPTool(
            name="test_tool",
            description="Test tool",
            parameters={"type": "object", "properties": {}},
            handler=lambda: None
        )

        anthropic_format = tool.to_anthropic_format()
        
        assert anthropic_format["name"] == "test_tool"
        assert anthropic_format["description"] == "Test tool"
        assert anthropic_format["input_schema"] == {"type": "object", "properties": {}}


class TestMCPToolResult:
    """Test MCPToolResult class functionality."""

    def test_successful_result(self):
        """Test creating a successful tool result."""
        result = MCPToolResult(
            tool_name="test_tool",
            success=True,
            result={"output": "success"},
            metadata={"execution_time": 0.1}
        )

        assert result.tool_name == "test_tool"
        assert result.success is True
        assert result.result == {"output": "success"}
        assert result.error is None
        assert result.metadata == {"execution_time": 0.1}

    def test_failed_result(self):
        """Test creating a failed tool result."""
        result = MCPToolResult(
            tool_name="test_tool",
            success=False,
            result=None,
            error="Tool execution failed"
        )

        assert result.tool_name == "test_tool"
        assert result.success is False
        assert result.result is None
        assert result.error == "Tool execution failed"
        assert result.metadata == {}


class TestMCPToolServer:
    """Test MCPToolServer class functionality."""

    def test_server_initialization(self):
        """Test server initialization."""
        server = MCPToolServer("test-server")
        assert server.name == "test-server"
        assert len(server._tools) == 0

    def test_register_tool(self):
        """Test tool registration."""
        server = MCPToolServer()
        tool = MCPTool(
            name="test",
            description="Test tool",
            parameters={},
            handler=lambda: None
        )

        server.register_tool(tool)
        
        assert "test" in server._tools
        assert server._tools["test"] == tool

    def test_register_function(self):
        """Test registering a function as a tool."""
        server = MCPToolServer()
        
        def add(a: int, b: int) -> int:
            return a + b

        server.register_function(
            name="add",
            description="Adds two numbers",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            },
            handler=add,
            requires_approval=True
        )

        tool = server.get_tool("add")
        assert tool is not None
        assert tool.name == "add"
        assert tool.requires_approval is True

    def test_get_tool(self):
        """Test retrieving a tool by name."""
        server = MCPToolServer()
        tool = MCPTool(
            name="test",
            description="Test tool",
            parameters={},
            handler=lambda: None
        )
        server.register_tool(tool)

        retrieved = server.get_tool("test")
        assert retrieved == tool

        not_found = server.get_tool("nonexistent")
        assert not_found is None

    def test_list_tools(self):
        """Test listing all registered tools."""
        server = MCPToolServer()
        
        for i in range(3):
            tool = MCPTool(
                name=f"tool_{i}",
                description=f"Tool {i}",
                parameters={},
                handler=lambda: None
            )
            server.register_tool(tool)

        tools = server.list_tools()
        assert set(tools) == {"tool_0", "tool_1", "tool_2"}

    def test_get_tools_for_provider_openai(self):
        """Test getting tools in OpenAI format."""
        server = MCPToolServer()
        
        server.register_function(
            name="test_tool",
            description="Test tool",
            parameters={"type": "object"},
            handler=lambda: None
        )

        tools = server.get_tools_for_provider("openai")
        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "test_tool"

    def test_get_tools_for_provider_anthropic(self):
        """Test getting tools in Anthropic format."""
        server = MCPToolServer()
        
        server.register_function(
            name="test_tool",
            description="Test tool",
            parameters={"type": "object"},
            handler=lambda: None
        )

        tools = server.get_tools_for_provider("anthropic")
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"
        assert "input_schema" in tools[0]

    def test_execute_tool_success(self):
        """Test successful tool execution."""
        server = MCPToolServer()
        
        def multiply(a: int, b: int) -> int:
            return a * b

        server.register_function(
            name="multiply",
            description="Multiplies two numbers",
            parameters={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            },
            handler=multiply
        )

        result = server.execute_tool("multiply", {"a": 3, "b": 4})
        
        assert result.success is True
        assert result.result == 12
        assert result.tool_name == "multiply"
        assert result.error is None

    def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        server = MCPToolServer()
        
        result = server.execute_tool("nonexistent", {})
        
        assert result.success is False
        assert result.result is None
        assert result.error == "Tool not found: nonexistent"
        assert result.tool_name == "nonexistent"

    def test_execute_tool_exception(self):
        """Test tool execution with exception."""
        server = MCPToolServer()
        
        def failing_tool():
            raise ValueError("Tool failed")

        server.register_function(
            name="failing_tool",
            description="Failing tool",
            parameters={},
            handler=failing_tool
        )

        result = server.execute_tool("failing_tool", {})
        
        assert result.success is False
        assert result.result is None
        assert "Tool failed" in result.error
        assert result.tool_name == "failing_tool"

    def test_execute_tool_with_invalid_parameters(self):
        """Test tool execution with invalid parameters."""
        server = MCPToolServer()
        
        def require_params(required_param: str) -> str:
            return required_param

        server.register_function(
            name="require_params",
            description="Requires parameters",
            parameters={
                "type": "object",
                "properties": {
                    "required_param": {"type": "string"}
                },
                "required": ["required_param"]
            },
            handler=require_params
        )

        # Missing required parameter should raise TypeError
        result = server.execute_tool("require_params", {})
        assert result.success is False
        assert result.error is not None


class TestDefaultTools:
    """Test default MCP tools."""

    def test_register_default_tools(self):
        """Test registration of default tools."""
        server = MCPToolServer()
        register_default_tools(server)
        
        tools = server.list_tools()
        assert "calculator" in tools
        assert "analyze_text" in tools

    def test_calculator_tool(self):
        """Test the calculator tool."""
        server = MCPToolServer()
        register_default_tools(server)
        
        # Test addition
        result = server.execute_tool("calculator", {"operation": "add", "a": 5, "b": 3})
        assert result.success is True
        assert result.result == 8
        
        # Test division by zero
        result = server.execute_tool("calculator", {"operation": "divide", "a": 5, "b": 0})
        assert result.success is True
        assert result.result == float('inf')
        
        # Test invalid operation
        result = server.execute_tool("calculator", {"operation": "invalid", "a": 5, "b": 3})
        assert result.success is False
        assert "Unknown operation" in result.error

    def test_analyze_text_tool(self):
        """Test the text analysis tool."""
        server = MCPToolServer()
        register_default_tools(server)
        
        text = "Hello world. This is a test."
        result = server.execute_tool("analyze_text", {"text": text})
        
        assert result.success is True
        stats = result.result
        assert stats["character_count"] == len(text)
        assert stats["word_count"] == 6
        assert stats["sentence_count"] == 2
        assert 0 < stats["average_word_length"] < 10


class TestMCPToolServerFactory:
    """Test MCP tool server factory functions."""

    def test_get_mcp_server_singleton(self):
        """Test that get_mcp_server returns singleton instance."""
        server1 = get_mcp_server()
        server2 = get_mcp_server()
        
        assert server1 is server2

    def test_create_mcp_server_with_defaults(self):
        """Test creating MCP server with default tools."""
        server = create_mcp_server(register_defaults=True)
        
        tools = server.list_tools()
        assert len(tools) >= 2  # At least calculator and analyze_text
        assert "calculator" in tools
        assert "analyze_text" in tools

    def test_create_mcp_server_without_defaults(self):
        """Test creating MCP server without default tools."""
        server = create_mcp_server(register_defaults=False)
        
        tools = server.list_tools()
        assert len(tools) == 0


class TestExecuteToolCalls:
    """Test batch tool execution."""

    def test_execute_multiple_tool_calls(self):
        """Test executing multiple tool calls."""
        server = MCPToolServer()
        register_default_tools(server)
        
        tool_calls = [
            {
                "function": {
                    "name": "calculator",
                    "arguments": json.dumps({"operation": "add", "a": 1, "b": 2})
                }
            },
            {
                "function": {
                    "name": "calculator",
                    "arguments": {"operation": "multiply", "a": 3, "b": 4}
                }
            }
        ]
        
        results = execute_tool_calls(server, tool_calls)
        
        assert len(results) == 2
        assert results[0].success is True
        assert results[0].result == 3
        assert results[1].success is True
        assert results[1].result == 12

    def test_execute_tool_calls_with_invalid_json(self):
        """Test tool calls with invalid JSON arguments."""
        server = MCPToolServer()
        register_default_tools(server)
        
        tool_calls = [
            {
                "function": {
                    "name": "calculator",
                    "arguments": "invalid json"
                }
            }
        ]
        
        results = execute_tool_calls(server, tool_calls)
        
        assert len(results) == 1
        # Should handle invalid JSON gracefully
        assert results[0].success is False or results[0].result is not None


class TestMCPToolServerAsync:
    """Test async aspects of MCP tool server."""

    @pytest.mark.asyncio
    async def test_async_tool_execution(self):
        """Test executing async tools."""
        server = MCPToolServer()
        
        async def async_tool(delay: float) -> str:
            await asyncio.sleep(delay)
            return "async result"

        server.register_function(
            name="async_tool",
            description="Async test tool",
            parameters={
                "type": "object",
                "properties": {
                    "delay": {"type": "number"}
                },
                "required": ["delay"]
            },
            handler=async_tool
        )

        # Execute async tool
        result = server.execute_tool("async_tool", {"delay": 0.1})
        
        # The result should be a coroutine
        assert asyncio.iscoroutine(result.result)
        
        # Await the coroutine
        final_result = await result.result
        assert final_result == "async result"


class TestMCPToolServerSecurity:
    """Test security aspects of MCP tool server."""

    def test_tool_approval_flag(self):
        """Test tool approval requirement flag."""
        server = MCPToolServer()
        
        def safe_tool():
            return "safe"

        def sensitive_tool():
            return "sensitive data"

        server.register_function(
            name="safe_tool",
            description="Safe tool",
            parameters={},
            handler=safe_tool,
            requires_approval=False
        )

        server.register_function(
            name="sensitive_tool",
            description="Sensitive tool",
            parameters={},
            handler=sensitive_tool,
            requires_approval=True
        )

        safe = server.get_tool("safe_tool")
        sensitive = server.get_tool("sensitive_tool")
        
        assert safe.requires_approval is False
        assert sensitive.requires_approval is True

    def test_tool_parameter_validation(self):
        """Test tool parameter validation."""
        server = MCPToolServer()
        
        def validate_input(data: str) -> str:
            if "malicious" in data.lower():
                raise ValueError("Malicious input detected")
            return data

        server.register_function(
            name="validate_input",
            description="Validates input",
            parameters={
                "type": "object",
                "properties": {
                    "data": {"type": "string"}
                },
                "required": ["data"]
            },
            handler=validate_input
        )

        # Valid input
        result = server.execute_tool("validate_input", {"data": "safe input"})
        assert result.success is True
        
        # Malicious input
        result = server.execute_tool("validate_input", {"data": "malicious code"})
        assert result.success is False
        assert "Malicious input detected" in result.error


class TestMCPToolServerPerformance:
    """Test performance aspects of MCP tool server."""

    def test_tool_execution_time(self):
        """Test tool execution time tracking."""
        server = MCPToolServer()
        
        def fast_tool():
            return "fast"

        def slow_tool():
            import time
            time.sleep(0.1)
            return "slow"

        server.register_function("fast_tool", "Fast tool", {}, fast_tool)
        server.register_function("slow_tool", "Slow tool", {}, slow_tool)

        import time
        start = time.time()
        server.execute_tool("fast_tool", {})
        fast_time = time.time() - start

        start = time.time()
        server.execute_tool("slow_tool", {})
        slow_time = time.time() - start

        assert slow_time > fast_time
        assert slow_time >= 0.1  # Should take at least 0.1 seconds

    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution."""
        server = MCPToolServer()
        
        def identity(x):
            return x

        server.register_function(
            "identity",
            "Identity function",
            {"type": "object", "properties": {"x": {}}},
            identity
        )

        import threading
        results = []
        errors = []

        def execute_tool(i):
            try:
                result = server.execute_tool("identity", {"x": i})
                results.append(result.result)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(10):
            thread = threading.Thread(target=execute_tool, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert len(results) == 10
        assert set(results) == set(range(10))
