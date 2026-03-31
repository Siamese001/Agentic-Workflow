"""Test PolicyPackValidator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPolicyPackValidator:
    """Test PolicyPackValidator functionality."""

    def test_policy_pack_validator_imports(self):
        """Test policy_pack_validator module imports."""
        from agentic_core import policy_pack_validator
        assert policy_pack_validator is not None

    def test_policy_pack_validator_class(self):
        """Test PolicyPackValidator class exists."""
        from agentic_core import PolicyPackValidator
        assert PolicyPackValidator is not None

    def test_policy_pack_validator_callable(self):
        """Test policy_pack_validator functions are callable."""
        from agentic_core import validate_policy_pack_validator
        assert callable(validate_policy_pack_validator)
