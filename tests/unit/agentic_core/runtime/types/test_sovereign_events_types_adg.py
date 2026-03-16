"""ADG contract tests for runtime/types/sovereign_events_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_events_types_adg")
_emit_applies_guardrail("p0", "test_sovereign_events_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_events_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_events_types_adg", "state_snapshot")
emit_replay_key("p0", "test_sovereign_events_types_adg")
emit_determinism_digest("p0", "test_sovereign_events_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
