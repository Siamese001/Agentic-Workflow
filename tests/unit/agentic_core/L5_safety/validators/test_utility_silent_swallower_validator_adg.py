"""Test UtilitySilentSwallowerValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestUtilitySilentSwallowerValidatorAdg:
    """Test UtilitySilentSwallowerValidatorAdg functionality."""

    def test_utility_silent_swallower_validator_adg_imports(self):
        """Test utility_silent_swallower_validator_adg module imports."""
        from agentic_core import utility_silent_swallower_validator_adg

        assert utility_silent_swallower_validator_adg is not None

    def test_utility_silent_swallower_validator_adg_class(self):
        """Test UtilitySilentSwallowerValidatorAdg class exists."""
        from agentic_core import UtilitySilentSwallowerValidatorAdg

        assert UtilitySilentSwallowerValidatorAdg is not None

    def test_utility_silent_swallower_validator_adg_callable(self):
        """Test utility_silent_swallower_validator_adg functions are callable."""
        from agentic_core import validate_utility_silent_swallower_validator_adg

        assert callable(validate_utility_silent_swallower_validator_adg)
