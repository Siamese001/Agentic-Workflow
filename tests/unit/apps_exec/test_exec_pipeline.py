"""Test ExecPipeline functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestExecPipeline:
    """Test ExecPipeline functionality."""

    def test_exec_pipeline_imports(self):
        """Test exec_pipeline module imports."""
        from agentic_core import exec_pipeline

        assert exec_pipeline is not None

    def test_exec_pipeline_class(self):
        """Test ExecPipeline class exists."""
        from agentic_core import ExecPipeline

        assert ExecPipeline is not None

    def test_exec_pipeline_callable(self):
        """Test exec_pipeline functions are callable."""
        from agentic_core import validate_exec_pipeline

        assert callable(validate_exec_pipeline)
