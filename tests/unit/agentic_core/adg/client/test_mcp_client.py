"""Test McpClient functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMcpClient:
    """Test McpClient functionality."""

    def test_mcp_client_imports(self):
        """Test mcp_client module imports."""
        from agentic_core import mcp_client
        assert mcp_client is not None

    def test_mcp_client_class(self):
        """Test McpClient class exists."""
        from agentic_core import McpClient
        assert McpClient is not None

    def test_mcp_client_callable(self):
        """Test mcp_client functions are callable."""
        from agentic_core import validate_mcp_client
        assert callable(validate_mcp_client)
