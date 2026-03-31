"""Test RunGuardianHierarchyComplianceAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunGuardianHierarchyComplianceAdg:
    """Test RunGuardianHierarchyComplianceAdg functionality."""

    def test_run_guardian_hierarchy_compliance_adg_imports(self):
        """Test run_guardian_hierarchy_compliance_adg module imports."""
        from agentic_core import run_guardian_hierarchy_compliance_adg
        assert run_guardian_hierarchy_compliance_adg is not None

    def test_run_guardian_hierarchy_compliance_adg_class(self):
        """Test RunGuardianHierarchyComplianceAdg class exists."""
        from agentic_core import RunGuardianHierarchyComplianceAdg
        assert RunGuardianHierarchyComplianceAdg is not None

    def test_run_guardian_hierarchy_compliance_adg_callable(self):
        """Test run_guardian_hierarchy_compliance_adg functions are callable."""
        from agentic_core import validate_run_guardian_hierarchy_compliance_adg
        assert callable(validate_run_guardian_hierarchy_compliance_adg)
