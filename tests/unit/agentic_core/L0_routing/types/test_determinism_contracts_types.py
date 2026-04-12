"""Test DeterminismContractsTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDeterminismContractsTypes:
    """Test DeterminismContractsTypes functionality."""

    def test_determinism_contracts_types_imports(self):
        """Test determinism_contracts_types module imports."""
        from agentic_core import determinism_contracts_types

        assert determinism_contracts_types is not None

    def test_determinism_contracts_types_class(self):
        """Test DeterminismContractsTypes class exists."""
        from agentic_core import DeterminismContractsTypes

        assert DeterminismContractsTypes is not None

    def test_determinism_contracts_types_callable(self):
        """Test determinism_contracts_types functions are callable."""
        from agentic_core import validate_determinism_contracts_types

        assert callable(validate_determinism_contracts_types)
