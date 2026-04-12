"""Test RunGuardianDriftDetectionAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunGuardianDriftDetectionAdg:
    """Test RunGuardianDriftDetectionAdg functionality."""

    def test_run_guardian_drift_detection_adg_imports(self):
        """Test run_guardian_drift_detection_adg module imports."""
        from agentic_core import run_guardian_drift_detection_adg

        assert run_guardian_drift_detection_adg is not None

    def test_run_guardian_drift_detection_adg_class(self):
        """Test RunGuardianDriftDetectionAdg class exists."""
        from agentic_core import RunGuardianDriftDetectionAdg

        assert RunGuardianDriftDetectionAdg is not None

    def test_run_guardian_drift_detection_adg_callable(self):
        """Test run_guardian_drift_detection_adg functions are callable."""
        from agentic_core import validate_run_guardian_drift_detection_adg

        assert callable(validate_run_guardian_drift_detection_adg)
