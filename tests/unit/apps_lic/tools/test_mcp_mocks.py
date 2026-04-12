"""Test McpMocks functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMcpMocks:
    """Test McpMocks functionality."""

    def test_mcp_mocks_imports(self):
        """Test mcp_mocks module imports."""
        from agentic_core import mcp_mocks

        assert mcp_mocks is not None

    def test_mcp_mocks_class(self):
        """Test McpMocks class exists."""
        from agentic_core import McpMocks

        assert McpMocks is not None

    def test_mcp_mocks_callable(self):
        """Test mcp_mocks functions are callable."""
        from agentic_core import validate_mcp_mocks

        assert callable(validate_mcp_mocks)
