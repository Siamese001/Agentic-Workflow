"""Test Input functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInput:
    """Test Input functionality."""

    def test_input_imports(self):
        """Test input module imports."""
        from agentic_core import input
        assert input is not None

    def test_input_class(self):
        """Test Input class exists."""
        from agentic_core import Input
        assert Input is not None

    def test_input_callable(self):
        """Test input functions are callable."""
        from agentic_core import validate_input
        assert callable(validate_input)
