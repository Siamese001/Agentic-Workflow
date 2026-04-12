"""Test SecurityManagerAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSecurityManagerAgentAdg:
    """Test SecurityManagerAgentAdg functionality."""

    def test_security_manager_agent_adg_imports(self):
        """Test security_manager_agent_adg module imports."""
        from agentic_core import security_manager_agent_adg

        assert security_manager_agent_adg is not None

    def test_security_manager_agent_adg_class(self):
        """Test SecurityManagerAgentAdg class exists."""
        from agentic_core import SecurityManagerAgentAdg

        assert SecurityManagerAgentAdg is not None

    def test_security_manager_agent_adg_callable(self):
        """Test security_manager_agent_adg functions are callable."""
        from agentic_core import validate_security_manager_agent_adg

        assert callable(validate_security_manager_agent_adg)
