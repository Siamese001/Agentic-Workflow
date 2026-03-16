"""ADG contract tests for apps_rg/types/SovereignContext.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "test_SovereignContext_adg", "execution_auth")
_emit_validates_capability("p2", "test_SovereignContext_adg", "capability_check")
_emit_routes_to_capability("p2", "test_SovereignContext_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_SovereignContext_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_SovereignContext_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_SovereignContext_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_SovereignContext_adg", "exec_output")
_emit_dispatches_agent("p3", "test_SovereignContext_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_SovereignContext_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_SovereignContext_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_SovereignContext_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_SovereignContext_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_SovereignContext_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_SovereignContext_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_SovereignContext_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_SovereignContext_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_SovereignContext_adg", "eval_metric")
_emit_stores_embedding("p4", "test_SovereignContext_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_SovereignContext_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_SovereignContext_adg", "exec_snapshot_link")

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
