"""Test QualityDetector functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQualityDetector:
    """Test QualityDetector functionality."""

    def test_quality_detector_imports(self):
        """Test quality_detector module imports."""
        from agentic_core import quality_detector
        assert quality_detector is not None

    def test_quality_detector_class(self):
        """Test QualityDetector class exists."""
        from agentic_core import QualityDetector
        assert QualityDetector is not None

    def test_quality_detector_callable(self):
        """Test quality_detector functions are callable."""
        from agentic_core import validate_quality_detector
        assert callable(validate_quality_detector)
