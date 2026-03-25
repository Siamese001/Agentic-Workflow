"""Unit tests for DPO Pair Generator - deterministic HITL feedback processing."""

import pytest

from agentic_core.L6_observability.engines.hitl_dpo_pair_generator import (
    DefaultDeterministicDPOPairGenerator,
)
from agentic_core.L6_observability.types.dpo_types import DPOExampleId
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

# REMOVED: _emit_emits_metric_event("test_dpo_pair_generator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_dpo_pair_generator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_dpo_pair_generator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_dpo_pair_generator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_dpo_pair_generator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_dpo_pair_generator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_dpo_pair_generator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_dpo_pair_generator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_dpo_pair_generator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_dpo_pair_generator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_dpo_pair_generator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_dpo_pair_generator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_dpo_pair_generator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_dpo_pair_generator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_dpo_pair_generator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_dpo_pair_generator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_dpo_pair_generator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_dpo_pair_generator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_dpo_pair_generator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_dpo_pair_generator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_dpo_pair_generator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_dpo_pair_generator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_dpo_pair_generator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_dpo_pair_generator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_dpo_pair_generator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_dpo_pair_generator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_dpo_pair_generator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_dpo_pair_generator", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_dpo_pair_generator")
# REMOVED: _emit_applies_guardrail("p0", "test_dpo_pair_generator", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_dpo_pair_generator", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_dpo_pair_generator", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_dpo_pair_generator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_dpo_pair_generator", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_dpo_pair_generator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_dpo_pair_generator", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_dpo_pair_generator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_dpo_pair_generator", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_dpo_pair_generator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_dpo_pair_generator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_dpo_pair_generator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_dpo_pair_generator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_dpo_pair_generator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_dpo_pair_generator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_dpo_pair_generator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_dpo_pair_generator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_dpo_pair_generator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_dpo_pair_generator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_dpo_pair_generator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_dpo_pair_generator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_dpo_pair_generator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_dpo_pair_generator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_dpo_pair_generator")
# REMOVED: _emit_gated_by_confidence("p1", "test_dpo_pair_generator", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_dpo_pair_generator")
# REMOVED: emit_determinism_digest("p0", "test_dpo_pair_generator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_dpo_pair_generator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_dpo_pair_generator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_dpo_pair_generator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_dpo_pair_generator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_dpo_pair_generator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_dpo_pair_generator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_dpo_pair_generator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_dpo_pair_generator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_dpo_pair_generator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_dpo_pair_generator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_dpo_pair_generator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_dpo_pair_generator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_dpo_pair_generator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_dpo_pair_generator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_dpo_pair_generator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_dpo_pair_generator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_dpo_pair_generator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_dpo_pair_generator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_dpo_pair_generator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_dpo_pair_generator", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestDPOPairGenerator:
    """Test suite for DPO Pair Generator deterministic behavior."""

    def test_hash_stable_same_inputs(self):
        """Same inputs must produce identical hashes and content_hash."""
        generator = DefaultDeterministicDPOPairGenerator()

        control_output = b"control_output_data"
        candidate_output = b"candidate_output_data"
        human_decision = "APPROVE"
        reason_codes = ("good_quality", "meets_requirements")

        # Generate pair twice
        pair1 = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision=human_decision,
            reason_codes=reason_codes,
        )

        pair2 = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision=human_decision,
            reason_codes=reason_codes,
        )

        # Must be identical
        assert pair1.content_hash() == pair2.content_hash()
        assert pair1.example_id.control_hash == pair2.example_id.control_hash
        assert pair1.example_id.candidate_hash == pair2.example_id.candidate_hash
        assert pair1.human_decision == pair2.human_decision
        assert pair1.reasons == pair2.reasons

    def test_different_inputs_different_hashes(self):
        """Different inputs must produce different hashes."""
        generator = DefaultDeterministicDPOPairGenerator()

        control_output1 = b"control_output_1"
        candidate_output1 = b"candidate_output_1"

        control_output2 = b"control_output_2"
        candidate_output2 = b"candidate_output_2"

        pair1 = generator.generate(
            control_output_bytes=control_output1,
            candidate_output_bytes=candidate_output1,
            human_decision="APPROVE",
            reason_codes=("test",),
        )

        pair2 = generator.generate(
            control_output_bytes=control_output2,
            candidate_output_bytes=candidate_output2,
            human_decision="APPROVE",
            reason_codes=("test",),
        )

        # Should have different hashes
        assert pair1.content_hash() != pair2.content_hash()
        assert pair1.example_id.control_hash != pair2.example_id.control_hash
        assert pair1.example_id.candidate_hash != pair2.example_id.candidate_hash

    def test_approve_vs_reject_different_pairs(self):
        """APPROVE and REJECT decisions should create different pairs."""
        generator = DefaultDeterministicDPOPairGenerator()

        control_output = b"same_control"
        candidate_output = b"same_candidate"

        approve_pair = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision="APPROVE",
            reason_codes=("good_quality",),
        )

        reject_pair = generator.generate(
            control_output_bytes=control_output,
            candidate_output_bytes=candidate_output,
            human_decision="REJECT",
            reason_codes=("poor_quality",),
        )

        # Same example_id but different decision
        assert approve_pair.example_id.control_hash == reject_pair.example_id.control_hash
        assert approve_pair.example_id.candidate_hash == reject_pair.example_id.candidate_hash
        assert approve_pair.human_decision != reject_pair.human_decision
        assert approve_pair.content_hash() != reject_pair.content_hash()

    def test_invalid_human_decision_raises_error(self):
        """Invalid human decision should raise ValueError."""
        generator = DefaultDeterministicDPOPairGenerator()

        with pytest.raises(ValueError, match="human_decision must be 'APPROVE' or 'REJECT'"):
            generator.generate(
                control_output_bytes=b"control",
                candidate_output_bytes=b"candidate",
                human_decision="INVALID",
                reason_codes=("test",),
            )

    def test_canonical_bytes_ascii_only(self):
        """canonical_bytes() must be ASCII-only."""
        generator = DefaultDeterministicDPOPairGenerator()

        pair = generator.generate(
            control_output_bytes=b"control",
            candidate_output_bytes=b"candidate",
            human_decision="APPROVE",
            reason_codes=("test_reason", "another_reason"),
        )

        canonical = pair.canonical_bytes()

        # Must be bytes
        assert isinstance(canonical, bytes)

        # Must be ASCII-only
        try:
            canonical.decode("ascii")
        except UnicodeDecodeError:
            pytest.fail("canonical_bytes() must be ASCII-only")

        # Must be stable across calls
        assert canonical == pair.canonical_bytes()

    def test_content_hash_stability(self):
        """content_hash() must be stable 64-character hex string."""
        generator = DefaultDeterministicDPOPairGenerator()

        pair = generator.generate(
            control_output_bytes=b"control",
            candidate_output_bytes=b"candidate",
            human_decision="REJECT",
            reason_codes=("performance_issue",),
        )

        content_hash = pair.content_hash()

        # Must be 64-character hex string
        assert isinstance(content_hash, str)
        assert len(content_hash) == 64
        assert all(c in "0123456789abcdef" for c in content_hash)

        # Must be stable across calls
        assert content_hash == pair.content_hash()

    def test_example_id_deterministic_construction(self):
        """DPOExampleId should be deterministic from hashes."""
        control_hash = "a1b2c3d4" * 8  # 32 chars * 8 = 256 chars, but we need 64
        control_hash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        candidate_hash = "fedcba09" * 8
        candidate_hash = "fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"

        example_id = DPOExampleId(
            control_hash=control_hash,
            candidate_hash=candidate_hash,
        )

        # Should have correct hashes
        assert example_id.control_hash == control_hash
        assert example_id.candidate_hash == candidate_hash

        # Content hash should be deterministic
        content_hash = example_id.content_hash()
        assert len(content_hash) == 64
        assert content_hash == example_id.content_hash()

    def test_reason_codes_preserved(self):
        """Reason codes should be preserved exactly as provided."""
        generator = DefaultDeterministicDPOPairGenerator()

        reason_codes = ("performance", "accuracy", "user_satisfaction")

        pair = generator.generate(
            control_output_bytes=b"control",
            candidate_output_bytes=b"candidate",
            human_decision="APPROVE",
            reason_codes=reason_codes,
        )

        # Should preserve exact tuple
        assert pair.reasons == reason_codes
        assert isinstance(pair.reasons, tuple)
        assert len(pair.reasons) == 3
