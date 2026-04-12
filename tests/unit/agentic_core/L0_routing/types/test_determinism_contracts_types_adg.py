"""Test DeterminismContractsTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterminismContractsTypesAdg:
    """Test DeterminismContractsTypesAdg functionality."""

    def test_determinism_contracts_types_adg_imports(self):
        """Test determinism_contracts_types_adg module imports."""
        from agentic_core import determinism_contracts_types_adg

        assert determinism_contracts_types_adg is not None

    def test_determinism_contracts_types_adg_class(self):
        """Test DeterminismContractsTypesAdg class exists."""
        from agentic_core import DeterminismContractsTypesAdg

        assert DeterminismContractsTypesAdg is not None

    def test_determinism_contracts_types_adg_callable(self):
        """Test determinism_contracts_types_adg functions are callable."""
        from agentic_core import validate_determinism_contracts_types_adg

        assert callable(validate_determinism_contracts_types_adg)
