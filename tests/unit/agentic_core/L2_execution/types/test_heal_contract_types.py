"""Test HealContractTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealContractTypes:
    """Test HealContractTypes functionality."""

    def test_heal_contract_types_imports(self):
        """Test heal_contract_types module imports."""
        from agentic_core import heal_contract_types

        assert heal_contract_types is not None

    def test_heal_contract_types_class(self):
        """Test HealContractTypes class exists."""
        from agentic_core import HealContractTypes

        assert HealContractTypes is not None

    def test_heal_contract_types_callable(self):
        """Test heal_contract_types functions are callable."""
        from agentic_core import validate_heal_contract_types

        assert callable(validate_heal_contract_types)
