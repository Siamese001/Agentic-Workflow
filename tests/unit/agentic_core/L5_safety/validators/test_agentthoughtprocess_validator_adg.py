"""Test AgentthoughtprocessValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAgentthoughtprocessValidatorAdg:
    """Test AgentthoughtprocessValidatorAdg functionality."""

    def test_agentthoughtprocess_validator_adg_imports(self):
        """Test agentthoughtprocess_validator_adg module imports."""
        from agentic_core import agentthoughtprocess_validator_adg

        assert agentthoughtprocess_validator_adg is not None

    def test_agentthoughtprocess_validator_adg_class(self):
        """Test AgentthoughtprocessValidatorAdg class exists."""
        from agentic_core import AgentthoughtprocessValidatorAdg

        assert AgentthoughtprocessValidatorAdg is not None

    def test_agentthoughtprocess_validator_adg_callable(self):
        """Test agentthoughtprocess_validator_adg functions are callable."""
        from agentic_core import validate_agentthoughtprocess_validator_adg

        assert callable(validate_agentthoughtprocess_validator_adg)
