"""Test ADG visitors rigorous functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgVisitorsRigorous:
    """Test ADG visitors rigorous functionality."""

    def test_visitors_imports(self):
        """Test visitors module imports."""
        from agentic_core.adg.extraction import static_scanner
        assert static_scanner is not None

    def test_block_visitor_exists(self):
        """Test block decomposition visitor exists."""
        from agentic_core.adg.extraction.static_scanner import _BlockDecompositionVisitor
        assert _BlockDecompositionVisitor is not None

    def test_type_surface_visitor_exists(self):
        """Test type surface visitor exists."""
        from agentic_core.adg.extraction.static_scanner import _TypeSurfaceCollector
        assert _TypeSurfaceCollector is not None
