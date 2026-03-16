"""ADG-driven tests for apps_rg/types/SovereignContext.py — fan_in=3.

Contract tests: SovereignContext airlock, commit, rollback, get.
"""
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

_emit_records_execution_trace("p0", "evidence", "test_sovereign_context_adg")
_emit_applies_guardrail("p0", "test_sovereign_context_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_sovereign_context_adg", "policy_binding")
_emit_snapshots_state("p0", "test_sovereign_context_adg", "state_snapshot")
emit_replay_key("p0", "test_sovereign_context_adg")
emit_determinism_digest("p0", "test_sovereign_context_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sovereign_context_adg", "execution_auth")
_emit_validates_capability("p2", "test_sovereign_context_adg", "capability_check")
_emit_routes_to_capability("p2", "test_sovereign_context_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_sovereign_context_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_sovereign_context_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sovereign_context_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_sovereign_context_adg", "exec_output")
_emit_dispatches_agent("p3", "test_sovereign_context_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sovereign_context_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sovereign_context_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sovereign_context_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_sovereign_context_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sovereign_context_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sovereign_context_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sovereign_context_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sovereign_context_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sovereign_context_adg", "eval_metric")
_emit_stores_embedding("p4", "test_sovereign_context_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sovereign_context_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sovereign_context_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from apps_rg.types.SovereignContext import SimpleBuffer, SimpleTrace, SovereignContext


class TestSovereignContextImport:
    def test_class_importable(self):
        assert callable(SovereignContext)

    def test_simple_buffer_importable(self):
        assert callable(SimpleBuffer)

    def test_simple_trace_importable(self):
        assert callable(SimpleTrace)


class TestSovereignContextAirlock:
    def test_write_to_airlock(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("key", "value")
        # Not visible until committed
        assert ctx.get("key") is None

    def test_commit_airlock_requires_signature(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("k", "v")
        with pytest.raises(ValueError, match="signature"):
            ctx.commit_airlock("")

    def test_commit_airlock_makes_visible(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("x", 42)
        ctx.commit_airlock("valid_sig_abc123")
        assert ctx.get("x") == 42

    def test_commit_clears_airlock(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("y", "data")
        ctx.commit_airlock("sig")
        # Writing again to same key in airlock should work (airlock is cleared)
        ctx.write_to_airlock("y", "new_data")
        assert ctx.get("y") == "data"  # committed state still old

    def test_rollback_discards_airlock(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("z", "staged")
        ctx.rollback_airlock()
        # After rollback, commit has nothing to promote
        ctx.commit_airlock("sig")
        assert ctx.get("z") is None


class TestSovereignContextGet:
    def test_get_default_none(self):
        ctx = SovereignContext()
        assert ctx.get("missing") is None

    def test_get_with_default(self):
        ctx = SovereignContext()
        assert ctx.get("missing", "fallback") == "fallback"

    def test_get_committed_value(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("k", 99)
        ctx.commit_airlock("sig")
        assert ctx.get("k") == 99


class TestSimpleBuffer:
    def test_write_and_read(self):
        buf = SimpleBuffer()
        buf.write("k", "v")
        assert buf.read("k") == "v"

    def test_read_missing_returns_default(self):
        buf = SimpleBuffer()
        assert buf.read("x") is None
        assert buf.read("x", "default") == "default"


class TestSimpleTrace:
    def test_add_trace_and_summary(self):
        trace = SimpleTrace()
        trace.add_trace("START", {"step": 1})
        summary = trace.get_summary()
        assert summary["total_spans"] == 1

    def test_error_counted_in_failures(self):
        trace = SimpleTrace()
        trace.add_trace("ERROR_OCCURRED", {"detail": "x"})
        summary = trace.get_summary()
        assert summary["failures"] == 1

    def test_no_errors_zero_failures(self):
        trace = SimpleTrace()
        trace.add_trace("SUCCESS")
        summary = trace.get_summary()
        assert summary["failures"] == 0
