"""Test HandlerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHandlerAdg:
    """Test HandlerAdg functionality."""

    def test_handler_adg_imports(self):
        """Test handler_adg module imports."""
        from agentic_core import handler_adg
        assert handler_adg is not None

    def test_handler_adg_class(self):
        """Test HandlerAdg class exists."""
        from agentic_core import HandlerAdg
        assert HandlerAdg is not None

    def test_handler_adg_callable(self):
        """Test handler_adg functions are callable."""
        from agentic_core import validate_handler_adg
        assert callable(validate_handler_adg)
