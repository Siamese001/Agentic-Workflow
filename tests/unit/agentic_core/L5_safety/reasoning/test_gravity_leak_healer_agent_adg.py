"""Test GravityLeakHealerAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGravityLeakHealerAgentAdg:
    """Test GravityLeakHealerAgentAdg functionality."""

    def test_gravity_leak_healer_agent_adg_imports(self):
        """Test gravity_leak_healer_agent_adg module imports."""
        from agentic_core import gravity_leak_healer_agent_adg

        assert gravity_leak_healer_agent_adg is not None

    def test_gravity_leak_healer_agent_adg_class(self):
        """Test GravityLeakHealerAgentAdg class exists."""
        from agentic_core import GravityLeakHealerAgentAdg

        assert GravityLeakHealerAgentAdg is not None

    def test_gravity_leak_healer_agent_adg_callable(self):
        """Test gravity_leak_healer_agent_adg functions are callable."""
        from agentic_core import validate_gravity_leak_healer_agent_adg

        assert callable(validate_gravity_leak_healer_agent_adg)
