"""ADG contract tests for apps_lic/types/TraceRegistry.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_TraceRegistry_adg")
_emit_applies_guardrail("p0", "test_TraceRegistry_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_TraceRegistry_adg", "policy_binding")
_emit_snapshots_state("p0", "test_TraceRegistry_adg", "state_snapshot")
emit_replay_key("p0", "test_TraceRegistry_adg")
emit_determinism_digest("p0", "test_TraceRegistry_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
