"""Test GravityValidatorHardened functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGravityValidatorHardened:
    """Test GravityValidatorHardened functionality."""

    def test_gravity_validator_hardened_imports(self):
        """Test gravity_validator_hardened module imports."""
        from agentic_core import gravity_validator_hardened
        assert gravity_validator_hardened is not None

    def test_gravity_validator_hardened_class(self):
        """Test GravityValidatorHardened class exists."""
        from agentic_core import GravityValidatorHardened
        assert GravityValidatorHardened is not None

    def test_gravity_validator_hardened_callable(self):
        """Test gravity_validator_hardened functions are callable."""
        from agentic_core import validate_gravity_validator_hardened
        assert callable(validate_gravity_validator_hardened)
