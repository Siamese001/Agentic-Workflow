"""Test BlackboardStore functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBlackboardStore:
    """Test BlackboardStore functionality."""

    def test_blackboard_store_imports(self):
        """Test blackboard store module imports."""
        from agentic_core.L4_state import blackboard_store
        assert blackboard_store is not None

    def test_blackboard_store_class(self):
        """Test blackboard store class exists."""
        from agentic_core.L4_state.blackboard_store import BlackboardStore
        assert BlackboardStore is not None

    def test_store_blackboard(self):
        """Test store blackboard function."""
        from agentic_core.L4_state.blackboard_store import store_blackboard
        assert callable(store_blackboard)
