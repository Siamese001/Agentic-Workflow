"""Test PolicyStateObserverAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPolicyStateObserverAdg:
    """Test PolicyStateObserverAdg functionality."""

    def test_policy_state_observer_adg_imports(self):
        """Test policy_state_observer_adg module imports."""
        from agentic_core import policy_state_observer_adg

        assert policy_state_observer_adg is not None

    def test_policy_state_observer_adg_class(self):
        """Test PolicyStateObserverAdg class exists."""
        from agentic_core import PolicyStateObserverAdg

        assert PolicyStateObserverAdg is not None

    def test_policy_state_observer_adg_callable(self):
        """Test policy_state_observer_adg functions are callable."""
        from agentic_core import validate_policy_state_observer_adg

        assert callable(validate_policy_state_observer_adg)
