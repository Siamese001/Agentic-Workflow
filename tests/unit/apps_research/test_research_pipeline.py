"""Test ResearchPipeline functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResearchPipeline:
    """Test ResearchPipeline functionality."""

    def test_research_pipeline_imports(self):
        """Test research_pipeline module imports."""
        from agentic_core import research_pipeline
        assert research_pipeline is not None

    def test_research_pipeline_class(self):
        """Test ResearchPipeline class exists."""
        from agentic_core import ResearchPipeline
        assert ResearchPipeline is not None

    def test_research_pipeline_callable(self):
        """Test research_pipeline functions are callable."""
        from agentic_core import validate_research_pipeline
        assert callable(validate_research_pipeline)
