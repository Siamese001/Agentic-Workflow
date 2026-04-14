"""Test BlackboardStore functionality."""

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
blackboard_store = import_or_skip(
    "agentic_core.L4_state.blackboard_store",
    reason="blackboard_store unavailable for BlackboardStore tests",
)
BlackboardStore = blackboard_store.BlackboardStore
store_blackboard = blackboard_store.store_blackboard


@pytest.mark.unit
class TestBlackboardStore:
    """Test BlackboardStore functionality."""

    def test_blackboard_store_imports(self):
        assert blackboard_store is not None

    def test_blackboard_store_class(self):
        assert BlackboardStore is not None

    def test_store_blackboard(self):
        assert callable(store_blackboard)
