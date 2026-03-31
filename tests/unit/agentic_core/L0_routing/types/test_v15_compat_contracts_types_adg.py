"""Test V15CompatContractsTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestV15CompatContractsTypesAdg:
    """Test V15CompatContractsTypesAdg functionality."""

    def test_v15_compat_contracts_types_adg_imports(self):
        """Test v15_compat_contracts_types_adg module imports."""
        from agentic_core import v15_compat_contracts_types_adg
        assert v15_compat_contracts_types_adg is not None

    def test_v15_compat_contracts_types_adg_class(self):
        """Test V15CompatContractsTypesAdg class exists."""
        from agentic_core import V15CompatContractsTypesAdg
        assert V15CompatContractsTypesAdg is not None

    def test_v15_compat_contracts_types_adg_callable(self):
        """Test v15_compat_contracts_types_adg functions are callable."""
        from agentic_core import validate_v15_compat_contracts_types_adg
        assert callable(validate_v15_compat_contracts_types_adg)
