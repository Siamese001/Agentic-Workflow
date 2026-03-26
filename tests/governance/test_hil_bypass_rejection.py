"""
REQ-085/086/HDA: Human-in-the-Loop bypass rejection tests.

Tests that HumanDecisionArtifact enforces:
  1. reviewer_sig must be present and valid before execution proceeds
  2. MODIFY_DIFF forces l5_reclear_required=True (automatically)
  3. original_plan_hash must match the submitted plan (anti-replay)
  4. Empty/missing fields are rejected at construction time (fail-closed)
  5. verify() raises on tampered or absent signature

§1 windsurfrules compliance:
- §1.3  Deterministic: fixed secret bytes, no wall-clock, no randomness
- §1.5  Edge cases: empty sig, empty trace_id, wrong plan hash, tampered sig
- §1.6  State transitions: unsigned→sign→verify PASS; unsigned→verify FAIL
- §1.7  Determinism: same inputs → same HMAC → same sig
- §1.8  Fail-closed: HumanDecisionViolation raised before execution
- §1.9  Matrix: action × sig-state × plan-hash-match
- §1.11 Regression: near-miss (valid sig on different payload)

ROBUSTNESS_MATRIX:
  Surface                        | success | edge | failure | recovery | determinism
  -------------------------------|---------|------|---------|----------|------------
  construction validation        |   ✅   |  ✅  |   ✅   |   N/A   |     ✅
  sign() produces valid sig      |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  verify() passes on valid sig   |   ✅   |  ✅  |   N/A  |   N/A   |     ✅
  verify() rejects absent sig    |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  verify() rejects tampered sig  |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  plan_hash mismatch rejected    |   N/A  |  ✅  |   ✅   |   ✅   |     ✅
  MODIFY_DIFF forces l5_reclear  |   ✅   |  ✅  |   N/A  |   N/A   |     ✅

DEFECT_MODEL:
  D1 - Empty reviewer_sig accepted — human bypass with no signature
  D2 - MODIFY_DIFF proceeds without L5 re-clear
  D3 - Tampered artifact passes verify() — replay/forgery attack
  D4 - Plan hash mismatch accepted — cross-plan replay
  D5 - HMAC non-deterministic (sign different results for same input)
  D6 - APPROVE with empty trace_id accepted — untraceable approval
"""

from __future__ import annotations

import pytest

#  # MOVED: from agentic_core.L5_safety.types.human_decision_artifact_types import (
    HumanDecisionArtifact,
    HumanDecisionViolation,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_hil_bypass_rejection", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_hil_bypass_rejection", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_hil_bypass_rejection", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_hil_bypass_rejection", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_hil_bypass_rejection", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_hil_bypass_rejection", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_hil_bypass_rejection", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_hil_bypass_rejection", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_hil_bypass_rejection", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_hil_bypass_rejection", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_hil_bypass_rejection", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_hil_bypass_rejection", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_hil_bypass_rejection", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_hil_bypass_rejection", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_hil_bypass_rejection", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_hil_bypass_rejection", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_hil_bypass_rejection", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_hil_bypass_rejection", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_hil_bypass_rejection", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_hil_bypass_rejection", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_hil_bypass_rejection", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_hil_bypass_rejection", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_hil_bypass_rejection", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_hil_bypass_rejection", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_hil_bypass_rejection", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_hil_bypass_rejection", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_hil_bypass_rejection", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_hil_bypass_rejection", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_hil_bypass_rejection")
# REMOVED: _emit_applies_guardrail("p0", "test_hil_bypass_rejection", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_hil_bypass_rejection", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_hil_bypass_rejection", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_hil_bypass_rejection", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hil_bypass_rejection", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_hil_bypass_rejection", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_hil_bypass_rejection", "write_through")
# REMOVED: _emit_writes_through("p1", "test_hil_bypass_rejection", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_hil_bypass_rejection", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_hil_bypass_rejection", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_hil_bypass_rejection", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_hil_bypass_rejection", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_hil_bypass_rejection", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_hil_bypass_rejection", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_hil_bypass_rejection", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_hil_bypass_rejection", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_hil_bypass_rejection", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_hil_bypass_rejection", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_hil_bypass_rejection", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_hil_bypass_rejection", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_hil_bypass_rejection", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_hil_bypass_rejection", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_hil_bypass_rejection")
# REMOVED: _emit_gated_by_confidence("p1", "test_hil_bypass_rejection", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_hil_bypass_rejection")
# REMOVED: emit_determinism_digest("p0", "test_hil_bypass_rejection")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_hil_bypass_rejection", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_hil_bypass_rejection", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_hil_bypass_rejection", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_hil_bypass_rejection", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_hil_bypass_rejection", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_hil_bypass_rejection", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_hil_bypass_rejection", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_hil_bypass_rejection", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_hil_bypass_rejection", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_hil_bypass_rejection", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_hil_bypass_rejection", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_hil_bypass_rejection", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_hil_bypass_rejection", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_hil_bypass_rejection", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_hil_bypass_rejection", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_hil_bypass_rejection", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_hil_bypass_rejection", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_hil_bypass_rejection", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_hil_bypass_rejection", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_hil_bypass_rejection", "exec_snapshot_link")

