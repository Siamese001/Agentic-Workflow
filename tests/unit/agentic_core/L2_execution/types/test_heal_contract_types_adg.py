"""Test HealContractTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealContractTypesAdg:
    """Test HealContractTypesAdg functionality."""

    def test_heal_contract_types_adg_imports(self):
        """Test heal_contract_types_adg module imports."""
        from agentic_core import heal_contract_types_adg

        assert heal_contract_types_adg is not None

    def test_heal_contract_types_adg_class(self):
        """Test HealContractTypesAdg class exists."""
        from agentic_core import HealContractTypesAdg

        assert HealContractTypesAdg is not None

    def test_heal_contract_types_adg_callable(self):
        """Test heal_contract_types_adg functions are callable."""
        from agentic_core import validate_heal_contract_types_adg

        assert callable(validate_heal_contract_types_adg)
