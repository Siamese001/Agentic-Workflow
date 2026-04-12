"""Test SystemArchitectAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSystemArchitectAgentAdg:
    """Test SystemArchitectAgentAdg functionality."""

    def test_system_architect_agent_adg_imports(self):
        """Test system_architect_agent_adg module imports."""
        from agentic_core import system_architect_agent_adg

        assert system_architect_agent_adg is not None

    def test_system_architect_agent_adg_class(self):
        """Test SystemArchitectAgentAdg class exists."""
        from agentic_core import SystemArchitectAgentAdg

        assert SystemArchitectAgentAdg is not None

    def test_system_architect_agent_adg_callable(self):
        """Test system_architect_agent_adg functions are callable."""
        from agentic_core import validate_system_architect_agent_adg

        assert callable(validate_system_architect_agent_adg)
