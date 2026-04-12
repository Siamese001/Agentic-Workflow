"""Test ResourceManagerAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResourceManagerAgentAdg:
    """Test ResourceManagerAgentAdg functionality."""

    def test_resource_manager_agent_adg_imports(self):
        """Test resource_manager_agent_adg module imports."""
        from agentic_core import resource_manager_agent_adg

        assert resource_manager_agent_adg is not None

    def test_resource_manager_agent_adg_class(self):
        """Test ResourceManagerAgentAdg class exists."""
        from agentic_core import ResourceManagerAgentAdg

        assert ResourceManagerAgentAdg is not None

    def test_resource_manager_agent_adg_callable(self):
        """Test resource_manager_agent_adg functions are callable."""
        from agentic_core import validate_resource_manager_agent_adg

        assert callable(validate_resource_manager_agent_adg)
