"""Test RunHierarchyAgentDryRunUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunHierarchyAgentDryRunUtilAdg:
    """Test RunHierarchyAgentDryRunUtilAdg functionality."""

    def test_run_hierarchy_agent_dry_run_util_adg_imports(self):
        """Test run_hierarchy_agent_dry_run_util_adg module imports."""
        from agentic_core import run_hierarchy_agent_dry_run_util_adg

        assert run_hierarchy_agent_dry_run_util_adg is not None

    def test_run_hierarchy_agent_dry_run_util_adg_class(self):
        """Test RunHierarchyAgentDryRunUtilAdg class exists."""
        from agentic_core import RunHierarchyAgentDryRunUtilAdg

        assert RunHierarchyAgentDryRunUtilAdg is not None

    def test_run_hierarchy_agent_dry_run_util_adg_callable(self):
        """Test run_hierarchy_agent_dry_run_util_adg functions are callable."""
        from agentic_core import validate_run_hierarchy_agent_dry_run_util_adg

        assert callable(validate_run_hierarchy_agent_dry_run_util_adg)
