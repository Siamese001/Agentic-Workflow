"""Test EvalPipeline functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEvalPipeline:
    """Test EvalPipeline functionality."""

    def test_eval_pipeline_imports(self):
        """Test eval_pipeline module imports."""
        from agentic_core import eval_pipeline

        assert eval_pipeline is not None

    def test_eval_pipeline_class(self):
        """Test EvalPipeline class exists."""
        from agentic_core import EvalPipeline

        assert EvalPipeline is not None

    def test_eval_pipeline_callable(self):
        """Test eval_pipeline functions are callable."""
        from agentic_core import validate_eval_pipeline

        assert callable(validate_eval_pipeline)
