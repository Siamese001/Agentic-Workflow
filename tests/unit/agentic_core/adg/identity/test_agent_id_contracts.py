"""Test AgentIdContracts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentIdContracts:
    """Test AgentIdContracts functionality."""

    def test_agent_id_contracts_imports(self):
        """Test agent ID contracts module imports."""
        from agentic_core import agent_id_contracts
        assert agent_id_contracts is not None

    def test_agent_id_contract_class(self):
        """Test agent ID contract class exists."""
        from agentic_core.agent_id_contracts import AgentIdContract
        assert AgentIdContract is not None

    def test_validate_agent_id(self):
        """Test validate agent ID function."""
        from agentic_core.agent_id_contracts import validate_agent_id
        assert callable(validate_agent_id)
