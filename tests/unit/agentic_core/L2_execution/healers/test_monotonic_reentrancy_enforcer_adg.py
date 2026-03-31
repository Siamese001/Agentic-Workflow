"""Test MonotonicReentrancyEnforcerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMonotonicReentrancyEnforcerAdg:
    """Test MonotonicReentrancyEnforcerAdg functionality."""

    def test_monotonic_reentrancy_enforcer_adg_imports(self):
        """Test monotonic_reentrancy_enforcer_adg module imports."""
        from agentic_core import monotonic_reentrancy_enforcer_adg
        assert monotonic_reentrancy_enforcer_adg is not None

    def test_monotonic_reentrancy_enforcer_adg_class(self):
        """Test MonotonicReentrancyEnforcerAdg class exists."""
        from agentic_core import MonotonicReentrancyEnforcerAdg
        assert MonotonicReentrancyEnforcerAdg is not None

    def test_monotonic_reentrancy_enforcer_adg_callable(self):
        """Test monotonic_reentrancy_enforcer_adg functions are callable."""
        from agentic_core import validate_monotonic_reentrancy_enforcer_adg
        assert callable(validate_monotonic_reentrancy_enforcer_adg)
