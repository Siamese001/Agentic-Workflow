"""Test drift ratchet gate functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDriftRatchetGate:
    """Test drift ratchet gate functionality."""

    def test_drift_ratchet_imports(self):
        """Test drift ratchet module imports."""
        from tools.adg import drift_score
        assert drift_score is not None

    def test_drift_ratchet_check_function(self):
        """Test drift ratchet check function."""
        from tools.adg.drift_score import check_ratchet
        assert callable(check_ratchet)

    def test_drift_ratchet_threshold(self):
        """Test drift ratchet threshold exists."""
        from tools.adg.drift_score import RATCHET_THRESHOLD
        assert isinstance(RATCHET_THRESHOLD, (int, float))
