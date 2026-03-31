"""Test ToolExecutor functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolExecutor:
    """Test ToolExecutor functionality."""

    def test_tool_executor_imports(self):
        """Test tool_executor module imports."""
        from agentic_core import tool_executor
        assert tool_executor is not None

    def test_tool_executor_class(self):
        """Test ToolExecutor class exists."""
        from agentic_core import ToolExecutor
        assert ToolExecutor is not None

    def test_tool_executor_callable(self):
        """Test tool_executor functions are callable."""
        from agentic_core import validate_tool_executor
        assert callable(validate_tool_executor)
