"""Test ToolRegistryAgent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolRegistryAgent:
    """Test ToolRegistryAgent functionality."""

    def test_tool_registry_agent_imports(self):
        """Test tool_registry_agent module imports."""
        from agentic_core import tool_registry_agent

        assert tool_registry_agent is not None

    def test_tool_registry_agent_class(self):
        """Test ToolRegistryAgent class exists."""
        from agentic_core import ToolRegistryAgent

        assert ToolRegistryAgent is not None

    def test_tool_registry_agent_callable(self):
        """Test tool_registry_agent functions are callable."""
        from agentic_core import validate_tool_registry_agent

        assert callable(validate_tool_registry_agent)
