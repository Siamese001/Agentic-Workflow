"""Test DepthPipelineExecuteSsot functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDepthPipelineExecuteSsot:
    """Test DepthPipelineExecuteSsot functionality."""

    def test_depth_pipeline_execute_ssot_imports(self):
        """Test depth_pipeline_execute_ssot module imports."""
        from agentic_core import depth_pipeline_execute_ssot
        assert depth_pipeline_execute_ssot is not None

    def test_depth_pipeline_execute_ssot_class(self):
        """Test DepthPipelineExecuteSsot class exists."""
        from agentic_core import DepthPipelineExecuteSsot
        assert DepthPipelineExecuteSsot is not None

    def test_depth_pipeline_execute_ssot_callable(self):
        """Test depth_pipeline_execute_ssot functions are callable."""
        from agentic_core import validate_depth_pipeline_execute_ssot
        assert callable(validate_depth_pipeline_execute_ssot)
