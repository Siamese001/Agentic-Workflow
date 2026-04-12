"""Test EphemeralVmTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEphemeralVmTypesAdg:
    """Test EphemeralVmTypesAdg functionality."""

    def test_ephemeral_vm_types_adg_imports(self):
        """Test ephemeral_vm_types_adg module imports."""
        from agentic_core import ephemeral_vm_types_adg

        assert ephemeral_vm_types_adg is not None

    def test_ephemeral_vm_types_adg_class(self):
        """Test EphemeralVmTypesAdg class exists."""
        from agentic_core import EphemeralVmTypesAdg

        assert EphemeralVmTypesAdg is not None

    def test_ephemeral_vm_types_adg_callable(self):
        """Test ephemeral_vm_types_adg functions are callable."""
        from agentic_core import validate_ephemeral_vm_types_adg

        assert callable(validate_ephemeral_vm_types_adg)
