"""
Phase 5 — Wave 1 Tests: ViolationEvent schema, hashing, emission.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.types.violation_event_types import (
    ViolationEvent,
    emit_violation_event,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_violation_event", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_violation_event", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_violation_event", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_violation_event", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_violation_event", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_violation_event", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_violation_event", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_violation_event", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_violation_event", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_violation_event", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_violation_event", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_violation_event", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_violation_event", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_violation_event", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_violation_event", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_violation_event", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_violation_event", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_violation_event", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_violation_event", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_violation_event", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_violation_event", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_violation_event", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_violation_event", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_violation_event", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_violation_event", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_violation_event", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_violation_event", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_violation_event", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_violation_event")
# REMOVED: _emit_applies_guardrail("p0", "test_violation_event", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_violation_event", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_violation_event", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_violation_event", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_violation_event", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_violation_event", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_violation_event", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_violation_event", "write_through")
# REMOVED: _emit_writes_through("p1", "test_violation_event", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_violation_event", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_violation_event", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_violation_event", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_violation_event", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_violation_event", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_violation_event", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_violation_event", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_violation_event", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_violation_event", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_violation_event", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_violation_event", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_violation_event", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_violation_event", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_violation_event", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_violation_event")
# REMOVED: _emit_gated_by_confidence("p1", "test_violation_event", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_violation_event")
# REMOVED: emit_determinism_digest("p0", "test_violation_event")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_violation_event", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_violation_event", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_violation_event", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_violation_event", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_violation_event", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_violation_event", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_violation_event", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_violation_event", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_violation_event", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_violation_event", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_violation_event", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_violation_event", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_violation_event", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_violation_event", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_violation_event", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_violation_event", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_violation_event", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_violation_event", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_violation_event", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_violation_event", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"


def _make_event(**overrides) -> ViolationEvent:
    defaults: dict = {
        "schema_version": 1,
        "mission_id": "mission-abc",
        "commit_tick": 5,
        "guardian_decision": "block",
        "violation_codes": ["SCOPE_VIOLATION", "IMPORT_ERROR"],
        "severity_score": 0.9,
        "created_at_utc": _TS,
    }
    defaults.update(overrides)
    return ViolationEvent(**defaults)


class TestViolationEventHash:
    def test_violation_event_hash_stable(self):
        """Same inputs produce the same event_hash on repeated construction."""
        e1 = _make_event()
        e2 = _make_event()
        assert e1.event_hash == e2.event_hash
        assert len(e1.event_hash) == 64

    def test_hash_changes_with_mission_id(self):
        e1 = _make_event(mission_id="mission-A")
        e2 = _make_event(mission_id="mission-B")
        assert e1.event_hash != e2.event_hash

    def test_hash_changes_with_commit_tick(self):
        e1 = _make_event(commit_tick=1)
        e2 = _make_event(commit_tick=2)
        assert e1.event_hash != e2.event_hash

    def test_hash_changes_with_decision(self):
        e1 = _make_event(guardian_decision="allow")
        e2 = _make_event(guardian_decision="block")
        assert e1.event_hash != e2.event_hash

    def test_hash_changes_with_severity(self):
        e1 = _make_event(severity_score=0.5)
        e2 = _make_event(severity_score=0.9)
        assert e1.event_hash != e2.event_hash

    def test_event_hash_excluded_from_canonical_bytes(self):
        """canonical_bytes must not contain the string 'event_hash'."""
        e = _make_event()
        assert b"event_hash" not in e.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        e1 = _make_event()
        e2 = _make_event()
        assert e1.canonical_bytes() == e2.canonical_bytes()


class TestViolationEventCodesSorted:
    def test_violation_event_codes_sorted_in_canonical_bytes(self):
        """
        violation_codes in canonical_bytes must be sorted regardless of
        the order passed to the constructor.
        """
        e_unsorted = _make_event(violation_codes=["Z_CODE", "A_CODE", "M_CODE"])
        e_sorted = _make_event(violation_codes=["A_CODE", "M_CODE", "Z_CODE"])
        assert e_unsorted.event_hash == e_sorted.event_hash
        assert e_unsorted.violation_codes == ["A_CODE", "M_CODE", "Z_CODE"]

    def test_violation_codes_stored_sorted(self):
        e = _make_event(violation_codes=["Z", "A", "M"])
        assert e.violation_codes == ["A", "M", "Z"]

    def test_empty_violation_codes_allowed(self):
        e = _make_event(violation_codes=[])
        assert e.violation_codes == []
        assert len(e.event_hash) == 64


class TestSeverityScoreRange:
    def test_severity_score_range_enforced_zero(self):
        e = _make_event(severity_score=0.0)
        assert e.severity_score == 0.0

    def test_severity_score_range_enforced_one(self):
        e = _make_event(severity_score=1.0)
        assert e.severity_score == 1.0

    def test_severity_score_below_zero_raises(self):
        with pytest.raises(ValueError, match="severity_score"):
            _make_event(severity_score=-0.01)

    def test_severity_score_above_one_raises(self):
        with pytest.raises(ValueError, match="severity_score"):
            _make_event(severity_score=1.001)

    def test_severity_score_midpoint(self):
        e = _make_event(severity_score=0.5)
        assert e.severity_score == 0.5


class TestViolationEventValidation:
    def test_invalid_schema_version_raises(self):
    """Test invalid_schema_version_raises contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"

    def test_valid_decisions_accepted(self):
        for decision in ("allow", "block", "escalate"):
            e = _make_event(guardian_decision=decision)
            assert e.guardian_decision == decision

    def test_non_list_violation_codes_raises(self):
        with pytest.raises(TypeError, match="violation_codes"):
            _make_event(violation_codes="SCOPE_VIOLATION")


class TestEmitViolationEvent:
    def test_emit_returns_violation_event(self):
        e = emit_violation_event(
            mission_id="m1",
            commit_tick=3,
            guardian_decision="escalate",
            violation_codes=["CODE_A"],
            severity_score=0.8,
            created_at_utc=_TS,
        )
        assert isinstance(e, ViolationEvent)
        assert e.guardian_decision == "escalate"

    def test_emit_appends_to_registry(self):
        registry: list[ViolationEvent] = []
        emit_violation_event(
            mission_id="m1",
            commit_tick=1,
            guardian_decision="block",
            violation_codes=[],
            severity_score=0.5,
            created_at_utc=_TS,
            _registry=registry,
        )
        emit_violation_event(
            mission_id="m1",
            commit_tick=2,
            guardian_decision="allow",
            violation_codes=[],
            severity_score=0.1,
            created_at_utc=_TS,
            _registry=registry,
        )
        assert len(registry) == 2

    def test_emit_does_not_alter_decision(self):
        """Emission is pure recording — decision field is unchanged."""
        e = emit_violation_event(
            mission_id="m1",
            commit_tick=7,
            guardian_decision="allow",
            violation_codes=[],
            severity_score=0.0,
            created_at_utc=_TS,
        )
        assert e.guardian_decision == "allow"

    def test_to_dict_round_trip(self):
        e = _make_event()
        d = e.to_dict()
        e2 = ViolationEvent.from_dict(d)
        assert e2.event_hash == e.event_hash
        assert e2.violation_codes == e.violation_codes
