"""Test AdgAntipatternDetection functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgAntipatternDetection:
    """Test AdgAntipatternDetection functionality."""

    def test_adg_antipattern_imports(self):
        """Test ADG antipattern module imports."""
        from tools.adg import antipattern_detection
        assert antipattern_detection is not None

    def test_antipattern_detector_class(self):
        """Test antipattern detector class exists."""
        from tools.adg.antipattern_detection import AntipatternDetector
        assert AntipatternDetector is not None

    def test_detect_antipatterns_function(self):
        """Test detect antipatterns function."""
        from tools.adg.antipattern_detection import detect_antipatterns
        assert callable(detect_antipatterns)
