"""Test AgentRosterRunnerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentRosterRunnerAdg:
    """Test AgentRosterRunnerAdg functionality."""

    def test_agent_roster_runner_adg_imports(self):
        """Test agent_roster_runner_adg module imports."""
        from agentic_core import agent_roster_runner_adg

        assert agent_roster_runner_adg is not None

    def test_agent_roster_runner_adg_class(self):
        """Test AgentRosterRunnerAdg class exists."""
        from agentic_core import AgentRosterRunnerAdg

        assert AgentRosterRunnerAdg is not None

    def test_agent_roster_runner_adg_callable(self):
        """Test agent_roster_runner_adg functions are callable."""
        from agentic_core import validate_agent_roster_runner_adg

        assert callable(validate_agent_roster_runner_adg)
