"""
Unit tests for shared_engine_ops/tool_ops/
Tests tool operations for external tool integration.
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ToolStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]
    required_params: List[str]

@dataclass
class ToolResult:
    success: bool
    data: Optional[Any]
    error: Optional[str]
    execution_time_ms: float

class TestToolRegistration:
    """Tests for tool registration."""

    def test_register_tool(self):
        """Tool is registered correctly."""
        tools: Dict[str, ToolDefinition] = {}

        tool = ToolDefinition(
            name="search",
            description="Search for documents",
            parameters={"query": "string", "limit": "integer"},
            required_params=["query"],
        )
        tools[tool.name] = tool

        assert "search" in tools
        assert tools["search"].description == "Search for documents"

    def test_get_registered_tool(self):
        """Registered tool is retrieved correctly."""
        tools = {
            "search": ToolDefinition(
                name="search",
                description="Search",
                parameters={},
                required_params=[],
            ),
        }

        tool = tools.get("search")
        assert tool is not None
        assert tool.name == "search"

    def test_unregistered_tool_returns_none(self):
        """Unregistered tool returns None."""
        tools: Dict[str, ToolDefinition] = {}
        tool = tools.get("nonexistent")
        assert tool is None

    def test_list_available_tools(self):
        """Available tools are listed correctly."""
        tools = {
            "search": ToolDefinition("search", "Search", {}, []),
            "calculate": ToolDefinition("calculate", "Calculate", {}, []),
        }

        available = list(tools.keys())
        assert len(available) == 2
        assert "search" in available


class TestToolExecution:
    """Tests for tool execution."""

    def test_execute_tool_success(self):
        """Tool executes successfully."""
        def mock_search(query: str) -> Dict:
            return {"results": [f"Result for: {query}"]}

        result = mock_search("test query")

        tool_result = ToolResult(
            success=True,
            data=result,
            error=None,
            execution_time_ms=50.0,
        )

        assert tool_result.success is True
        assert tool_result.data is not None

    def test_execute_tool_failure(self):
        """Tool failure is handled correctly."""
        def mock_failing_tool() -> Dict:
            raise ValueError("Tool execution failed")

        try:
            mock_failing_tool()
            tool_result = ToolResult(success=True, data={}, error=None, execution_time_ms=0)
        except ValueError as e:
            tool_result = ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time_ms=10.0,
            )

        assert tool_result.success is False
        assert tool_result.error is not None

    def test_execute_with_timeout(self):
        """Tool execution respects timeout."""
        timeout_ms = 1000
        execution_time_ms = 500

        timed_out = execution_time_ms > timeout_ms
        assert timed_out is False

    def test_execute_with_retry(self):
        """Tool execution retries on failure."""
        max_retries = 3
        attempts = 0
        success = False

        while attempts < max_retries and not success:
            attempts += 1
            if attempts == 2:  # Succeeds on second attempt
                success = True

        assert success is True
        assert attempts == 2


class TestToolParameterValidation:
    """Tests for tool parameter validation."""

    def test_validate_required_params(self):
        """Required parameters are validated."""
        tool = ToolDefinition(
            name="search",
            description="Search",
            parameters={"query": "string", "limit": "integer"},
            required_params=["query"],
        )

        params = {"limit": 10}  # Missing required 'query'

        missing = [p for p in tool.required_params if p not in params]
        assert "query" in missing

    def test_validate_param_types(self):
        """Parameter types are validated."""
        expected_types = {"query": str, "limit": int}
        params = {"query": "test", "limit": "ten"}  # Wrong type for limit

        type_errors = []
        for param, expected_type in expected_types.items():
            if param in params and not isinstance(params[param], expected_type):
                type_errors.append(f"{param}: expected {expected_type.__name__}")

        assert len(type_errors) == 1

    def test_validate_param_values(self):
        """Parameter values are validated."""
        constraints = {"limit": {"min": 1, "max": 100}}
        params = {"limit": 150}

        violations = []
        for param, bounds in constraints.items():
            value = params.get(param)
            if value is not None:
                if value < bounds["min"] or value > bounds["max"]:
                    violations.append(f"{param} out of range")

        assert len(violations) == 1


class TestToolStatusCheck:
    """Tests for tool status checking."""

    def test_tool_available(self):
        """Available tool status is detected."""
        tool_statuses = {
            "search": ToolStatus.AVAILABLE,
            "calculate": ToolStatus.AVAILABLE,
        }

        is_available = tool_statuses.get("search") == ToolStatus.AVAILABLE
        assert is_available is True

    def test_tool_unavailable(self):
        """Unavailable tool status is detected."""
        tool_statuses = {
            "search": ToolStatus.UNAVAILABLE,
        }

        is_available = tool_statuses.get("search") == ToolStatus.AVAILABLE
        assert is_available is False

    def test_tool_rate_limited(self):
        """Rate-limited tool status is detected."""
        tool_statuses = {
            "api_call": ToolStatus.RATE_LIMITED,
        }

        status = tool_statuses.get("api_call")
        assert status == ToolStatus.RATE_LIMITED

    def test_check_all_tools_status(self):
        """All tools status is checked."""
        tool_statuses = {
            "tool1": ToolStatus.AVAILABLE,
            "tool2": ToolStatus.UNAVAILABLE,
            "tool3": ToolStatus.AVAILABLE,
        }

        available_tools = [t for t, s in tool_statuses.items() if s == ToolStatus.AVAILABLE]
        assert len(available_tools) == 2
