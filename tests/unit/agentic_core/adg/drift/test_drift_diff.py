"""Test DriftDiff functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDriftDiff:
    """Test DriftDiff functionality."""

    def test_drift_diff_imports(self):
        """Test drift_diff module imports."""
        from agentic_core import drift_diff

        assert drift_diff is not None

    def test_drift_diff_class(self):
        """Test DriftDiff class exists."""
        from agentic_core import DriftDiff

        assert DriftDiff is not None

    def test_drift_diff_callable(self):
        """Test drift_diff functions are callable."""
        from agentic_core import validate_drift_diff

        assert callable(validate_drift_diff)
