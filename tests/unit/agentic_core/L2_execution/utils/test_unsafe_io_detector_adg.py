"""Test UnsafeIoDetectorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestUnsafeIoDetectorAdg:
    """Test UnsafeIoDetectorAdg functionality."""

    def test_unsafe_io_detector_adg_imports(self):
        """Test unsafe_io_detector_adg module imports."""
        from agentic_core import unsafe_io_detector_adg

        assert unsafe_io_detector_adg is not None

    def test_unsafe_io_detector_adg_class(self):
        """Test UnsafeIoDetectorAdg class exists."""
        from agentic_core import UnsafeIoDetectorAdg

        assert UnsafeIoDetectorAdg is not None

    def test_unsafe_io_detector_adg_callable(self):
        """Test unsafe_io_detector_adg functions are callable."""
        from agentic_core import validate_unsafe_io_detector_adg

        assert callable(validate_unsafe_io_detector_adg)
