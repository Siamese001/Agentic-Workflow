"""Test CompletenessMetrics functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCompletenessMetrics:
    """Test CompletenessMetrics functionality."""

    def test_completeness_metrics_imports(self):
        """Test completeness_metrics module imports."""
        from agentic_core import completeness_metrics

        assert completeness_metrics is not None

    def test_completeness_metrics_class(self):
        """Test CompletenessMetrics class exists."""
        from agentic_core import CompletenessMetrics

        assert CompletenessMetrics is not None

    def test_completeness_metrics_callable(self):
        """Test completeness_metrics functions are callable."""
        from agentic_core import validate_completeness_metrics

        assert callable(validate_completeness_metrics)
