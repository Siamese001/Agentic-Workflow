"""Test QueueOverflowFallback functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQueueOverflowFallback:
    """Test QueueOverflowFallback functionality."""

    def test_queue_overflow_fallback_imports(self):
        """Test queue_overflow_fallback module imports."""
        from agentic_core import queue_overflow_fallback

        assert queue_overflow_fallback is not None

    def test_queue_overflow_fallback_class(self):
        """Test QueueOverflowFallback class exists."""
        from agentic_core import QueueOverflowFallback

        assert QueueOverflowFallback is not None

    def test_queue_overflow_fallback_callable(self):
        """Test queue_overflow_fallback functions are callable."""
        from agentic_core import validate_queue_overflow_fallback

        assert callable(validate_queue_overflow_fallback)
