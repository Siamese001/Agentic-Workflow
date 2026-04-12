"""Test SystemInvariantScannerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSystemInvariantScannerAdg:
    """Test SystemInvariantScannerAdg functionality."""

    def test_system_invariant_scanner_adg_imports(self):
        """Test system_invariant_scanner_adg module imports."""
        from agentic_core import system_invariant_scanner_adg

        assert system_invariant_scanner_adg is not None

    def test_system_invariant_scanner_adg_class(self):
        """Test SystemInvariantScannerAdg class exists."""
        from agentic_core import SystemInvariantScannerAdg

        assert SystemInvariantScannerAdg is not None

    def test_system_invariant_scanner_adg_callable(self):
        """Test system_invariant_scanner_adg functions are callable."""
        from agentic_core import validate_system_invariant_scanner_adg

        assert callable(validate_system_invariant_scanner_adg)
