"""Test McpToolTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMcpToolTypesAdg:
    """Test McpToolTypesAdg functionality."""

    def test_mcp_tool_types_adg_imports(self):
        """Test mcp_tool_types_adg module imports."""
        from agentic_core import mcp_tool_types_adg

        assert mcp_tool_types_adg is not None

    def test_mcp_tool_types_adg_class(self):
        """Test McpToolTypesAdg class exists."""
        from agentic_core import McpToolTypesAdg

        assert McpToolTypesAdg is not None

    def test_mcp_tool_types_adg_callable(self):
        """Test mcp_tool_types_adg functions are callable."""
        from agentic_core import validate_mcp_tool_types_adg

        assert callable(validate_mcp_tool_types_adg)
