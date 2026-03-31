"""Test Reasoning functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoning:
    """Test Reasoning functionality."""

    def test_reasoning_imports(self):
        """Test reasoning module imports."""
        from agentic_core import reasoning
        assert reasoning is not None

    def test_reasoning_class(self):
        """Test Reasoning class exists."""
        from agentic_core import Reasoning
        assert Reasoning is not None

    def test_reasoning_callable(self):
        """Test reasoning functions are callable."""
        from agentic_core import validate_reasoning
        assert callable(validate_reasoning)
