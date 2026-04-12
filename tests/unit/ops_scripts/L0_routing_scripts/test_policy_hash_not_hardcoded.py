"""Test PolicyHashNotHardcoded functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPolicyHashNotHardcoded:
    """Test PolicyHashNotHardcoded functionality."""

    def test_policy_hash_not_hardcoded_imports(self):
        """Test policy_hash_not_hardcoded module imports."""
        from agentic_core import policy_hash_not_hardcoded

        assert policy_hash_not_hardcoded is not None

    def test_policy_hash_not_hardcoded_class(self):
        """Test PolicyHashNotHardcoded class exists."""
        from agentic_core import PolicyHashNotHardcoded

        assert PolicyHashNotHardcoded is not None

    def test_policy_hash_not_hardcoded_callable(self):
        """Test policy_hash_not_hardcoded functions are callable."""
        from agentic_core import validate_policy_hash_not_hardcoded

        assert callable(validate_policy_hash_not_hardcoded)
