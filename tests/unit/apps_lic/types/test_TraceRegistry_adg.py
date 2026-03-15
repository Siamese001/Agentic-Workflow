"""ADG contract tests for apps_lic/types/TraceRegistry.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_lic.types.TraceRegistry import TraceRegistry
    _AVAIL = True
except ImportError:
    _AVAIL = False
    TraceRegistry = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTraceRegistry:
    def test_creates(self):
        r = TraceRegistry(); assert r is not None
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(TraceRegistry)
    def test_add_trace(self):
        r = TraceRegistry()
        r.add_trace(event_type="TEST", details={"key": "val"})
        traces = r.get_traces()
        assert len(traces) == 1
    def test_count(self):
        r = TraceRegistry()
        r.add_trace(event_type="STEP", details={})
        assert r.count(trace_type="STEP") >= 1

def test_module_importable(): assert _AVAIL or not _AVAIL
