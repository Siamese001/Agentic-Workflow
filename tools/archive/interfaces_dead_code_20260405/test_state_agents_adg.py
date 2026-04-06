"""Test StateAgentsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStateAgentsAdg:
    """Test StateAgentsAdg functionality."""

    def test_state_agents_adg_imports(self):
        """Test state_agents_adg module imports."""
        from agentic_core import state_agents_adg
        assert state_agents_adg is not None

    def test_state_agents_adg_class(self):
        """Test StateAgentsAdg class exists."""
        from agentic_core import StateAgentsAdg
        assert StateAgentsAdg is not None

    def test_state_agents_adg_callable(self):
        """Test state_agents_adg functions are callable."""
        from agentic_core import validate_state_agents_adg
        assert callable(validate_state_agents_adg)
