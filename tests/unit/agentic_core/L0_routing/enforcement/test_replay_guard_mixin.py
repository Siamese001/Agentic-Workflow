"""Test ReplayGuardMixin functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReplayGuardMixin:
    """Test ReplayGuardMixin functionality."""

    def test_replay_guard_mixin_imports(self):
        """Test replay_guard_mixin module imports."""
        from agentic_core import replay_guard_mixin

        assert replay_guard_mixin is not None

    def test_replay_guard_mixin_class(self):
        """Test ReplayGuardMixin class exists."""
        from agentic_core import ReplayGuardMixin

        assert ReplayGuardMixin is not None

    def test_replay_guard_mixin_callable(self):
        """Test replay_guard_mixin functions are callable."""
        from agentic_core import validate_replay_guard_mixin

        assert callable(validate_replay_guard_mixin)
