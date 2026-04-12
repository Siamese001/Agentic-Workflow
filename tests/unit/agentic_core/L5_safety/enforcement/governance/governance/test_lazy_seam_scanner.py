"""Test LazySeamScanner functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLazySeamScanner:
    """Test LazySeamScanner functionality."""

    def test_lazy_seam_scanner_imports(self):
        """Test lazy_seam_scanner module imports."""
        from agentic_core import lazy_seam_scanner

        assert lazy_seam_scanner is not None

    def test_lazy_seam_scanner_class(self):
        """Test LazySeamScanner class exists."""
        from agentic_core import LazySeamScanner

        assert LazySeamScanner is not None

    def test_lazy_seam_scanner_callable(self):
        """Test lazy_seam_scanner functions are callable."""
        from agentic_core import validate_lazy_seam_scanner

        assert callable(validate_lazy_seam_scanner)
