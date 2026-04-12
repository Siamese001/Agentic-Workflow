"""Test SurgicalContext functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSurgicalContext:
    """Test SurgicalContext functionality."""

    def test_surgical_context_imports(self):
        """Test surgical_context module imports."""
        from agentic_core import surgical_context

        assert surgical_context is not None

    def test_surgical_context_class(self):
        """Test SurgicalContext class exists."""
        from agentic_core import SurgicalContext

        assert SurgicalContext is not None

    def test_surgical_context_callable(self):
        """Test surgical_context functions are callable."""
        from agentic_core import validate_surgical_context

        assert callable(validate_surgical_context)
