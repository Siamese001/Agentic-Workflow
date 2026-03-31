"""Test SilentDegradationDetector functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSilentDegradationDetector:
    """Test SilentDegradationDetector functionality."""

    def test_silent_degradation_detector_imports(self):
        """Test silent_degradation_detector module imports."""
        from agentic_core import silent_degradation_detector
        assert silent_degradation_detector is not None

    def test_silent_degradation_detector_class(self):
        """Test SilentDegradationDetector class exists."""
        from agentic_core import SilentDegradationDetector
        assert SilentDegradationDetector is not None

    def test_silent_degradation_detector_callable(self):
        """Test silent_degradation_detector functions are callable."""
        from agentic_core import validate_silent_degradation_detector
        assert callable(validate_silent_degradation_detector)
