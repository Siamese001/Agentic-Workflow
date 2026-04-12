"""Test HitlGraphAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHitlGraphAdg:
    """Test HitlGraphAdg functionality."""

    def test_hitl_graph_adg_imports(self):
        """Test hitl_graph_adg module imports."""
        from agentic_core import hitl_graph_adg

        assert hitl_graph_adg is not None

    def test_hitl_graph_adg_class(self):
        """Test HitlGraphAdg class exists."""
        from agentic_core import HitlGraphAdg

        assert HitlGraphAdg is not None

    def test_hitl_graph_adg_callable(self):
        """Test hitl_graph_adg functions are callable."""
        from agentic_core import validate_hitl_graph_adg

        assert callable(validate_hitl_graph_adg)
