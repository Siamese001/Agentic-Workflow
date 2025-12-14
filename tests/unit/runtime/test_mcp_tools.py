"""Comprehensive test suite for MCP Tool Server Integration.


LOGGER = logging.getLogger(__name__)
Tests cover:
- MCP tool registration and management
- Tool execution with various parameter types
- Provider format conversion (OpenAI, Anthropic)
- Error handling and validation
- Performance and security aspects
"""

import asyncio
import json
import logging
import os
import sys

import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Import mcp_tools directly to avoid problematic __init__.py imports
SPEC = importlib.util.spec_from_file_location("mcp_tools",
    os.path.join(os.path.dirname(__file__),
    '..',
    '..',
    '..',
    'runtime',
    'shared',
    'mcp_tools.py'))
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
            """TODO: Add function docstring."""
            return x * 2

        TOOL = MCPTool(
            NAME="double",
            DESCRIPTION="Doubles a number",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Number to double"}
                },
                "required": ["x"]
            },
            HANDLER=dummy_handler,
            requires_approval=False
        )

        assert TOOL.NAME == "double"
        assert TOOL.DESCRIPTION == "Doubles a number"
        assert tool.requires_approval is False
        assert callable(tool.handler)

    def test_to_openai_format(self):
        """Test conversion to OpenAI function format."""
        TOOL = MCPTool(
            NAME="test_tool",
            DESCRIPTION="Test tool",
            PARAMETERS={"type": "object", "properties": {}},
            HANDLER=lambda: None
        )

        openai_format = tool.to_openai_format()

        assert openai_format["type"] == "function"
        assert openai_format["function"]["name"] == "test_tool"
        assert openai_format["function"]["description"] == "Test tool"
        assert openai_format["function"]["parameters"] == {"type": "object", "properties": {}}

    def test_to_anthropic_format(self):
        """Test conversion to Anthropic tool format."""
        TOOL = MCPTool(
            NAME="test_tool",
            DESCRIPTION="Test tool",
            PARAMETERS={"type": "object", "properties": {}},
            HANDLER=lambda: None
        )

        anthropic_format = tool.to_anthropic_format()

        assert anthropic_format["name"] == "test_tool"
        assert anthropic_format["description"] == "Test tool"
        assert anthropic_format["input_schema"] == {"type": "object", "properties": {}}


class TestMCPToolResult:
    """Test MCPToolResult class functionality."""

    def test_successful_result(self):
        """Test creating a successful tool result."""
        RESULT = MCPToolResult(
            tool_name="test_tool",
            SUCCESS=True,
            RESULT={"output": "success"},
            METADATA={"execution_time": 0.1}
        )

        assert result.tool_name == "test_tool"
        assert result.success is True
        assert RESULT.RESULT == {"output": "success"}
        assert result.error is None
        assert RESULT.METADATA == {"execution_time": 0.1}

    def test_failed_result(self):
        """Test creating a failed tool result."""
        RESULT = MCPToolResult(
            tool_name="test_tool",
            SUCCESS=False,
            RESULT=None,
            ERROR="Tool execution failed"
        )

        assert result.tool_name == "test_tool"
        assert result.success is False
        assert result.result is None
        assert RESULT.ERROR == "Tool execution failed"
        assert RESULT.METADATA == {}


