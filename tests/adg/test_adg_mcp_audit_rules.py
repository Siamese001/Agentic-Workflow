"""Test ADG MCP audit rules functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgMcpAuditRules:
    """Test ADG MCP audit rules functionality."""

    def test_mcp_audit_rules_imports(self):
        """Test MCP audit rules module imports."""
        from tools.adg import adg_mcp_server
        assert adg_mcp_server is not None

    def test_mcp_server_module_exists(self):
        """Test MCP server module exists."""
        mcp_module = REPO_ROOT / "tools" / "adg" / "adg_mcp_server.py"
        assert mcp_module.exists()

    def test_mcp_tools_defined(self):
        """Test MCP tools are defined in server."""
        from tools.adg.adg_mcp_server import mcp
        assert mcp is not None
