"""Test ViolationEvent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestViolationEvent:
    """Test ViolationEvent functionality."""

    def test_violation_event_imports(self):
        """Test violation_event module imports."""
        from agentic_core import violation_event
        assert violation_event is not None

    def test_violation_event_class(self):
        """Test ViolationEvent class exists."""
        from agentic_core import ViolationEvent
        assert ViolationEvent is not None

    def test_violation_event_callable(self):
        """Test violation_event functions are callable."""
        from agentic_core import validate_violation_event
        assert callable(validate_violation_event)
