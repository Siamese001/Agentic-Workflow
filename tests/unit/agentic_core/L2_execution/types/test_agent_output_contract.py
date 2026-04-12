"""Test AgentOutputContract functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentOutputContract:
    """Test AgentOutputContract functionality."""

    def test_agent_output_contract_imports(self):
        """Test agent_output_contract module imports."""
        from agentic_core import agent_output_contract

        assert agent_output_contract is not None

    def test_agent_output_contract_class(self):
        """Test AgentOutputContract class exists."""
        from agentic_core import AgentOutputContract

        assert AgentOutputContract is not None

    def test_agent_output_contract_callable(self):
        """Test agent_output_contract functions are callable."""
        from agentic_core import validate_agent_output_contract

        assert callable(validate_agent_output_contract)
