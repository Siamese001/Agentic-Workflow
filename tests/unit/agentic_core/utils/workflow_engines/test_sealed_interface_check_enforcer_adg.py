"""Test SealedInterfaceCheckEnforcerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSealedInterfaceCheckEnforcerAdg:
    """Test SealedInterfaceCheckEnforcerAdg functionality."""

    def test_sealed_interface_check_enforcer_adg_imports(self):
        """Test sealed_interface_check_enforcer_adg module imports."""
        from agentic_core import sealed_interface_check_enforcer_adg

        assert sealed_interface_check_enforcer_adg is not None

    def test_sealed_interface_check_enforcer_adg_class(self):
        """Test SealedInterfaceCheckEnforcerAdg class exists."""
        from agentic_core import SealedInterfaceCheckEnforcerAdg

        assert SealedInterfaceCheckEnforcerAdg is not None

    def test_sealed_interface_check_enforcer_adg_callable(self):
        """Test sealed_interface_check_enforcer_adg functions are callable."""
        from agentic_core import validate_sealed_interface_check_enforcer_adg

        assert callable(validate_sealed_interface_check_enforcer_adg)