pytestmark = pytest.mark.governance

_SECRET = b"test-secret-key-32bytes-padded!!"
_TRACE = "trace-abc-123"
_POLICY = "policy-hash-xyz"
_REVIEWER = "reviewer-001"
_PLAN_HASH = "plan-hash-aaa"
_PATCH = {"op": "replace", "path": "/model", "value": "gpt-4o"}


def _make(
    action: str = "APPROVE",
    trace_id: str = _TRACE,
    policy_hash: str = _POLICY,
    reviewer_id: str = _REVIEWER,
    original_plan_hash: str = _PLAN_HASH,
    structured_patch_schema: dict | None = None,
    reviewer_sig: str = "",
) -> HumanDecisionArtifact:
    return HumanDecisionArtifact(
        trace_id=trace_id,
        policy_hash=policy_hash,
        reviewer_id=reviewer_id,
        action=action,
        original_plan_hash=original_plan_hash,
        structured_patch_schema=structured_patch_schema or {},
        reviewer_sig=reviewer_sig,
    )


# ---------------------------------------------------------------------------
# Construction validation — fail-closed (§1.8)
# ---------------------------------------------------------------------------


class TestConstructionValidation:
    def test_empty_trace_id_raises(self):
                from agentic_core.L5_safety.types.human_decision_artifact_types import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                with pytest.raises(HumanDecisionViolation, match="trace_id"):
                    _make(trace_id="")

            _make(trace_id="")

    def test_empty_original_plan_hash_raises(self):
        with pytest.raises(HumanDecisionViolation, match="original_plan_hash"):
            _make(original_plan_hash="")

    def test_modify_diff_without_patch_raises(self):
        with pytest.raises(HumanDecisionViolation, match="structured_patch_schema"):
            _make(action="MODIFY_DIFF", structured_patch_schema={})

    def test_modify_diff_with_patch_succeeds(self):
        artifact = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        assert artifact.action == "MODIFY_DIFF"

    def test_approve_without_patch_succeeds(self):
        artifact = _make(action="APPROVE")
        assert artifact.action == "APPROVE"

    def test_reject_without_patch_succeeds(self):
        artifact = _make(action="REJECT")
        assert artifact.action == "REJECT"

    def test_artifact_is_frozen(self):
        artifact = _make()
        with pytest.raises(AttributeError):
            artifact.reviewer_id = "hacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# MODIFY_DIFF forces l5_reclear_required (§1.6 / D2)
# ---------------------------------------------------------------------------


class TestL5ReclearEnforcement:
    def test_modify_diff_sets_l5_reclear_true(self):
        artifact = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        assert artifact.l5_reclear_required is True

    def test_approve_does_not_set_l5_reclear(self):
        artifact = _make(action="APPROVE")
        assert artifact.l5_reclear_required is False

    def test_reject_does_not_set_l5_reclear(self):
        artifact = _make(action="REJECT")
        assert artifact.l5_reclear_required is False

    def test_l5_reclear_is_deterministic_across_instances(self):
        a = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        b = _make(action="MODIFY_DIFF", structured_patch_schema=_PATCH)
        assert a.l5_reclear_required == b.l5_reclear_required is True


# ---------------------------------------------------------------------------
# Sign / verify lifecycle (§1.6 state transitions)
# ---------------------------------------------------------------------------