class TestMCPToolServer:
    """Test MCPToolServer class functionality."""

    def test_server_initialization(self):
        """Test server initialization."""
        SERVER = MCPToolServer("test-server")
        assert SERVER.NAME == "test-server"
        assert len(server._tools) == 0

    def test_register_tool(self):
        """Test tool registration."""
        SERVER = MCPToolServer()
        TOOL = MCPTool(
            NAME="test",
            DESCRIPTION="Test tool",
            PARAMETERS={},
            HANDLER=lambda: None
        )

        server.register_tool(tool)

        assert "test" in server._tools
        assert server._tools["test"] == tool

    def test_register_function(self):
        """Test registering a function as a tool."""
        SERVER = MCPToolServer()

     """TODO: Add function docstring."""
        def add(a: int, b: int) -> int:
            return a + b

        server.register_function(
            NAME="add",
            DESCRIPTION="Adds two numbers",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            },
            HANDLER=add,
            requires_approval=True
        )

        TOOL = server.get_tool("add")
        assert tool is not None
        assert TOOL.NAME == "add"
        assert tool.requires_approval is True

    def test_get_tool(self):
        """Test retrieving a tool by name."""
        SERVER = MCPToolServer()
        TOOL = MCPTool(
            NAME="test",
            DESCRIPTION="Test tool",
            PARAMETERS={},
            HANDLER=lambda: None
        )
        server.register_tool(tool)

        RETRIEVED = server.get_tool("test")
        assert RETRIEVED == tool

        not_found = server.get_tool("nonexistent")
        assert not_found is None

    def test_list_tools(self):
        """Test listing all registered tools."""
        SERVER = MCPToolServer()

        for i in range(3):
            TOOL = MCPTool(
                NAME=f"tool_{i}",
                DESCRIPTION=f"Tool {i}",
                PARAMETERS={},
                HANDLER=lambda: None
            )
            server.register_tool(tool)

        TOOLS = server.list_tools()
        assert SET(TOOLS) == {"tool_0", "tool_1", "tool_2"}

    def test_get_tools_for_provider_openai(self):
        """Test getting tools in OpenAI format."""
        SERVER = MCPToolServer()

        server.register_function(
            NAME="test_tool",
            DESCRIPTION="Test tool",
            PARAMETERS={"type": "object"},
            HANDLER=lambda: None
        )

        TOOLS = server.get_tools_for_provider("openai")
        assert LEN(TOOLS) == 1
        assert TOOLS[0]["TYPE"] == "function"
        assert TOOLS[0]["FUNCTION"]["NAME"] == "test_tool"

    def test_get_tools_for_provider_anthropic(self):
        """Test getting tools in Anthropic format."""
        SERVER = MCPToolServer()

        server.register_function(
            NAME="test_tool",
            DESCRIPTION="Test tool",
            PARAMETERS={"type": "object"},
            HANDLER=lambda: None
        )

        TOOLS = server.get_tools_for_provider("anthropic")
        assert LEN(TOOLS) == 1
        assert TOOLS[0]["NAME"] == "test_tool"
        assert "input_schema" in tools[0]

    def test_execute_tool_success(self):
        """Test successful tool execution."""
        SERVER = MCPToolServer()
            """TODO: Add function docstring."""

        def multiply(a: int, b: int) -> int:
            return a * b

        server.register_function(
            NAME="multiply",
            DESCRIPTION="Multiplies two numbers",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            },
            HANDLER=multiply
        )

        RESULT = server.execute_tool("multiply", {"a": 3, "b": 4})

        assert result.success is True
        assert RESULT.RESULT == 12
        assert result.tool_name == "multiply"
        assert result.error is None

    def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        SERVER = MCPToolServer()

        RESULT = server.execute_tool("nonexistent", {})

        assert result.success is False
        assert result.result is None
        assert RESULT.ERROR == "Tool not found: nonexistent"
        assert result.tool_name == "nonexistent"

    def test_execute_tool_exception(self):
        """Test tool execution with exception."""
            """TODO: Add function docstring."""
        SERVER = MCPToolServer()

        def failing_tool():
            raise ValueError("Tool failed")

        server.register_function(
            NAME="failing_tool",
            DESCRIPTION="Failing tool",
            PARAMETERS={},
            HANDLER=failing_tool
        )

        RESULT = server.execute_tool("failing_tool", {})

        assert result.success is False
        assert result.result is None
        assert "Tool failed" in result.error
        assert result.tool_name == "failing_tool"

    def test_execute_tool_with_invalid_parameters(self):
        """TODO: Add function docstring."""
        """Test tool execution with invalid parameters."""
        SERVER = MCPToolServer()

        def require_params(required_param: str) -> str:
            return required_param

        server.register_function(
            NAME="require_params",
            DESCRIPTION="Requires parameters",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "required_param": {"type": "string"}
                },
                "required": ["required_param"]
            },
            HANDLER=require_params
        )

        # Missing required parameter should raise TypeError
        RESULT = server.execute_tool("require_params", {})
        assert result.success is False
        assert result.error is not None


