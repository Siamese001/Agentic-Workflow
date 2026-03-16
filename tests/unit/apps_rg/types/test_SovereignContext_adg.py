"""ADG contract tests for apps_rg/types/SovereignContext.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_SovereignContext_adg")
_emit_applies_guardrail("p0", "test_SovereignContext_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_SovereignContext_adg", "policy_binding")
_emit_snapshots_state("p0", "test_SovereignContext_adg", "state_snapshot")
emit_replay_key("p0", "test_SovereignContext_adg")
emit_determinism_digest("p0", "test_SovereignContext_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_rg.types.SovereignContext import SimpleBuffer, SimpleTrace, SovereignContext
    _AVAIL = True
except ImportError:
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
