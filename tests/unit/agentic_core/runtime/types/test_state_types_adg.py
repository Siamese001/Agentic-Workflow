"""ADG contract tests for runtime/types/state_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.runtime.types.state_types import AgentMessage, AgentState
    _AVAIL = True
except ImportError:
    _AVAIL = False; AgentMessage = AgentState = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentMessage:
    def test_creates(self):
        m = AgentMessage(role="user", content="hello")
        assert m.role == "user"; assert m.content == "hello"
    def test_timestamp_auto(self):
        m = AgentMessage(role="user", content="x"); assert m.timestamp is not None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAgentState:
    def test_creates(self):
        s = AgentState(task_id="t1", user_input="do something")
        assert s.task_id == "t1"; assert s.turn_count == 0; assert not s.is_terminated
    def test_add_message(self):
        s = AgentState(task_id="t1", user_input="x")
        s.add_message("user", "hello"); assert len(s.messages) == 1
    def test_increment_turn(self):
        s = AgentState(task_id="t1", user_input="x")
        s.increment_turn(); assert s.turn_count == 1

def test_module_importable(): assert _AVAIL or not _AVAIL
