"""Test RunHierarchyHealerDryRunUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunHierarchyHealerDryRunUtilAdg:
    """Test RunHierarchyHealerDryRunUtilAdg functionality."""

    def test_run_hierarchy_healer_dry_run_util_adg_imports(self):
        """Test run_hierarchy_healer_dry_run_util_adg module imports."""
        from agentic_core import run_hierarchy_healer_dry_run_util_adg

        assert run_hierarchy_healer_dry_run_util_adg is not None

    def test_run_hierarchy_healer_dry_run_util_adg_class(self):
        """Test RunHierarchyHealerDryRunUtilAdg class exists."""
        from agentic_core import RunHierarchyHealerDryRunUtilAdg

        assert RunHierarchyHealerDryRunUtilAdg is not None

    def test_run_hierarchy_healer_dry_run_util_adg_callable(self):
        """Test run_hierarchy_healer_dry_run_util_adg functions are callable."""
        from agentic_core import validate_run_hierarchy_healer_dry_run_util_adg

        assert callable(validate_run_hierarchy_healer_dry_run_util_adg)
