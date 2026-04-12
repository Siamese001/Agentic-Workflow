"""Test ContextValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestContextValidatorAdg:
    """Test ContextValidatorAdg functionality."""

    def test_context_validator_adg_imports(self):
        """Test context_validator_adg module imports."""
        from agentic_core import context_validator_adg

        assert context_validator_adg is not None

    def test_context_validator_adg_class(self):
        """Test ContextValidatorAdg class exists."""
        from agentic_core import ContextValidatorAdg

        assert ContextValidatorAdg is not None

    def test_context_validator_adg_callable(self):
        """Test context_validator_adg functions are callable."""
        from agentic_core import validate_context_validator_adg

        assert callable(validate_context_validator_adg)
