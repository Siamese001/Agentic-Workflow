"""Test MetaLearningPipeline functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningPipeline:
    """Test MetaLearningPipeline functionality."""

    def test_meta_learning_pipeline_imports(self):
        """Test meta_learning_pipeline module imports."""
        from agentic_core import meta_learning_pipeline

        assert meta_learning_pipeline is not None

    def test_meta_learning_pipeline_class(self):
        """Test MetaLearningPipeline class exists."""
        from agentic_core import MetaLearningPipeline

        assert MetaLearningPipeline is not None

    def test_meta_learning_pipeline_callable(self):
        """Test meta_learning_pipeline functions are callable."""
        from agentic_core import validate_meta_learning_pipeline

        assert callable(validate_meta_learning_pipeline)
