"""Test ValidatorsAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestValidatorsAdg:
    """Test ValidatorsAdg functionality."""

    def test_validators_adg_imports(self):
        """Test validators_adg module imports."""
        from agentic_core import validators_adg

        assert validators_adg is not None

    def test_validators_adg_class(self):
        """Test ValidatorsAdg class exists."""
        from agentic_core import ValidatorsAdg

        assert ValidatorsAdg is not None

    def test_validators_adg_callable(self):
        """Test validators_adg functions are callable."""
        from agentic_core import validate_validators_adg

        assert callable(validate_validators_adg)