class TestSignVerifyLifecycle:
    def test_unsigned_verify_raises(self):
        artifact = _make()
        with pytest.raises(HumanDecisionViolation, match="reviewer_sig absent"):
            artifact.verify(_SECRET)

    def test_sign_then_verify_passes(self):
        artifact = _make().sign(_SECRET)
        artifact.verify(_SECRET)  # must not raise

    def test_sign_produces_nonempty_sig(self):
        artifact = _make().sign(_SECRET)
        assert artifact.reviewer_sig
        assert len(artifact.reviewer_sig) > 10

    def test_sign_is_deterministic(self):
        a = _make().sign(_SECRET)
        b = _make().sign(_SECRET)
        assert a.reviewer_sig == b.reviewer_sig

    def test_sign_different_secrets_different_sigs(self):
        a = _make().sign(b"secret-one")
        b = _make().sign(b"secret-two")
        assert a.reviewer_sig != b.reviewer_sig

    def test_verify_wrong_secret_raises(self):
        artifact = _make().sign(_SECRET)
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            artifact.verify(b"wrong-secret")


# ---------------------------------------------------------------------------
# Tampered artifact — D3 regression
# ---------------------------------------------------------------------------


class TestTamperedArtifact:
    def test_tampered_action_fails_verify(self):
    """Test tampered_action_fails_verify runtime behavior."""
    # Arrange
    # TODO: Set up test data for tampered_action_fails_verify
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute tampered_action_fails_verify
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions

    def test_tampered_reviewer_id_fails_verify(self):
        signed = _make().sign(_SECRET)
        tampered = HumanDecisionArtifact(
            trace_id=signed.trace_id,
            policy_hash=signed.policy_hash,
            reviewer_id="attacker",
            action=signed.action,
            original_plan_hash=signed.original_plan_hash,
            structured_patch_schema=signed.structured_patch_schema,
            reviewer_sig=signed.reviewer_sig,
        )
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            tampered.verify(_SECRET)

    def test_tampered_trace_id_fails_verify(self):
        signed = _make().sign(_SECRET)
        tampered = HumanDecisionArtifact(
            trace_id="injected-trace",
            policy_hash=signed.policy_hash,
            reviewer_id=signed.reviewer_id,
            action=signed.action,
            original_plan_hash=signed.original_plan_hash,
            structured_patch_schema=signed.structured_patch_schema,
            reviewer_sig=signed.reviewer_sig,
        )
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            tampered.verify(_SECRET)


# ---------------------------------------------------------------------------
# Plan hash mismatch — cross-plan replay (D4)
# ---------------------------------------------------------------------------


class TestPlanHashMismatch:
    def test_correct_plan_hash_passes(self):
        artifact = _make(original_plan_hash="plan-aaa")
        artifact.assert_plan_hash_matches("plan-aaa")  # no raise

    def test_wrong_plan_hash_raises(self):
        artifact = _make(original_plan_hash="plan-aaa")
        with pytest.raises(HumanDecisionViolation, match="mismatch"):
            artifact.assert_plan_hash_matches("plan-bbb")

    def test_empty_submitted_hash_raises(self):
        artifact = _make(original_plan_hash="plan-aaa")
        with pytest.raises(HumanDecisionViolation):
            artifact.assert_plan_hash_matches("")

    def test_plan_hash_check_is_exact(self):
        artifact = _make(original_plan_hash="plan-aaa")
        # Near-miss: prefix match is not enough
        with pytest.raises(HumanDecisionViolation):
            artifact.assert_plan_hash_matches("plan-aa")


# ---------------------------------------------------------------------------
# Matrix: action × sig-state × plan-hash (§1.9)
# ---------------------------------------------------------------------------


class TestActionMatrix:
    @pytest.mark.parametrize(
        "action,patch,expect_l5",
        [
            ("APPROVE", {}, False),
            ("REJECT", {}, False),
            ("MODIFY_DIFF", _PATCH, True),
        ],
    )
    def test_l5_reclear_by_action(self, action, patch, expect_l5):
    """Test l5_reclear_by_action runtime behavior."""
    # Arrange
    # TODO: Set up test data for l5_reclear_by_action
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute l5_reclear_by_action
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions


# ---------------------------------------------------------------------------
# Fail-closed: no side-effects before violation raised (§1.8)
# ---------------------------------------------------------------------------


class TestFailClosed:
    def test_verify_raises_before_any_side_effect(self):
        artifact = _make()
        sentinel = []
        with pytest.raises(HumanDecisionViolation):
            artifact.verify(_SECRET)
            sentinel.append("ran")
        assert sentinel == []

    def test_plan_hash_raises_before_any_side_effect(self):
        artifact = _make(original_plan_hash="correct")
        sentinel = []
        with pytest.raises(HumanDecisionViolation):
            artifact.assert_plan_hash_matches("wrong")
            sentinel.append("ran")
        assert sentinel == []
