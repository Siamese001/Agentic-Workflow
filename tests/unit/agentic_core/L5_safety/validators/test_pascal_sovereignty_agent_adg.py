"""Test PascalSovereigntyAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPascalSovereigntyAgentAdg:
    """Test PascalSovereigntyAgentAdg functionality."""

    def test_pascal_sovereignty_agent_adg_imports(self):
        """Test pascal_sovereignty_agent_adg module imports."""
        from agentic_core import pascal_sovereignty_agent_adg

        assert pascal_sovereignty_agent_adg is not None

    def test_pascal_sovereignty_agent_adg_class(self):
        """Test PascalSovereigntyAgentAdg class exists."""
        from agentic_core import PascalSovereigntyAgentAdg

        assert PascalSovereigntyAgentAdg is not None

    def test_pascal_sovereignty_agent_adg_callable(self):
        """Test pascal_sovereignty_agent_adg functions are callable."""
        from agentic_core import validate_pascal_sovereignty_agent_adg

        assert callable(validate_pascal_sovereignty_agent_adg)
