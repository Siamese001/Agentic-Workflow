"""Test InterfacesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInterfacesAdg:
    """Test InterfacesAdg functionality."""

    def test_interfaces_adg_imports(self):
        """Test interfaces_adg module imports."""
        from agentic_core import interfaces_adg

        assert interfaces_adg is not None

    def test_interfaces_adg_class(self):
        """Test InterfacesAdg class exists."""
        from agentic_core import InterfacesAdg

        assert InterfacesAdg is not None

    def test_interfaces_adg_callable(self):
        """Test interfaces_adg functions are callable."""
        from agentic_core import validate_interfaces_adg

        assert callable(validate_interfaces_adg)
