"""Test ReasoningStreamer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoningStreamer:
    """Test ReasoningStreamer functionality."""

    def test_reasoning_streamer_imports(self):
        """Test reasoning_streamer module imports."""
        from agentic_core import reasoning_streamer

        assert reasoning_streamer is not None

    def test_reasoning_streamer_class(self):
        """Test ReasoningStreamer class exists."""
        from agentic_core import ReasoningStreamer

        assert ReasoningStreamer is not None

    def test_reasoning_streamer_callable(self):
        """Test reasoning_streamer functions are callable."""
        from agentic_core import validate_reasoning_streamer

        assert callable(validate_reasoning_streamer)
