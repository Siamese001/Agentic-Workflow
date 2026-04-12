"""Test HoppipelineexecutorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHoppipelineexecutorAdg:
    """Test HoppipelineexecutorAdg functionality."""

    def test_HOPPipelineExecutor_adg_imports(self):
        """Test HOPPipelineExecutor_adg module imports."""
        from agentic_core import HOPPipelineExecutor_adg

        assert HOPPipelineExecutor_adg is not None

    def test_HOPPipelineExecutor_adg_class(self):
        """Test HoppipelineexecutorAdg class exists."""
        from agentic_core import HoppipelineexecutorAdg

        assert HoppipelineexecutorAdg is not None

    def test_HOPPipelineExecutor_adg_callable(self):
        """Test HOPPipelineExecutor_adg functions are callable."""
        from agentic_core import validate_HOPPipelineExecutor_adg

        assert callable(validate_HOPPipelineExecutor_adg)
