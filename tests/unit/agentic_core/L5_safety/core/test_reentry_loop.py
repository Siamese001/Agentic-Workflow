"""Test ReentryLoop functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReentryLoop:
    """Test ReentryLoop functionality."""

    def test_reentry_loop_imports(self):
        """Test reentry_loop module imports."""
        from agentic_core import reentry_loop

        assert reentry_loop is not None

    def test_reentry_loop_class(self):
        """Test ReentryLoop class exists."""
        from agentic_core import ReentryLoop

        assert ReentryLoop is not None

    def test_reentry_loop_callable(self):
        """Test reentry_loop functions are callable."""
        from agentic_core import validate_reentry_loop

        assert callable(validate_reentry_loop)
