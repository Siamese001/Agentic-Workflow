"""Test LateChunking functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLateChunking:
    """Test LateChunking functionality."""

    def test_late_chunking_imports(self):
        """Test late_chunking module imports."""
        from agentic_core import late_chunking

        assert late_chunking is not None

    def test_late_chunking_class(self):
        """Test LateChunking class exists."""
        from agentic_core import LateChunking

        assert LateChunking is not None

    def test_late_chunking_callable(self):
        """Test late_chunking functions are callable."""
        from agentic_core import validate_late_chunking

        assert callable(validate_late_chunking)
