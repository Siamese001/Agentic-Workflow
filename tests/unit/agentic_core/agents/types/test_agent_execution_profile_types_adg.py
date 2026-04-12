"""Test AgentExecutionProfileTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentExecutionProfileTypesAdg:
    """Test AgentExecutionProfileTypesAdg functionality."""

    def test_agent_execution_profile_types_adg_imports(self):
        """Test agent_execution_profile_types_adg module imports."""
        from agentic_core import agent_execution_profile_types_adg

        assert agent_execution_profile_types_adg is not None

    def test_agent_execution_profile_types_adg_class(self):
        """Test AgentExecutionProfileTypesAdg class exists."""
        from agentic_core import AgentExecutionProfileTypesAdg

        assert AgentExecutionProfileTypesAdg is not None

    def test_agent_execution_profile_types_adg_callable(self):
        """Test agent_execution_profile_types_adg functions are callable."""
        from agentic_core import validate_agent_execution_profile_types_adg

        assert callable(validate_agent_execution_profile_types_adg)
