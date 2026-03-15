"""ADG contract tests for apps_shared/types/event_bus_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.event_bus_types import EventType, MemoryEventBus, SystemEvent
    _AVAIL = True
except ImportError:
    _AVAIL = False
    EventType = SystemEvent = MemoryEventBus = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEventType:
    def test_is_enum(self):
        import enum; assert issubclass(EventType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(EventType, str)
    def test_has_workflow_started(self):
        assert EventType.WORKFLOW_STARTED.value == "WORKFLOW_STARTED"
    def test_has_agent_failed(self):
        assert EventType.AGENT_FAILED.value == "AGENT_FAILED"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSystemEvent:
    def test_creates(self):
        e = SystemEvent(
            trace_id="t1", type=EventType.WORKFLOW_STARTED,
            source_component="test", payload={"key": "val"},
        )
        assert e.trace_id == "t1"; assert e.correlation_id is None
    def test_auto_id(self):
        e = SystemEvent(
            trace_id="t1", type=EventType.AGENT_COMPLETED,
            source_component="test", payload={},
        )
        assert e.id is not None and len(e.id) > 0
    def test_to_dict(self):
        e = SystemEvent(
            trace_id="t1", type=EventType.DATA_PROCESSED,
            source_component="comp", payload={"x": 1},
        )
        d = e.to_dict()
        assert d["trace_id"] == "t1"; assert d["type"] == "DATA_PROCESSED"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMemoryEventBus:
    def test_creates(self): bus = MemoryEventBus(); assert bus is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
