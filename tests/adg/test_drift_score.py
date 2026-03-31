"""Test drift score functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDriftScore:
    """Test drift score functionality."""

    def test_drift_score_imports(self):
        """Test drift score module imports."""
        from tools.adg import drift_score
        assert drift_score is not None

    def test_drift_score_calculate_function(self):
        """Test drift score calculate function."""
        from tools.adg.drift_score import calculate_drift
        assert callable(calculate_drift)

    def test_drift_score_compare_function(self):
        """Test drift score compare function."""
        from tools.adg.drift_score import compare_artifacts
        assert callable(compare_artifacts)
