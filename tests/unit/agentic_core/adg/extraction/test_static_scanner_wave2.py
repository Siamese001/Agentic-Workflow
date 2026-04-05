"""Test StaticScannerWave2 functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStaticScannerWave2:
    """Test StaticScannerWave2 functionality."""

    def test_static_scanner_wave2_imports(self):
        """Test static_scanner_wave2 module imports."""
        from agentic_core import static_scanner_wave2
        assert static_scanner_wave2 is not None

    def test_static_scanner_wave2_class(self):
        """Test StaticScannerWave2 class exists."""
        from agentic_core import StaticScannerWave2
        assert StaticScannerWave2 is not None

    def test_static_scanner_wave2_callable(self):
        """Test static_scanner_wave2 functions are callable."""
        from agentic_core import validate_static_scanner_wave2
        assert callable(validate_static_scanner_wave2)
