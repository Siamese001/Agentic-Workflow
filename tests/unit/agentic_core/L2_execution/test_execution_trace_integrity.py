"""Addendum 1.1: ExecutionTrace.validate_completeness() tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError
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

_emit_records_execution_trace("p0", "evidence", "test_execution_trace_integrity")
_emit_applies_guardrail("p0", "test_execution_trace_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_trace_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_execution_trace_integrity", "state_snapshot")
emit_replay_key("p0", "test_execution_trace_integrity")
emit_determinism_digest("p0", "test_execution_trace_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_trace_integrity", "execution_auth")
_emit_validates_capability("p2", "test_execution_trace_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_execution_trace_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_trace_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_trace_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_trace_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_trace_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_execution_trace_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_trace_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_trace_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_trace_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_trace_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_trace_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_trace_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_trace_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_trace_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_trace_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_execution_trace_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_trace_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_trace_integrity", "exec_snapshot_link")


def _complete_trace() -> ExecutionTrace:
    b = ExecutionTraceBuilder("trace-001", "ip-001")
    b.set_governed_payload("abc123")
    b.set_llm_response("some response text")
    b.set_hash_chain_root("root-hash-abc")
    b.set_validation_decision("PASS")
    b.set_transcript(b"tool transcript bytes")
    return b.seal()


class TestValidateCompleteness:
    def test_complete_trace_passes(self):
        trace = _complete_trace()
        trace.validate_completeness()

    def test_empty_governed_payload_raises(self):
        b = ExecutionTraceBuilder("trace-002", "ip-002")
        b.set_llm_response("response")
        b.set_hash_chain_root("root")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="governed_payload_hash"):
            trace.validate_completeness()

    def test_empty_llm_response_hash_raises(self):
        b = ExecutionTraceBuilder("trace-003", "ip-003")
        b.set_governed_payload("abc")
        b.set_hash_chain_root("root")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="llm_response_hash"):
            trace.validate_completeness()

    def test_empty_hash_chain_root_raises(self):
        b = ExecutionTraceBuilder("trace-004", "ip-004")
        b.set_governed_payload("abc")
        b.set_llm_response("resp")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="hash_chain_root"):
            trace.validate_completeness()

    def test_negative_no_error_on_full_trace(self):
        """Negative control: error must NOT be raised on a complete trace."""
        trace = _complete_trace()
        raised = False
        try:
            trace.validate_completeness()
        except ExecutionTraceIntegrityError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised

    def test_multiple_missing_fields_listed(self):
        b = ExecutionTraceBuilder("trace-005", "ip-005")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError) as exc_info:
            trace.validate_completeness()
        msg = str(exc_info.value)
        assert "governed_payload_hash" in msg or "llm_response_hash" in msg
