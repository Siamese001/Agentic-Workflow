"""Test AgentRegistry functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentRegistry:
    """Test AgentRegistry functionality."""

    def test_agent_registry_imports(self):
        """Test agent_registry module imports."""
        from agentic_core import agent_registry

        assert agent_registry is not None

    def test_agent_registry_class(self):
        """Test AgentRegistry class exists."""
        from agentic_core import AgentRegistry

        assert AgentRegistry is not None

    def test_agent_registry_callable(self):
        """Test agent_registry functions are callable."""
        from agentic_core import validate_agent_registry

        assert callable(validate_agent_registry)
