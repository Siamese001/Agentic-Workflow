"""Test PtcToolContractsTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPtcToolContractsTypesAdg:
    """Test PtcToolContractsTypesAdg functionality."""

    def test_ptc_tool_contracts_types_adg_imports(self):
        """Test ptc_tool_contracts_types_adg module imports."""
        from agentic_core import ptc_tool_contracts_types_adg

        assert ptc_tool_contracts_types_adg is not None

    def test_ptc_tool_contracts_types_adg_class(self):
        """Test PtcToolContractsTypesAdg class exists."""
        from agentic_core import PtcToolContractsTypesAdg

        assert PtcToolContractsTypesAdg is not None

    def test_ptc_tool_contracts_types_adg_callable(self):
        """Test ptc_tool_contracts_types_adg functions are callable."""
        from agentic_core import validate_ptc_tool_contracts_types_adg

        assert callable(validate_ptc_tool_contracts_types_adg)
