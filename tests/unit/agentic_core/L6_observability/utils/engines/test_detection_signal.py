"""Test DetectionSignal functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDetectionSignal:
    """Test DetectionSignal functionality."""

    def test_detection_signal_imports(self):
        """Test detection_signal module imports."""
        from agentic_core import detection_signal

        assert detection_signal is not None

    def test_detection_signal_class(self):
        """Test DetectionSignal class exists."""
        from agentic_core import DetectionSignal

        assert DetectionSignal is not None

    def test_detection_signal_callable(self):
        """Test detection_signal functions are callable."""
        from agentic_core import validate_detection_signal

        assert callable(validate_detection_signal)
