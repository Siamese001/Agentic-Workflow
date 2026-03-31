"""Test HierarchyAgentHealerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHierarchyAgentHealerAdg:
    """Test HierarchyAgentHealerAdg functionality."""

    def test_hierarchy_agent_healer_adg_imports(self):
        """Test hierarchy_agent_healer_adg module imports."""
        from agentic_core import hierarchy_agent_healer_adg
        assert hierarchy_agent_healer_adg is not None

    def test_hierarchy_agent_healer_adg_class(self):
        """Test HierarchyAgentHealerAdg class exists."""
        from agentic_core import HierarchyAgentHealerAdg
        assert HierarchyAgentHealerAdg is not None

    def test_hierarchy_agent_healer_adg_callable(self):
        """Test hierarchy_agent_healer_adg functions are callable."""
        from agentic_core import validate_hierarchy_agent_healer_adg
        assert callable(validate_hierarchy_agent_healer_adg)
