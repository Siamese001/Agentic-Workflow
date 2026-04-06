"""Test ExecutionAgents functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecutionAgents:
    """Test ExecutionAgents functionality."""

    def test_execution_agents_imports(self):
        """Test execution_agents module imports."""
        from agentic_core import execution_agents
        assert execution_agents is not None

    def test_execution_agents_class(self):
        """Test ExecutionAgents class exists."""
        from agentic_core import ExecutionAgents
        assert ExecutionAgents is not None

    def test_execution_agents_callable(self):
        """Test execution_agents functions are callable."""
        from agentic_core import validate_execution_agents
        assert callable(validate_execution_agents)
