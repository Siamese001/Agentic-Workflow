"""Test CapabilityContracts functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCapabilityContracts:
    """Test CapabilityContracts functionality."""

    def test_capability_contracts_imports(self):
        """Test capability contracts module imports."""
        from agentic_core import capability_contracts
        assert capability_contracts is not None

    def test_capability_contract_class(self):
        """Test capability contract class exists."""
        from agentic_core.capability_contracts import CapabilityContract
        assert CapabilityContract is not None

    def test_validate_capability(self):
        """Test validate capability function."""
        from agentic_core.capability_contracts import validate_capability
        assert callable(validate_capability)
