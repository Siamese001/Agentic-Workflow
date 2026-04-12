"""Test PtcContractAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPtcContractAdg:
    """Test PtcContractAdg functionality."""

    def test_ptc_contract_adg_imports(self):
        """Test ptc_contract_adg module imports."""
        from agentic_core import ptc_contract_adg

        assert ptc_contract_adg is not None

    def test_ptc_contract_adg_class(self):
        """Test PtcContractAdg class exists."""
        from agentic_core import PtcContractAdg

        assert PtcContractAdg is not None

    def test_ptc_contract_adg_callable(self):
        """Test ptc_contract_adg functions are callable."""
        from agentic_core import validate_ptc_contract_adg

        assert callable(validate_ptc_contract_adg)
