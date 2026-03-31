"""Test CodeQualityMetrics functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeQualityMetrics:
    """Test CodeQualityMetrics functionality."""

    def test_code_quality_metrics_imports(self):
        """Test code_quality_metrics module imports."""
        from agentic_core import code_quality_metrics
        assert code_quality_metrics is not None

    def test_code_quality_metrics_class(self):
        """Test CodeQualityMetrics class exists."""
        from agentic_core import CodeQualityMetrics
        assert CodeQualityMetrics is not None

    def test_code_quality_metrics_callable(self):
        """Test code_quality_metrics functions are callable."""
        from agentic_core import validate_code_quality_metrics
        assert callable(validate_code_quality_metrics)
