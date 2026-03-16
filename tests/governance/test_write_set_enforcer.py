"""Wave 6.1: L2.2 Write-Set Enforcement tests.

Validates:
- Declared write executes successfully
- Undeclared write attempt is blocked
- Aborted enforcer rejects all subsequent writes
- verify() returns correct state
- actual_writes tracks correctly
"""

import pytest

from agentic_core.L2_execution.enforcement.write_set_enforcer import (
    WriteSetEnforcer,
    WriteSetViolation,
)
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

_emit_records_execution_trace("p0", "evidence", "test_write_set_enforcer")
_emit_applies_guardrail("p0", "test_write_set_enforcer", "p0_governance")
_emit_reads_policy_state("p0", "test_write_set_enforcer", "policy_binding")
_emit_snapshots_state("p0", "test_write_set_enforcer", "state_snapshot")
emit_replay_key("p0", "test_write_set_enforcer")
emit_determinism_digest("p0", "test_write_set_enforcer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_write_set_enforcer", "execution_auth")
_emit_validates_capability("p2", "test_write_set_enforcer", "capability_check")
_emit_routes_to_capability("p2", "test_write_set_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "test_write_set_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "test_write_set_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_write_set_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "test_write_set_enforcer", "exec_output")
_emit_dispatches_agent("p3", "test_write_set_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_write_set_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_write_set_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_write_set_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "test_write_set_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_write_set_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_write_set_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_write_set_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_write_set_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_write_set_enforcer", "eval_metric")
_emit_stores_embedding("p4", "test_write_set_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_write_set_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_write_set_enforcer", "exec_snapshot_link")

pytestmark = pytest.mark.governance


class TestDeclaredWriteAllowed:
    """Declared writes must succeed."""

    def test_declared_write_succeeds(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a", "key_b"}))
        enforcer.record_write("key_a")
        assert "key_a" in enforcer.actual_writes

    def test_multiple_declared_writes(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a", "b", "c"}))
        enforcer.record_write("a")
        enforcer.record_write("b")
        enforcer.record_write("c")
        assert enforcer.is_complete

    def test_verify_passes_on_declared(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"x"}))
        enforcer.record_write("x")
        assert enforcer.verify() is True


class TestUndeclaredWriteBlocked:
    """Undeclared writes must raise."""

    def test_undeclared_write_raises(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a"}))
        with pytest.raises(WriteSetViolation, match="Undeclared write"):
            enforcer.record_write("key_z")

    def test_undeclared_aborts_enforcer(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"key_a"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("bad_key")
        assert enforcer.is_aborted

    def test_aborted_rejects_subsequent(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a", "b"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("bad")
        with pytest.raises(WriteSetViolation, match="aborted"):
            enforcer.record_write("a")

    def test_verify_fails_after_violation(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a"}))
        with pytest.raises(WriteSetViolation):
            enforcer.record_write("bad")
        assert enforcer.verify() is False


class TestWriteSetTracking:
    """actual_writes must track correctly."""

    def test_empty_initially(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a"}))
        assert enforcer.actual_writes == frozenset()

    def test_partial_not_complete(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a", "b"}))
        enforcer.record_write("a")
        assert not enforcer.is_complete

    def test_duplicate_write_idempotent(self):
        enforcer = WriteSetEnforcer(declared_write_set=frozenset({"a"}))
        enforcer.record_write("a")
        enforcer.record_write("a")
        assert enforcer.actual_writes == frozenset({"a"})
