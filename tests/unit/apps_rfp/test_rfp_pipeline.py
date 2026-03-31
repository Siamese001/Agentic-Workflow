"""Test RfpPipeline functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRfpPipeline:
    """Test RfpPipeline functionality."""

    def test_rfp_pipeline_imports(self):
        """Test rfp_pipeline module imports."""
        from agentic_core import rfp_pipeline
        assert rfp_pipeline is not None

    def test_rfp_pipeline_class(self):
        """Test RfpPipeline class exists."""
        from agentic_core import RfpPipeline
        assert RfpPipeline is not None

    def test_rfp_pipeline_callable(self):
        """Test rfp_pipeline functions are callable."""
        from agentic_core import validate_rfp_pipeline
        assert callable(validate_rfp_pipeline)
