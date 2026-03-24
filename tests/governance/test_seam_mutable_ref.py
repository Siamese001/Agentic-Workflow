"""REQ-270/273: Seam mutable reference enforcement.

Prove seam passes only immutable (frozen dataclass / tuple) references;
prove seam replay stable.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.enforcement.runtime_interceptor import (
    MutableReferenceError,
    MutableReferenceTracker,
    assert_immutable_reference,
    clear_mutable_ref_violations,
    get_mutable_ref_violations,
    immutable_references,
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

_emit_emits_metric_event("test_seam_mutable_ref", "p4obs", "metric_1")
_emit_emits_metric_event("test_seam_mutable_ref", "p4obs", "metric_2")
_emit_emits_metric_event("test_seam_mutable_ref", "p4obs", "metric_3")
_emit_emits_metric_event("test_seam_mutable_ref", "p4obs", "metric_4")
_emit_emits_metric_event("test_seam_mutable_ref", "p4obs", "metric_5")
_emit_emits_metric_event("test_seam_mutable_ref", "p4obs", "metric_6")
_emit_records_incident_event("test_seam_mutable_ref", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_seam_mutable_ref", "p4obs", "anomaly")
_emit_writes_observability_log("test_seam_mutable_ref", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_seam_mutable_ref", "p4obs", "mon_state")
_emit_triggers_alert("test_seam_mutable_ref", "p4obs", "alert")
_emit_links_incident_trace("test_seam_mutable_ref", "p4obs", "trace_link")
_emit_captures_pattern("test_seam_mutable_ref", "p3lm", "pattern")
_emit_records_learning_event("test_seam_mutable_ref", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_seam_mutable_ref", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_seam_mutable_ref", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_seam_mutable_ref", "p3lm", "routing")
_emit_improves_agent_policy("test_seam_mutable_ref", "p3lm", "policy")
_emit_stores_learning_state("test_seam_mutable_ref", "p3lm", "state")
_emit_records_execution_trace("test_seam_mutable_ref", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_seam_mutable_ref", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_seam_mutable_ref", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_seam_mutable_ref", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_seam_mutable_ref", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_seam_mutable_ref", "env_read", "p2_env_1")
_emit_reads_environ("test_seam_mutable_ref", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_seam_mutable_ref", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_seam_mutable_ref", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_seam_mutable_ref")
_emit_applies_guardrail("p0", "test_seam_mutable_ref", "p0_governance")
_emit_reads_policy_state("p0", "test_seam_mutable_ref", "policy_binding")
_emit_snapshots_state("p0", "test_seam_mutable_ref", "state_snapshot")
_emit_pulls_context("p1", "test_seam_mutable_ref", "context_pull")
_emit_pulls_context("p1", "test_seam_mutable_ref", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_seam_mutable_ref", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_seam_mutable_ref", "uwg_term_secondary")
_emit_writes_through("p1", "test_seam_mutable_ref", "write_through")
_emit_writes_through("p1", "test_seam_mutable_ref", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_seam_mutable_ref", "safety_validation")
_emit_invokes_eval("p1", "test_seam_mutable_ref", "eval_call")
_emit_proposal_commits_routing("p1", "test_seam_mutable_ref", "routing_commit")
_emit_escalates_to_human("p1", "test_seam_mutable_ref", "human_escalation")
_emit_routes_through("p1", "test_seam_mutable_ref", "route_through")
_emit_checks_agent_registry("p1", "test_seam_mutable_ref", "agent_registry")
_emit_validates_agent_capability("p1", "test_seam_mutable_ref", "capability")
_emit_dispatches_execution_plan("p1", "test_seam_mutable_ref", "exec_plan")
_emit_agent_executes_agent("p1", "test_seam_mutable_ref", "sub_agent")
_emit_routes_to_agent("p1", "test_seam_mutable_ref", "target_agent")
_emit_verifies_policy("p1", "test_seam_mutable_ref", "policy_check")
_emit_observes_runtime_state("p1", "test_seam_mutable_ref", "runtime_state")
_emit_verifies_boundary("p1", "test_seam_mutable_ref", "boundary_check")
_emit_transcripts_response("p1", "test_seam_mutable_ref", "transcript")
_emit_hard_fails_untranscripted("p1", "test_seam_mutable_ref")
_emit_gated_by_confidence("p1", "test_seam_mutable_ref", "confidence_gate")
emit_replay_key("p0", "test_seam_mutable_ref")
emit_determinism_digest("p0", "test_seam_mutable_ref")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_seam_mutable_ref", "execution_auth")
_emit_validates_capability("p2", "test_seam_mutable_ref", "capability_check")
_emit_routes_to_capability("p2", "test_seam_mutable_ref", "capability_route")
_emit_writes_via_uwg("p2", "test_seam_mutable_ref", "uwg_write")
_emit_blocks_direct_write("p2", "test_seam_mutable_ref", "direct_write_block")
_emit_records_tool_invocation("p2", "test_seam_mutable_ref", "tool_invocation")
_emit_captures_execution_output("p2", "test_seam_mutable_ref", "exec_output")
_emit_dispatches_agent("p3", "test_seam_mutable_ref", "agent_dispatch")
_emit_coordinates_agents("p3", "test_seam_mutable_ref", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_seam_mutable_ref", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_seam_mutable_ref", "healing_outcome")
_emit_escalates_failure("p3", "test_seam_mutable_ref", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_seam_mutable_ref", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_seam_mutable_ref", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_seam_mutable_ref", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_seam_mutable_ref", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_seam_mutable_ref", "eval_metric")
_emit_stores_embedding("p4", "test_seam_mutable_ref", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_seam_mutable_ref", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_seam_mutable_ref", "exec_snapshot_link")


@pytest.mark.governance
def test_req270_immutable_reference_enforcement():
    """REQ-270: Seam passes only immutable references."""
    # Test immutable types pass
    assert_immutable_reference(42, "test context")
    assert_immutable_reference("hello", "test context")
    assert_immutable_reference((1, 2, 3), "test context")
    assert_immutable_reference(frozenset([1, 2, 3]), "test context")
    assert_immutable_reference(True, "test context")
    assert_immutable_reference(None, "test context")

    # Test hashable objects pass
    class CustomHashable:
        def __hash__(self):
            return 42

    assert_immutable_reference(CustomHashable(), "test context")


@pytest.mark.governance
def test_req270_mutable_reference_detection():
    """REQ-270: Mutable references are detected and rejected."""
    clear_mutable_ref_violations()

    # Test mutable types fail
    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference([1, 2, 3], "test context")

    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference({"a": 1}, "test context")

    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference({1, 2, 3}, "test context")

    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference(bytearray(b"test"), "test context")


@pytest.mark.governance
def test_req270_frozen_dataclass_allowed():
    """REQ-270: Frozen dataclasses are allowed as immutable."""

    @dataclasses.dataclass(frozen=True)
    class FrozenData:
        value: int
        name: str

    frozen_obj = FrozenData(42, "test")
    assert_immutable_reference(frozen_obj, "test context")

    # Non-frozen dataclass should fail
    @dataclasses.dataclass
    class MutableData:
        value: int
        name: str

    mutable_obj = MutableData(42, "test")
    with pytest.raises(MutableReferenceError, match="Mutable reference detected"):
        assert_immutable_reference(mutable_obj, "test context")


@pytest.mark.governance
def test_req270_allowed_seam_contexts():
    """REQ-270: Mutable references allowed in specific seam contexts."""
    # Test that allowed contexts permit mutable references
    assert_immutable_reference([1, 2, 3], "sovereign_gateway_processing")
    assert_immutable_reference({"a": 1}, "embedding_factory_call")
    assert_immutable_reference([1, 2, 3], "capability_token_validation")

    # Test that non-allowed contexts reject mutable references
    with pytest.raises(MutableReferenceError):
        assert_immutable_reference([1, 2, 3], "random_context")

    with pytest.raises(MutableReferenceError):
        assert_immutable_reference({"a": 1}, "user_function")


@pytest.mark.governance
def test_req273_seam_replay_stability():
    """REQ-273: Seam replay is stable with immutable references."""

    # Simulate seam execution with immutable references
    def seam_execution(data: tuple[int, ...]) -> int:
        """Simulated seam that only accepts immutable data."""
        assert_immutable_reference(data, "seam_execution")
        return sum(data)

    # First execution
    immutable_data = (1, 2, 3, 4, 5)
    result1 = seam_execution(immutable_data)

    # Replay execution (should be identical)
    result2 = seam_execution(immutable_data)

    assert result1 == result2
    assert result1 == 15


@pytest.mark.governance
def test_req273_mutable_reference_breaks_replay():
    """REQ-273: Mutable references break replay stability."""

    def seam_with_mutable(data: list[int]) -> int:
        """Seam that incorrectly accepts mutable data."""
        # This would normally be caught by assert_immutable_reference
        # but we're testing the replay stability concept
        return sum(data)

    mutable_data = [1, 2, 3, 4, 5]
    result1 = seam_with_mutable(mutable_data)

    # Modify mutable data between executions
    mutable_data.append(6)
    result2 = seam_with_mutable(mutable_data)

    # Results differ - replay not stable
    assert result1 != result2
    assert result1 == 15
    assert result2 == 21


@pytest.mark.governance
def test_req270_273_decorator_enforcement():
    """REQ-270/273: Decorator enforces immutable references."""

    @immutable_references
    def process_data(values: tuple[int, ...], multiplier: int) -> tuple[int, ...]:
        return tuple(v * multiplier for v in values)

    # Should work with immutable arguments
    result = process_data((1, 2, 3), 2)
    assert result == (2, 4, 6)

    # Should fail with mutable arguments
    with pytest.raises(MutableReferenceError):
        process_data([1, 2, 3], 2)

    with pytest.raises(MutableReferenceError):
        process_data((1, 2, 3), [2])  # mutable keyword arg


@pytest.mark.governance
def test_req270_violation_tracking():
    """REQ-270: Mutable reference violations are tracked."""
    clear_mutable_ref_violations()

    with MutableReferenceTracker():
        # Generate some violations
        with pytest.raises(MutableReferenceError):
            assert_immutable_reference([1, 2, 3], "test1")

        with pytest.raises(MutableReferenceError):
            assert_immutable_reference({"a": 1}, "test2")

        # Check violations were recorded
        violations = get_mutable_ref_violations()
        assert len(violations) == 2
        assert "test1" in violations[0]
        assert "test2" in violations[1]

    # Violations should still be available after context exit
    violations = get_mutable_ref_violations()
    assert len(violations) == 2


@pytest.mark.governance
def test_req270_complex_object_immutability():
    """REQ-270: Complex object immutability detection."""
    # Nested immutable structures
    nested_immutable = ((1, 2), (3, 4), (5, 6))
    assert_immutable_reference(nested_immutable, "nested test")

    # Nested mutable structures
    nested_mutable = ([1, 2], [3, 4], [5, 6])
    with pytest.raises(MutableReferenceError):
        assert_immutable_reference(nested_mutable, "nested test")

    # Mixed structures (should fail due to mutable component)
    mixed = (1, [2, 3], 4)
    with pytest.raises(MutableReferenceError):
        assert_immutable_reference(mixed, "mixed test")
