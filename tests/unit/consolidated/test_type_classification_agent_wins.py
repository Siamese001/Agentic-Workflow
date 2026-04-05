"""Test TypeClassificationAgentWins functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTypeClassificationAgentWins:
    """Test TypeClassificationAgentWins functionality."""

    def test_type_classification_agent_wins_imports(self):
        """Test type_classification_agent_wins module imports."""
        from agentic_core import type_classification_agent_wins
        assert type_classification_agent_wins is not None

    def test_type_classification_agent_wins_class(self):
        """Test TypeClassificationAgentWins class exists."""
        from agentic_core import TypeClassificationAgentWins
        assert TypeClassificationAgentWins is not None

    def test_type_classification_agent_wins_callable(self):
        """Test type_classification_agent_wins functions are callable."""
        from agentic_core import validate_type_classification_agent_wins
        assert callable(validate_type_classification_agent_wins)
