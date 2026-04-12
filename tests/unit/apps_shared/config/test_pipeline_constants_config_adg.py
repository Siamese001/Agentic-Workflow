"""Test PipelineConstantsConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPipelineConstantsConfigAdg:
    """Test PipelineConstantsConfigAdg functionality."""

    def test_pipeline_constants_config_adg_imports(self):
        """Test pipeline_constants_config_adg module imports."""
        from agentic_core import pipeline_constants_config_adg

        assert pipeline_constants_config_adg is not None

    def test_pipeline_constants_config_adg_class(self):
        """Test PipelineConstantsConfigAdg class exists."""
        from agentic_core import PipelineConstantsConfigAdg

        assert PipelineConstantsConfigAdg is not None

    def test_pipeline_constants_config_adg_callable(self):
        """Test pipeline_constants_config_adg functions are callable."""
        from agentic_core import validate_pipeline_constants_config_adg

        assert callable(validate_pipeline_constants_config_adg)
