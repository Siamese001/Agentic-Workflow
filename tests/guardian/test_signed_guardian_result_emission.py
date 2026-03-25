"""
Wave 1.5 Gate Test: Guardian results are signed when V15 is enforced.

Verifies that maybe_sign_result() produces a SignedGuardianArtifact when
V15_ENFORCEMENT=1, and passes through unsigned when V15_ENFORCEMENT=0.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    V15EnforcementError,
    maybe_sign_result,
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

# REMOVED: _emit_emits_metric_event("test_signed_guardian_result_emission", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_signed_guardian_result_emission", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_signed_guardian_result_emission", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_signed_guardian_result_emission", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_signed_guardian_result_emission", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_signed_guardian_result_emission", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_signed_guardian_result_emission", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_signed_guardian_result_emission", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_signed_guardian_result_emission", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_signed_guardian_result_emission", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_signed_guardian_result_emission", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_signed_guardian_result_emission", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_signed_guardian_result_emission", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_signed_guardian_result_emission", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_signed_guardian_result_emission", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_signed_guardian_result_emission", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_signed_guardian_result_emission", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_signed_guardian_result_emission", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_signed_guardian_result_emission", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_signed_guardian_result_emission", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_signed_guardian_result_emission", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_signed_guardian_result_emission", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_signed_guardian_result_emission", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_signed_guardian_result_emission", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_signed_guardian_result_emission", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_signed_guardian_result_emission", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_signed_guardian_result_emission", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_signed_guardian_result_emission", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_signed_guardian_result_emission")
# REMOVED: _emit_applies_guardrail("p0", "test_signed_guardian_result_emission", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_signed_guardian_result_emission", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_signed_guardian_result_emission", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_signed_guardian_result_emission", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_signed_guardian_result_emission", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_signed_guardian_result_emission", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_signed_guardian_result_emission", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_signed_guardian_result_emission", "write_through")
# REMOVED: _emit_writes_through("p1", "test_signed_guardian_result_emission", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_signed_guardian_result_emission", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_signed_guardian_result_emission", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_signed_guardian_result_emission", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_signed_guardian_result_emission", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_signed_guardian_result_emission", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_signed_guardian_result_emission", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_signed_guardian_result_emission", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_signed_guardian_result_emission", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_signed_guardian_result_emission", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_signed_guardian_result_emission", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_signed_guardian_result_emission", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_signed_guardian_result_emission", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_signed_guardian_result_emission", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_signed_guardian_result_emission", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_signed_guardian_result_emission")
# REMOVED: _emit_gated_by_confidence("p1", "test_signed_guardian_result_emission", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_signed_guardian_result_emission")
# REMOVED: emit_determinism_digest("p0", "test_signed_guardian_result_emission")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_signed_guardian_result_emission", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_signed_guardian_result_emission", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_signed_guardian_result_emission", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_signed_guardian_result_emission", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_signed_guardian_result_emission", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_signed_guardian_result_emission", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_signed_guardian_result_emission", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_signed_guardian_result_emission", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_signed_guardian_result_emission", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_signed_guardian_result_emission", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_signed_guardian_result_emission", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_signed_guardian_result_emission", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_signed_guardian_result_emission", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_signed_guardian_result_emission", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_signed_guardian_result_emission", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_signed_guardian_result_emission", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_signed_guardian_result_emission", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_signed_guardian_result_emission", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_signed_guardian_result_emission", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_signed_guardian_result_emission", "exec_snapshot_link")


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Ensure V15 env vars are clean before each test."""
    monkeypatch.delenv("V15_ENFORCEMENT", raising=False)
    monkeypatch.delenv("V15_TEST_SIGNING", raising=False)


class TestSignedGuardianResultEmission:
    """§7 — Guardian results must be signed when V15 is enforced."""

    def test_enforced_with_test_signing_produces_signed_result(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        monkeypatch.setenv("V15_TEST_SIGNING", "1")

        result = GuardianResult(guardian_id="test_guardian")
        result.add_check(check_id="dummy", status="PASS", details="ok")

        signed = maybe_sign_result(result, commit_hash="abc123")

        assert signed is result, "maybe_sign_result should return the same object"
        assert signed.v15_signature, "signature must be non-empty when enforced"
        assert signed.v15_trace_id, "trace_id must be set when enforced"
        assert signed.v15_commit_hash == "abc123"

    def test_enforced_signed_result_passes_ensure_v15_signed(self, monkeypatch):
    """Test enforced_signed_result_passes_ensure_v15_signed contract compliance."""
    # Arrange
    # TODO: Set up contract test scenario
    test_scenario = {}  # Replace with actual test scenario

    # Act
    # TODO: Execute contract test
    contract_result = None  # Replace with actual contract test

    # Assert - General Contract
    assert contract_result is not None, "Contract should produce a result"
    assert isinstance(contract_result, object), "Result should be an object"
    # TODO: Add specific contract assertions
    # assert hasattr(contract_result, "complies"), "Result should indicate compliance"
        maybe_sign_result(result, commit_hash="abc123")

        # to_json() calls ensure_v15_signed() internally — must not raise
        json_str = result.to_json()
        assert '"v15_signature"' in json_str

    def test_not_enforced_returns_unsigned(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "0")

        result = GuardianResult(guardian_id="test_guardian")
        returned = maybe_sign_result(result, commit_hash="abc123")

        assert returned is result
        assert not result.v15_signature, "signature must be empty when not enforced"

    def test_not_enforced_serializes_without_error(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "0")

        result = GuardianResult(guardian_id="test_guardian")
        # to_json() must not raise when enforcement is off
        json_str = result.to_json()
        assert '"guardian_id"' in json_str

    def test_enforced_without_test_signing_raises(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        # V15_TEST_SIGNING not set — no enclave available

        result = GuardianResult(guardian_id="test_guardian")
        with pytest.raises(V15EnforcementError, match="signing enclave"):
            maybe_sign_result(result, commit_hash="abc123")

    def test_sign_preserves_trace_id_if_already_set(self, monkeypatch):
        monkeypatch.setenv("V15_ENFORCEMENT", "1")
        monkeypatch.setenv("V15_TEST_SIGNING", "1")

        result = GuardianResult(guardian_id="test_guardian")
        result.v15_trace_id = "pre-set-trace-id"
        maybe_sign_result(result, commit_hash="abc123")

        assert result.v15_trace_id == "pre-set-trace-id"
