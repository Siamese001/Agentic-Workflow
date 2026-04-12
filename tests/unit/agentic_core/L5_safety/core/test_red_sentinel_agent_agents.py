"""Test RedSentinelAgentAgents functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRedSentinelAgentAgents:
    """Test RedSentinelAgentAgents functionality."""

    def test_red_sentinel_agent_agents_imports(self):
        """Test red_sentinel_agent_agents module imports."""
        from agentic_core import red_sentinel_agent_agents

        assert red_sentinel_agent_agents is not None

    def test_red_sentinel_agent_agents_class(self):
        """Test RedSentinelAgentAgents class exists."""
        from agentic_core import RedSentinelAgentAgents

        assert RedSentinelAgentAgents is not None

    def test_red_sentinel_agent_agents_callable(self):
        """Test red_sentinel_agent_agents functions are callable."""
        from agentic_core import validate_red_sentinel_agent_agents

        assert callable(validate_red_sentinel_agent_agents)
