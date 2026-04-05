"""Test CheckSchemaPolicyValidatorAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCheckSchemaPolicyValidatorAdg:
    """Test CheckSchemaPolicyValidatorAdg functionality."""

    def test_check_schema_policy_validator_adg_imports(self):
        """Test check_schema_policy_validator_adg module imports."""
        from agentic_core import check_schema_policy_validator_adg
        assert check_schema_policy_validator_adg is not None

    def test_check_schema_policy_validator_adg_class(self):
        """Test CheckSchemaPolicyValidatorAdg class exists."""
        from agentic_core import CheckSchemaPolicyValidatorAdg
        assert CheckSchemaPolicyValidatorAdg is not None

    def test_check_schema_policy_validator_adg_callable(self):
        """Test check_schema_policy_validator_adg functions are callable."""
        from agentic_core import validate_check_schema_policy_validator_adg
        assert callable(validate_check_schema_policy_validator_adg)
