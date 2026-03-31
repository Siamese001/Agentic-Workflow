"""Test ToolVerifierImplAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestToolVerifierImplAdg:
    """Test ToolVerifierImplAdg functionality."""

    def test_tool_verifier_impl_adg_imports(self):
        """Test tool_verifier_impl_adg module imports."""
        from agentic_core import tool_verifier_impl_adg
        assert tool_verifier_impl_adg is not None

    def test_tool_verifier_impl_adg_class(self):
        """Test ToolVerifierImplAdg class exists."""
        from agentic_core import ToolVerifierImplAdg
        assert ToolVerifierImplAdg is not None

    def test_tool_verifier_impl_adg_callable(self):
        """Test tool_verifier_impl_adg functions are callable."""
        from agentic_core import validate_tool_verifier_impl_adg
        assert callable(validate_tool_verifier_impl_adg)
