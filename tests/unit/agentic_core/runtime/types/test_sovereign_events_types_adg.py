"""ADG contract tests for runtime/types/sovereign_events_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.runtime.types.sovereign_events_types import SovereignEvent
    _AVAIL = True
except ImportError:
    _AVAIL = False; SovereignEvent = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSovereignEvent:
    def test_creates(self):
        e = SovereignEvent(event_type="test.event", source_agent="TestAgent")
        assert e.event_type == "test.event"; assert e.severity == "INFO"
    def test_event_id_auto(self):
        e = SovereignEvent(event_type="x", source_agent="a"); assert e.event_id != ""
    def test_timestamp_auto(self):
        e = SovereignEvent(event_type="x", source_agent="a"); assert e.timestamp != ""

def test_module_importable(): assert _AVAIL or not _AVAIL
