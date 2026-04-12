"""Test UserFlowE2e functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestUserFlowE2e:
    """Test UserFlowE2e functionality."""

    def test_user_flow_e2e_imports(self):
        """Test user_flow_e2e module imports."""
        from agentic_core import user_flow_e2e

        assert user_flow_e2e is not None

    def test_user_flow_e2e_class(self):
        """Test UserFlowE2e class exists."""
        from agentic_core import UserFlowE2e

        assert UserFlowE2e is not None

    def test_user_flow_e2e_callable(self):
        """Test user_flow_e2e functions are callable."""
        from agentic_core import validate_user_flow_e2e

        assert callable(validate_user_flow_e2e)
