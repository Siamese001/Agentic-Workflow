"""Test LocalWorkflowLoaderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLocalWorkflowLoaderAdg:
    """Test LocalWorkflowLoaderAdg functionality."""

    def test_local_workflow_loader_adg_imports(self):
        """Test local_workflow_loader_adg module imports."""
        from agentic_core import local_workflow_loader_adg
        assert local_workflow_loader_adg is not None

    def test_local_workflow_loader_adg_class(self):
        """Test LocalWorkflowLoaderAdg class exists."""
        from agentic_core import LocalWorkflowLoaderAdg
        assert LocalWorkflowLoaderAdg is not None

    def test_local_workflow_loader_adg_callable(self):
        """Test local_workflow_loader_adg functions are callable."""
        from agentic_core import validate_local_workflow_loader_adg
        assert callable(validate_local_workflow_loader_adg)
