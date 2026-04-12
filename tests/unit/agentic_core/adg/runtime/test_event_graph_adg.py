"""Test EventGraphAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEventGraphAdg:
    """Test EventGraphAdg functionality."""

    def test_event_graph_adg_imports(self):
        """Test event_graph_adg module imports."""
        from agentic_core import event_graph_adg

        assert event_graph_adg is not None

    def test_event_graph_adg_class(self):
        """Test EventGraphAdg class exists."""
        from agentic_core import EventGraphAdg

        assert EventGraphAdg is not None

    def test_event_graph_adg_callable(self):
        """Test event_graph_adg functions are callable."""
        from agentic_core import validate_event_graph_adg

        assert callable(validate_event_graph_adg)
