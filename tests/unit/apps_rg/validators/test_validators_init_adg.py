"""Test ValidatorsInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestValidatorsInitAdg:
    """Test ValidatorsInitAdg functionality."""

    def test_validators_init_adg_imports(self):
        """Test validators_init_adg module imports."""
        from agentic_core import validators_init_adg
        assert validators_init_adg is not None

    def test_validators_init_adg_class(self):
        """Test ValidatorsInitAdg class exists."""
        from agentic_core import ValidatorsInitAdg
        assert ValidatorsInitAdg is not None

    def test_validators_init_adg_callable(self):
        """Test validators_init_adg functions are callable."""
        from agentic_core import validate_validators_init_adg
        assert callable(validate_validators_init_adg)
