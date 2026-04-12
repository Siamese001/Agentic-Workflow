"""Test Completeness functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCompleteness:
    """Test Completeness functionality."""

    def test_completeness_imports(self):
        """Test completeness module imports."""
        from agentic_core import completeness

        assert completeness is not None

    def test_completeness_class(self):
        """Test Completeness class exists."""
        from agentic_core import Completeness

        assert Completeness is not None

    def test_completeness_callable(self):
        """Test completeness functions are callable."""
        from agentic_core import validate_completeness

        assert callable(validate_completeness)
