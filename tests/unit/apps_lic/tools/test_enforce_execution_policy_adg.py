"""Test EnforceExecutionPolicyAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEnforceExecutionPolicyAdg:
    """Test EnforceExecutionPolicyAdg functionality."""

    def test_enforce_execution_policy_adg_imports(self):
        """Test enforce_execution_policy_adg module imports."""
        from agentic_core import enforce_execution_policy_adg
        assert enforce_execution_policy_adg is not None

    def test_enforce_execution_policy_adg_class(self):
        """Test EnforceExecutionPolicyAdg class exists."""
        from agentic_core import EnforceExecutionPolicyAdg
        assert EnforceExecutionPolicyAdg is not None

    def test_enforce_execution_policy_adg_callable(self):
        """Test enforce_execution_policy_adg functions are callable."""
        from agentic_core import validate_enforce_execution_policy_adg
        assert callable(validate_enforce_execution_policy_adg)
