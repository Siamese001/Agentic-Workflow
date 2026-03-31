"""Test ADG P3 enhancements functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgP3Enhancements:
    """Test ADG P3 enhancements functionality."""

    def test_p3_enhancements_imports(self):
        """Test P3 enhancements module imports."""
        from agentic_core.adg.extraction import static_scanner
        assert static_scanner is not None

    def test_p3_block_decomposition_exists(self):
        """Test P3 block decomposition exists."""
        from agentic_core.adg.extraction.static_scanner import _BlockDecompositionVisitor
        assert _BlockDecompositionVisitor is not None

    def test_p3_type_surface_exists(self):
        """Test P3 type surface collector exists."""
        from agentic_core.adg.extraction.static_scanner import _TypeSurfaceCollector
        assert _TypeSurfaceCollector is not None
