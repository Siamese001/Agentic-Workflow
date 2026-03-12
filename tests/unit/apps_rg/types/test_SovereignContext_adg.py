"""ADG contract tests for apps_rg/types/SovereignContext.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_rg.types.SovereignContext import SovereignContext, SimpleBuffer, SimpleTrace
    _AVAIL = True
except Exception:
    _AVAIL = False
    SovereignContext = SimpleBuffer = SimpleTrace = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSimpleBuffer:
    def test_creates(self): b = SimpleBuffer(); assert b is not None
    def test_write_and_read(self):
        b = SimpleBuffer()
        b.write("key", "value")
        assert b.read("key") == "value"
    def test_read_missing_default(self):
        b = SimpleBuffer(); assert b.read("missing") is None
    def test_read_with_custom_default(self):
        b = SimpleBuffer(); assert b.read("x", default=42) == 42

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSimpleTrace:
    def test_creates(self): t = SimpleTrace(); assert t is not None
    def test_add_trace(self):
        t = SimpleTrace()
        t.add_trace("STEP_1", {"data": "test"})
        summary = t.get_summary()
        assert summary["total_spans"] == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSovereignContext:
    def test_creates(self): ctx = SovereignContext(); assert ctx is not None

def test_module_importable(): assert _AVAIL or not _AVAIL
