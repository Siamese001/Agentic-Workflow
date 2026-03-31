"""Test AgentExecutorGateway functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentExecutorGateway:
    """Test AgentExecutorGateway functionality."""

    def test_agent_executor_gateway_imports(self):
        """Test agent_executor_gateway module imports."""
        from agentic_core import agent_executor_gateway
        assert agent_executor_gateway is not None

    def test_agent_executor_gateway_class(self):
        """Test AgentExecutorGateway class exists."""
        from agentic_core import AgentExecutorGateway
        assert AgentExecutorGateway is not None

    def test_agent_executor_gateway_callable(self):
        """Test agent_executor_gateway functions are callable."""
        from agentic_core import validate_agent_executor_gateway
        assert callable(validate_agent_executor_gateway)
