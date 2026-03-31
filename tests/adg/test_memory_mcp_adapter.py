"""Test memory MCP adapter functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMemoryMcpAdapter:
    """Test memory MCP adapter functionality."""

    def test_memory_mcp_adapter_imports(self):
        """Test memory MCP adapter module imports."""
        from system_learning.memory import mcp_adapter
        assert mcp_adapter is not None

    def test_memory_mcp_adapter_class(self):
        """Test memory MCP adapter class exists."""
        from system_learning.memory.mcp_adapter import MemoryMCPAdapter
        assert MemoryMCPAdapter is not None

    def test_memory_mcp_connect_function(self):
        """Test memory MCP connect function."""
        from system_learning.memory.mcp_adapter import connect_to_mcp
        assert callable(connect_to_mcp)
