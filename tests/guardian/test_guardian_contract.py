"""Test GuardianContract functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianContract:
    """Test GuardianContract functionality."""

    def test_guardian_contract_imports(self):
        """Test guardian_contract module imports."""
        from agentic_core import guardian_contract
        assert guardian_contract is not None

    def test_guardian_contract_class(self):
        """Test GuardianContract class exists."""
        from agentic_core import GuardianContract
        assert GuardianContract is not None

    def test_guardian_contract_callable(self):
        """Test guardian_contract functions are callable."""
        from agentic_core import validate_guardian_contract
        assert callable(validate_guardian_contract)
