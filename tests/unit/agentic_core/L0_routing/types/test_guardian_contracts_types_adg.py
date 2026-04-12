"""Test GuardianContractsTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianContractsTypesAdg:
    """Test GuardianContractsTypesAdg functionality."""

    def test_guardian_contracts_types_adg_imports(self):
        """Test guardian_contracts_types_adg module imports."""
        from agentic_core import guardian_contracts_types_adg

        assert guardian_contracts_types_adg is not None

    def test_guardian_contracts_types_adg_class(self):
        """Test GuardianContractsTypesAdg class exists."""
        from agentic_core import GuardianContractsTypesAdg

        assert GuardianContractsTypesAdg is not None

    def test_guardian_contracts_types_adg_callable(self):
        """Test guardian_contracts_types_adg functions are callable."""
        from agentic_core import validate_guardian_contracts_types_adg

        assert callable(validate_guardian_contracts_types_adg)
