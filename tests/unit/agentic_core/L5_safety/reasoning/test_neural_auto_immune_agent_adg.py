"""Test NeuralAutoImmuneAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestNeuralAutoImmuneAgentAdg:
    """Test NeuralAutoImmuneAgentAdg functionality."""

    def test_neural_auto_immune_agent_adg_imports(self):
        """Test neural_auto_immune_agent_adg module imports."""
        from agentic_core import neural_auto_immune_agent_adg

        assert neural_auto_immune_agent_adg is not None

    def test_neural_auto_immune_agent_adg_class(self):
        """Test NeuralAutoImmuneAgentAdg class exists."""
        from agentic_core import NeuralAutoImmuneAgentAdg

        assert NeuralAutoImmuneAgentAdg is not None

    def test_neural_auto_immune_agent_adg_callable(self):
        """Test neural_auto_immune_agent_adg functions are callable."""
        from agentic_core import validate_neural_auto_immune_agent_adg

        assert callable(validate_neural_auto_immune_agent_adg)
