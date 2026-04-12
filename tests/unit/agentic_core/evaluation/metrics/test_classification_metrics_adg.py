"""Test ClassificationMetricsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestClassificationMetricsAdg:
    """Test ClassificationMetricsAdg functionality."""

    def test_classification_metrics_adg_imports(self):
        """Test classification_metrics_adg module imports."""
        from agentic_core import classification_metrics_adg

        assert classification_metrics_adg is not None

    def test_classification_metrics_adg_class(self):
        """Test ClassificationMetricsAdg class exists."""
        from agentic_core import ClassificationMetricsAdg

        assert ClassificationMetricsAdg is not None

    def test_classification_metrics_adg_callable(self):
        """Test classification_metrics_adg functions are callable."""
        from agentic_core import validate_classification_metrics_adg

        assert callable(validate_classification_metrics_adg)
