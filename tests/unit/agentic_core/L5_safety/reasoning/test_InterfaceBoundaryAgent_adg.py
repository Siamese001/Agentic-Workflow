"""Test InterfaceboundaryagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInterfaceboundaryagentAdg:
    """Test InterfaceboundaryagentAdg functionality."""

    def test_InterfaceBoundaryAgent_adg_imports(self):
        """Test InterfaceBoundaryAgent_adg module imports."""
        from agentic_core import InterfaceBoundaryAgent_adg

        assert InterfaceBoundaryAgent_adg is not None

    def test_InterfaceBoundaryAgent_adg_class(self):
        """Test InterfaceboundaryagentAdg class exists."""
        from agentic_core import InterfaceboundaryagentAdg

        assert InterfaceboundaryagentAdg is not None

    def test_InterfaceBoundaryAgent_adg_callable(self):
        """Test InterfaceBoundaryAgent_adg functions are callable."""
        from agentic_core import validate_InterfaceBoundaryAgent_adg

        assert callable(validate_InterfaceBoundaryAgent_adg)
