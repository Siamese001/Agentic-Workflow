"""Test ReasoningAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReasoningAdg:
    """Test ReasoningAdg functionality."""

    def test_reasoning_adg_imports(self):
        """Test reasoning_adg module imports."""
        from agentic_core import reasoning_adg
        assert reasoning_adg is not None

    def test_reasoning_adg_class(self):
        """Test ReasoningAdg class exists."""
        from agentic_core import ReasoningAdg
        assert ReasoningAdg is not None

    def test_reasoning_adg_callable(self):
        """Test reasoning_adg functions are callable."""
        from agentic_core import validate_reasoning_adg
        assert callable(validate_reasoning_adg)
