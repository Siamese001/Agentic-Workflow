"""Test RunWorkflowLicAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunWorkflowLicAdg:
    """Test RunWorkflowLicAdg functionality."""

    def test_run_workflow_lic_adg_imports(self):
        """Test run_workflow_lic_adg module imports."""
        from agentic_core import run_workflow_lic_adg

        assert run_workflow_lic_adg is not None

    def test_run_workflow_lic_adg_class(self):
        """Test RunWorkflowLicAdg class exists."""
        from agentic_core import RunWorkflowLicAdg

        assert RunWorkflowLicAdg is not None

    def test_run_workflow_lic_adg_callable(self):
        """Test run_workflow_lic_adg functions are callable."""
        from agentic_core import validate_run_workflow_lic_adg

        assert callable(validate_run_workflow_lic_adg)
