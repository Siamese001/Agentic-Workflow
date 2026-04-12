"""Test GitOpsMcp functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGitOpsMcp:
    """Test GitOpsMcp functionality."""

    def test_git_ops_mcp_imports(self):
        """Test git_ops_mcp module imports."""
        from agentic_core import git_ops_mcp

        assert git_ops_mcp is not None

    def test_git_ops_mcp_class(self):
        """Test GitOpsMcp class exists."""
        from agentic_core import GitOpsMcp

        assert GitOpsMcp is not None

    def test_git_ops_mcp_callable(self):
        """Test git_ops_mcp functions are callable."""
        from agentic_core import validate_git_ops_mcp

        assert callable(validate_git_ops_mcp)
