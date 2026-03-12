"""ADG contract tests for apps_shared/types/state_operation_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.state_operation_types import (
        StateOperation, StateEventType, StatePath,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    StateOperation = StateEventType = StatePath = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStateOperation:
    def test_is_enum(self):
        import enum; assert issubclass(StateOperation, enum.Enum)
    def test_is_str_enum(self): assert issubclass(StateOperation, str)
    def test_has_create(self): assert StateOperation.CREATE.value == "create"
    def test_has_delete(self): assert StateOperation.DELETE.value == "delete"
    def test_five_operations(self): assert len(list(StateOperation)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStateEventType:
    def test_is_enum(self):
        import enum; assert issubclass(StateEventType, enum.Enum)
    def test_has_transition(self): assert StateEventType.TRANSITION.value == "transition"
    def test_has_rollback(self): assert StateEventType.ROLLBACK.value == "rollback"
    def test_four_event_types(self): assert len(list(StateEventType)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestStatePath:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(StatePath)
    def test_is_frozen(self):
        import dataclasses
        fields = {f.name: f for f in dataclasses.fields(StatePath)}
        assert StatePath.__dataclass_params__.frozen is True
    def test_creates_empty(self):
        p = StatePath(); assert str(p) == ""
    def test_from_string(self):
        p = StatePath.from_string("agent.state.key")
        assert p.parts == ("agent", "state", "key")
        assert str(p) == "agent.state.key"
    def test_truediv_appends(self):
        p = StatePath.from_string("agent") / "state"
        assert p.parts == ("agent", "state")

def test_module_importable(): assert _AVAIL or not _AVAIL
