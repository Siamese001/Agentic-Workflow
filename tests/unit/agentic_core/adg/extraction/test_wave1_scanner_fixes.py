"""Test Wave1ScannerFixes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestWave1ScannerFixes:
    """Test Wave1ScannerFixes functionality."""

    def test_wave1_scanner_fixes_imports(self):
        """Test wave1_scanner_fixes module imports."""
        from agentic_core import wave1_scanner_fixes
        assert wave1_scanner_fixes is not None

    def test_wave1_scanner_fixes_class(self):
        """Test Wave1ScannerFixes class exists."""
        from agentic_core import Wave1ScannerFixes
        assert Wave1ScannerFixes is not None

    def test_wave1_scanner_fixes_callable(self):
        """Test wave1_scanner_fixes functions are callable."""
        from agentic_core import validate_wave1_scanner_fixes
        assert callable(validate_wave1_scanner_fixes)
