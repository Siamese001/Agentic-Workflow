"""Test ToolsmithagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolsmithagentAdg:
    """Test ToolsmithagentAdg functionality."""

    def test_ToolsmithAgent_adg_imports(self):
        """Test ToolsmithAgent_adg module imports."""
        from agentic_core import ToolsmithAgent_adg

        assert ToolsmithAgent_adg is not None

    def test_ToolsmithAgent_adg_class(self):
        """Test ToolsmithagentAdg class exists."""
        from agentic_core import ToolsmithagentAdg

        assert ToolsmithagentAdg is not None

    def test_ToolsmithAgent_adg_callable(self):
        """Test ToolsmithAgent_adg functions are callable."""
        from agentic_core import validate_ToolsmithAgent_adg

        assert callable(validate_ToolsmithAgent_adg)
