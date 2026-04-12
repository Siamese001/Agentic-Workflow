"""Test ToolEnforcementTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolEnforcementTypesAdg:
    """Test ToolEnforcementTypesAdg functionality."""

    def test_tool_enforcement_types_adg_imports(self):
        """Test tool_enforcement_types_adg module imports."""
        from agentic_core import tool_enforcement_types_adg

        assert tool_enforcement_types_adg is not None

    def test_tool_enforcement_types_adg_class(self):
        """Test ToolEnforcementTypesAdg class exists."""
        from agentic_core import ToolEnforcementTypesAdg

        assert ToolEnforcementTypesAdg is not None

    def test_tool_enforcement_types_adg_callable(self):
        """Test tool_enforcement_types_adg functions are callable."""
        from agentic_core import validate_tool_enforcement_types_adg

        assert callable(validate_tool_enforcement_types_adg)
