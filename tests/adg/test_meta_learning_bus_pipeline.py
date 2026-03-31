"""Test meta learning bus pipeline functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMetaLearningBusPipeline:
    """Test meta learning bus pipeline functionality."""

    def test_meta_learning_pipeline_imports(self):
        """Test meta learning pipeline module imports."""
        from system_learning.meta_learning import pipeline
        assert pipeline is not None

    def test_meta_learning_pipeline_class(self):
        """Test meta learning pipeline class exists."""
        from system_learning.meta_learning.pipeline import MetaLearningPipeline
        assert MetaLearningPipeline is not None

    def test_meta_learning_run_pipeline(self):
        """Test meta learning run pipeline function."""
        from system_learning.meta_learning.pipeline import run_pipeline
        assert callable(run_pipeline)
