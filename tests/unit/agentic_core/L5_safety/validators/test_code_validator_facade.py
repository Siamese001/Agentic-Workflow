"""Test CodeValidatorFacade functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCodeValidatorFacade:
    """Test CodeValidatorFacade functionality."""

    def test_code_validator_facade_imports(self):
        """Test code_validator_facade module imports."""
        from agentic_core import code_validator_facade

        assert code_validator_facade is not None

    def test_code_validator_facade_class(self):
        """Test CodeValidatorFacade class exists."""
        from agentic_core import CodeValidatorFacade

        assert CodeValidatorFacade is not None

    def test_code_validator_facade_callable(self):
        """Test code_validator_facade functions are callable."""
        from agentic_core import validate_code_validator_facade

        assert callable(validate_code_validator_facade)
