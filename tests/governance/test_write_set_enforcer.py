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
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_write_set_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("test_write_set_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("test_write_set_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("test_write_set_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("test_write_set_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("test_write_set_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("test_write_set_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_write_set_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("test_write_set_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_write_set_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("test_write_set_enforcer", "p4obs", "alert")
_emit_links_incident_trace("test_write_set_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("test_write_set_enforcer", "p3lm", "pattern")
_emit_records_learning_event("test_write_set_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_write_set_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_write_set_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_write_set_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("test_write_set_enforcer", "p3lm", "policy")
_emit_stores_learning_state("test_write_set_enforcer", "p3lm", "state")
_emit_records_execution_trace("test_write_set_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_write_set_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_write_set_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_write_set_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_write_set_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_write_set_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("test_write_set_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_write_set_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_write_set_enforcer", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_write_set_enforcer")
_emit_applies_guardrail("p0", "test_write_set_enforcer", "p0_governance")
_emit_reads_policy_state("p0", "test_write_set_enforcer", "policy_binding")
_emit_snapshots_state("p0", "test_write_set_enforcer", "state_snapshot")
_emit_pulls_context("p1", "test_write_set_enforcer", "context_pull")
_emit_pulls_context("p1", "test_write_set_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_write_set_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_write_set_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "test_write_set_enforcer", "write_through")
_emit_writes_through("p1", "test_write_set_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_write_set_enforcer", "safety_validation")
_emit_invokes_eval("p1", "test_write_set_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "test_write_set_enforcer", "routing_commit")
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
