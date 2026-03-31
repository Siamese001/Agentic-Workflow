"""Test StaticScanner functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestStaticScanner:
    """Test StaticScanner functionality."""

    def test_static_scanner_imports(self):
        """Test static_scanner module imports."""
        from agentic_core import static_scanner
        assert static_scanner is not None

    def test_static_scanner_class(self):
        """Test StaticScanner class exists."""
        from agentic_core import StaticScanner
        assert StaticScanner is not None

    def test_static_scanner_callable(self):
        """Test static_scanner functions are callable."""
        from agentic_core import validate_static_scanner
        assert callable(validate_static_scanner)
