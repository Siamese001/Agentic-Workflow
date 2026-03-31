"""Test ContractCompatibility functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestContractCompatibility:
    """Test ContractCompatibility functionality."""

    def test_contract_compatibility_imports(self):
        """Test contract_compatibility module imports."""
        from agentic_core import contract_compatibility
        assert contract_compatibility is not None

    def test_contract_compatibility_class(self):
        """Test ContractCompatibility class exists."""
        from agentic_core import ContractCompatibility
        assert ContractCompatibility is not None

    def test_contract_compatibility_callable(self):
        """Test contract_compatibility functions are callable."""
        from agentic_core import validate_contract_compatibility
        assert callable(validate_contract_compatibility)
