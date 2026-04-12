"""Test QueueTimeoutFallback functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestQueueTimeoutFallback:
    """Test QueueTimeoutFallback functionality."""

    def test_queue_timeout_fallback_imports(self):
        """Test queue_timeout_fallback module imports."""
        from agentic_core import queue_timeout_fallback

        assert queue_timeout_fallback is not None

    def test_queue_timeout_fallback_class(self):
        """Test QueueTimeoutFallback class exists."""
        from agentic_core import QueueTimeoutFallback

        assert QueueTimeoutFallback is not None

    def test_queue_timeout_fallback_callable(self):
        """Test queue_timeout_fallback functions are callable."""
        from agentic_core import validate_queue_timeout_fallback

        assert callable(validate_queue_timeout_fallback)
