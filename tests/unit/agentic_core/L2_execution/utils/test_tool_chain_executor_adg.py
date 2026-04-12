"""Test ToolChainExecutorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolChainExecutorAdg:
    """Test ToolChainExecutorAdg functionality."""

    def test_tool_chain_executor_adg_imports(self):
        """Test tool_chain_executor_adg module imports."""
        from agentic_core import tool_chain_executor_adg

        assert tool_chain_executor_adg is not None

    def test_tool_chain_executor_adg_class(self):
        """Test ToolChainExecutorAdg class exists."""
        from agentic_core import ToolChainExecutorAdg

        assert ToolChainExecutorAdg is not None

    def test_tool_chain_executor_adg_callable(self):
        """Test tool_chain_executor_adg functions are callable."""
        from agentic_core import validate_tool_chain_executor_adg

        assert callable(validate_tool_chain_executor_adg)
