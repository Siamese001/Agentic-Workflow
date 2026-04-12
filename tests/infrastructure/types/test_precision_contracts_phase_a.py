"""Test PrecisionContractsPhaseA functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPrecisionContractsPhaseA:
    """Test PrecisionContractsPhaseA functionality."""

    def test_precision_contracts_imports(self):
        """Test precision contracts module imports."""
        from infrastructure import precision_contracts

        assert precision_contracts is not None

    def test_precision_contracts_validator(self):
        """Test precision contracts validator exists."""
        from infrastructure.types.precision_contracts import PhaseAValidator

        assert PhaseAValidator is not None

    def test_precision_contracts_check(self):
        """Test precision contracts check function."""
        from infrastructure.types.precision_contracts import check_precision_contracts

        assert callable(check_precision_contracts)