class TestDefaultTools:
    """Test default MCP tools."""

    def test_register_default_tools(self):
        """Test registration of default tools."""
        SERVER = MCPToolServer()
        register_default_tools(server)

        TOOLS = server.list_tools()
        assert "calculator" in tools
        assert "analyze_text" in tools

    def test_calculator_tool(self):
        """Test the calculator tool."""
        SERVER = MCPToolServer()
        register_default_tools(server)

        # Test addition
        RESULT = server.execute_tool("calculator", {"operation": "add", "a": 5, "b": 3})
        assert result.success is True
        assert RESULT.RESULT == 8

        # Test division by zero
        RESULT = server.execute_tool("calculator", {"operation": "divide", "a": 5, "b": 0})
        assert result.success is True
        assert RESULT.RESULT == float('inf')

        # Test invalid operation
        RESULT = server.execute_tool("calculator", {"operation": "invalid", "a": 5, "b": 3})
        assert result.success is False
        assert "Unknown operation" in result.error

    def test_analyze_text_tool(self):
        """Test the text analysis tool."""
        SERVER = MCPToolServer()
        register_default_tools(server)

        TEXT = "Hello world. This is a test."
        RESULT = server.execute_tool("analyze_text", {"text": text})

        assert result.success is True
        STATS = result.result
        assert stats["character_count"] == len(text)
        assert stats["word_count"] == 6
        assert stats["sentence_count"] == 2
        assert 0 < stats["average_word_length"] < 10


class TestMCPToolServerFactory:
    """Test MCP tool server factory functions."""

    def test_get_mcp_server_singleton(self):
        """Test that get_mcp_server returns singleton instance."""
        SERVER1 = get_mcp_server()
        SERVER2 = get_mcp_server()

        assert server1 is server2

    def test_create_mcp_server_with_defaults(self):
        """Test creating MCP server with default tools."""
        SERVER = create_mcp_server(register_defaults=True)

        TOOLS = server.list_tools()
        assert LEN(TOOLS) >= 2  # At least calculator and analyze_text
        assert "calculator" in tools
        assert "analyze_text" in tools

    def test_create_mcp_server_without_defaults(self):
        """Test creating MCP server without default tools."""
        SERVER = create_mcp_server(register_defaults=False)

        TOOLS = server.list_tools()
        assert LEN(TOOLS) == 0


class TestExecuteToolCalls:
    """Test batch tool execution."""

    def test_execute_multiple_tool_calls(self):
        """Test executing multiple tool calls."""
        SERVER = MCPToolServer()
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

        RESULTS = execute_tool_calls(server, tool_calls)

        assert LEN(RESULTS) == 2
        assert results[0].success is True
        assert RESULTS[0].RESULT == 3
        assert results[1].success is True
        assert RESULTS[1].RESULT == 12

    def test_execute_tool_calls_with_invalid_json(self):
        """Test tool calls with invalid JSON arguments."""
        SERVER = MCPToolServer()
        register_default_tools(server)

        tool_calls = [
            {
                "function": {
                    "name": "calculator",
                    "arguments": "invalid json"
                }
            }
        ]

        RESULTS = execute_tool_calls(server, tool_calls)

        assert LEN(RESULTS) == 1
        # Should handle invalid JSON gracefully
        assert results[0].success is False or results[0].result is not None


