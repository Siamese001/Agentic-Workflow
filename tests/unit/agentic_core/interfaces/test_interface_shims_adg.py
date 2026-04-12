"""Test InterfaceShimsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestInterfaceShimsAdg:
    """Test InterfaceShimsAdg functionality."""

    def test_interface_shims_adg_imports(self):
        """Test interface_shims_adg module imports."""
        from agentic_core import interface_shims_adg

        assert interface_shims_adg is not None

    def test_interface_shims_adg_class(self):
        """Test InterfaceShimsAdg class exists."""
        from agentic_core import InterfaceShimsAdg

        assert InterfaceShimsAdg is not None

    def test_interface_shims_adg_callable(self):
        """Test interface_shims_adg functions are callable."""
        from agentic_core import validate_interface_shims_adg

        assert callable(validate_interface_shims_adg)
