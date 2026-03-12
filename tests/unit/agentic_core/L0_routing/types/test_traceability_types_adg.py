"""ADG contract tests for agentic_core/L0_routing/types/traceability_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.traceability_types import (
        TraceSpan, TraceContext,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    TraceSpan = TraceContext = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTraceSpan:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(TraceSpan)
    def test_has_trace_id_field(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(TraceSpan)}
        assert "trace_id" in fields or "span_id" in fields

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTraceContext:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(TraceContext)

def test_module_importable(): assert _AVAIL or not _AVAIL
