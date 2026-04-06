"""Test InitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInitAdg:
    """Test InitAdg functionality."""

    def test___init___adg_imports(self):
        """Test __init___adg module imports."""
        from agentic_core import __init___adg
        assert __init___adg is not None

    def test___init___adg_class(self):
        """Test InitAdg class exists."""
        from agentic_core import InitAdg
        assert InitAdg is not None

    def test___init___adg_callable(self):
        """Test __init___adg functions are callable."""
        from agentic_core import validate___init___adg
        assert callable(validate___init___adg)
