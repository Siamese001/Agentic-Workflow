"""
file: tests/maintenance/test_tool_registry.py
description: Test cases for the tool_registry to verify tool safety and discovery.
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def disable_path_shield():
    """Marker fixture to disable path shield in conftest."""
    pass


@pytest.fixture
def tool_registry(disable_path_shield):
    """Provides a fresh tool_registry instance for each test."""
    from apps_shared.utils.tool_registry import tool_registry

    tool_registry.reset_instance()
    return tool_registry.get_instance()


class TestToolSafetyVerification:
    """Tests to verify tool registration safety."""

    def test_reject_rogue_tool_in_archives(self, tool_registry):
        """
        TC-001: Attempt to register a tool located in archives/.
        Expected: Registry must reject it.
        """

        def rogue_func():
            return "rogue"

        result = tool_registry.register_tool(
            tool_name="rogue_tool",
            tool_path="archives/void_violations/rogue_tool.py",
            tool_func=rogue_func,
        )

        assert result is False, "Registry should reject tools in archives/"
        assert "rogue_tool" not in tool_registry

    def test_reject_rogue_tool_in_tmp(self, tool_registry):
        """
        TC-002: Attempt to register a tool located in /tmp or temp folder.
        Expected: Registry must reject it.
        """

        def temp_func():
            return "temp"

        result = tool_registry.register_tool(
            tool_name="temp_tool", tool_path="/tmp/temp_tool.py", tool_func=temp_func
        )

        assert result is False, "Registry should reject tools in /tmp/"
        assert "temp_tool" not in tool_registry

    def test_accept_tool_in_sovereign_territory(self, tool_registry):
        """
        TC-003: Register a tool in valid agentic_core location.
        Expected: Registry must accept it.
        """

        def valid_func():
            return "valid"

        result = tool_registry.register_tool(
            tool_name="valid_tool",
            tool_path="agentic_core/L2_execution/tool_registry/file_io_tools.py",
            tool_func=valid_func,
            description="File I/O operations",
        )

        assert result is True, "Registry should accept tools in agentic_core/"
        assert "valid_tool" in tool_registry

        # Verify tool data
        tool = tool_registry.get_tool("valid_tool")
        assert tool is not None
        assert tool["verified"] is True
        assert tool["description"] == "File I/O operations"

    def test_accept_tool_in_apps_shared(self, tool_registry):
        """
        TC-004: Register a tool in apps_shared/utils.
        Expected: Registry must accept it.
        """

        def shared_func():
            return "shared"

        result = tool_registry.register_tool(
            tool_name="shared_tool",
            tool_path="apps_shared/utils/tool_registry.py",
            tool_func=shared_func,
        )

        assert result is True, "Registry should accept tools in apps_shared/"
        assert "shared_tool" in tool_registry


class TestToolDiscovery:
    """Tests for tool discovery via SovereignIndex."""

    def test_discover_tools_pattern(self, tool_registry, disable_path_shield):
        """
        TC-005: Use SovereignIndex to discover tool files.
        Expected: Should find tools in agentic_core/L2_execution/tool_registry/.
        """
        discovered = tool_registry.discover_tools("*_tools.py")

        assert len(discovered) > 0, "Should discover at least one *_tools.py file"

        # Verify at least one known tool file is found
        tool_names = [p.name for p in discovered]
        assert any("tools" in name for name in tool_names), (
            f"Should find tool files, got: {tool_names}"
        )


class TestToolRetrieval:
    """Tests for tool retrieval functionality."""

    def test_get_tool_func(self, tool_registry):
        """
        TC-006: Retrieve tool function by name.
        Expected: Should return the callable function.
        """

        def my_tool():
            return "executed"

        tool_registry.register_tool(
            tool_name="my_tool",
            tool_path="agentic_core/L2_execution/tool_registry/tools.py",
            tool_func=my_tool,
        )

        func = tool_registry.get_tool_func("my_tool")
        assert func is not None
        assert callable(func)
        assert func() == "executed"

    def test_get_nonexistent_tool(self, tool_registry):
        """
        TC-007: Attempt to retrieve a non-existent tool.
        Expected: Should return None.
        """
        tool = tool_registry.get_tool("nonexistent_tool")
        assert tool is None

    def test_list_tools(self, tool_registry):
        """
        TC-008: List all registered tools.
        Expected: Should return list of tool names.
        """

        def tool1():
            pass

        def tool2():
            pass

        tool_registry.register_tool("tool1", "agentic_core/utils/sovereign_index.py", tool1)
        tool_registry.register_tool(
            "tool2", "agentic_core/L2_execution/tool_registry/tools.py", tool2
        )

        tools = tool_registry.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools
        assert len(tools) == 2


class TestToolUnregistration:
    """Tests for tool unregistration."""

    def test_unregister_tool(self, tool_registry):
        """
        TC-009: Unregister a previously registered tool.
        Expected: Tool should be removed from registry.
        """

        def temp_tool():
            pass

        tool_registry.register_tool(
            "temp_tool", "agentic_core/L2_execution/tool_registry/tools.py", temp_tool
        )
        assert "temp_tool" in tool_registry

        result = tool_registry.unregister_tool("temp_tool")
        assert result is True
        assert "temp_tool" not in tool_registry

    def test_unregister_nonexistent_tool(self, tool_registry):
        """
        TC-010: Attempt to unregister a non-existent tool.
        Expected: Should return False.
        """
        result = tool_registry.unregister_tool("nonexistent")
        assert result is False


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main(["-v", __file__]))
