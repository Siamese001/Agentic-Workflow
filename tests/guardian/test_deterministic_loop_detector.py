"""Test DeterministicLoopDetector functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterministicLoopDetector:
    """Test DeterministicLoopDetector functionality."""

    def test_deterministic_loop_detector_imports(self):
        """Test deterministic_loop_detector module imports."""
        from agentic_core import deterministic_loop_detector
        assert deterministic_loop_detector is not None

    def test_deterministic_loop_detector_class(self):
        """Test DeterministicLoopDetector class exists."""
        from agentic_core import DeterministicLoopDetector
        assert DeterministicLoopDetector is not None

    def test_deterministic_loop_detector_callable(self):
        """Test deterministic_loop_detector functions are callable."""
        from agentic_core import validate_deterministic_loop_detector
        assert callable(validate_deterministic_loop_detector)
