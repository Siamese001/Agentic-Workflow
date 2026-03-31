"""Test surface linking example functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSurfaceLinkingExample:
    """Test surface linking example functionality."""

    def test_surface_linking_imports(self):
        """Test surface linking module imports."""
        from agentic_core.adg.extraction import static_scanner
        assert static_scanner is not None

    def test_type_surface_collector_exists(self):
        """Test type surface collector exists."""
        from agentic_core.adg.extraction.static_scanner import _TypeSurfaceCollector
        assert _TypeSurfaceCollector is not None

    def test_surface_linking_function(self):
        """Test surface linking function."""
        from agentic_core.adg.extraction.static_scanner import link_type_surface
        assert callable(link_type_surface)
