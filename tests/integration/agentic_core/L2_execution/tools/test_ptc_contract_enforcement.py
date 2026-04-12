"""Test PtcContractEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPtcContractEnforcement:
    """Test PtcContractEnforcement functionality."""

    def test_ptc_contract_enforcement_imports(self):
        """Test ptc_contract_enforcement module imports."""
        from agentic_core import ptc_contract_enforcement

        assert ptc_contract_enforcement is not None

    def test_ptc_contract_enforcement_class(self):
        """Test PtcContractEnforcement class exists."""
        from agentic_core import PtcContractEnforcement

        assert PtcContractEnforcement is not None

    def test_ptc_contract_enforcement_callable(self):
        """Test ptc_contract_enforcement functions are callable."""
        from agentic_core import validate_ptc_contract_enforcement

        assert callable(validate_ptc_contract_enforcement)
