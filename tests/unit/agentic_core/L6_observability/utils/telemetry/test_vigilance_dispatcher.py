"""Test VigilanceDispatcher functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVigilanceDispatcher:
    """Test VigilanceDispatcher functionality."""

    def test_vigilance_dispatcher_imports(self):
        """Test vigilance_dispatcher module imports."""
        from agentic_core import vigilance_dispatcher

        assert vigilance_dispatcher is not None

    def test_vigilance_dispatcher_class(self):
        """Test VigilanceDispatcher class exists."""
        from agentic_core import VigilanceDispatcher

        assert VigilanceDispatcher is not None

    def test_vigilance_dispatcher_callable(self):
        """Test vigilance_dispatcher functions are callable."""
        from agentic_core import validate_vigilance_dispatcher

        assert callable(validate_vigilance_dispatcher)