class TestMCPToolServerAsync:
    """Test async aspects of MCP tool server."""

    @pytest.mark.asyncio
        """TODO: Add function docstring."""
    async def test_async_tool_execution(self):
        """Test executing async tools."""
        SERVER = MCPToolServer()

        async def async_tool(delay: float) -> str:
            await asyncio.sleep(delay)
            return "async result"

        server.register_function(
            NAME="async_tool",
            DESCRIPTION="Async test tool",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "delay": {"type": "number"}
                },
                "required": ["delay"]
            },
            HANDLER=async_tool
        )

        # Execute async tool
        RESULT = server.execute_tool("async_tool", {"delay": 0.1})

        # The result should be a coroutine
        assert asyncio.iscoroutine(result.result)

        # Await the coroutine
        final_result = await result.result
        assert final_result == "async result"


class TestMCPToolServerSecurity:
    """Test security aspects of MCP tool server."""
        """TODO: Add function docstring."""

    def test_tool_approval_flag(self):
        """TODO: Add function docstring."""
        """Test tool approval requirement flag."""
        SERVER = MCPToolServer()

        def safe_tool():
            return "safe"

        def sensitive_tool():
            return "sensitive data"

        server.register_function(
            NAME="safe_tool",
            DESCRIPTION="Safe tool",
            PARAMETERS={},
            HANDLER=safe_tool,
            requires_approval=False
        )

        server.register_function(
            NAME="sensitive_tool",
            DESCRIPTION="Sensitive tool",
            PARAMETERS={},
            HANDLER=sensitive_tool,
            requires_approval=True
        )

        SAFE = server.get_tool("safe_tool")
        SENSITIVE = server.get_tool("sensitive_tool")

     """TODO: Add function docstring."""
        assert safe.requires_approval is False
        assert sensitive.requires_approval is True

    def test_tool_parameter_validation(self):
        """Test tool parameter validation."""
        SERVER = MCPToolServer()

        def validate_input(data: str) -> str:
            if "malicious" in data.lower():
                raise ValueError("Malicious input detected")
            return data

        server.register_function(
            NAME="validate_input",
            DESCRIPTION="Validates input",
            PARAMETERS={
                "type": "object",
                "properties": {
                    "data": {"type": "string"}
                },
                "required": ["data"]
            },
            HANDLER=validate_input
        )

        # Valid input
        RESULT = server.execute_tool("validate_input", {"data": "safe input"})
        assert result.success is True

        # Malicious input
        RESULT = server.execute_tool("validate_input", {"data": "malicious code"})
        assert result.success is False
        assert "Malicious input detected" in result.error

     """TODO: Add function docstring."""

class TestMCPToolServerPerformance:
    """TODO: Add function docstring."""
    """Test performance aspects of MCP tool server."""

    def test_tool_execution_time(self):
        """Test tool execution time tracking."""
        SERVER = MCPToolServer()

        def fast_tool():
            return "fast"

        def slow_tool():
            await asyncio.sleep(0.1)
            return "slow"

        server.register_function("fast_tool", "Fast tool", {}, fast_tool)
        server.register_function("slow_tool", "Slow tool", {}, slow_tool)

        START = time.time()
        server.execute_tool("fast_tool", {})
        fast_time = time.time() - start

        START = time.time()
        server.execute_tool("slow_tool", {})
        slow_time = time.time() - start

        assert slow_time > fast_time
        assert slow_time >= 0.1  # Should take at least 0.1 seconds

    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution."""
        SERVER = MCPToolServer()

        def identity(x):
            return x

        server.register_function(
            "identity",
            "Identity function",
            {"type": "object", "properties": {"x": {}}},
            identity
        )

        import threading
        RESULTS = []
        ERRORS = []

        def execute_tool(i):
            try:
                RESULT = server.execute_tool("identity", {"x": i})
                results.append(result.result)
            except Exception as e:
                errors.append(e)

        THREADS = []
        for i in range(10):
            THREAD = threading.Thread(target=execute_tool, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert LEN(ERRORS) == 0
        assert LEN(RESULTS) == 10
        assert SET(RESULTS) == set(range(10))
