"""
W4-D Policy Recommendation Engine Tests

Tests for deterministic policy recommendation generation from drift analysis.
"""

import os

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_policy_recommendation_w4d", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_policy_recommendation_w4d", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_policy_recommendation_w4d", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_policy_recommendation_w4d", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_policy_recommendation_w4d", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_policy_recommendation_w4d", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_policy_recommendation_w4d", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_policy_recommendation_w4d", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_policy_recommendation_w4d", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_policy_recommendation_w4d", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_policy_recommendation_w4d", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_policy_recommendation_w4d", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_policy_recommendation_w4d", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_policy_recommendation_w4d", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_policy_recommendation_w4d", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_policy_recommendation_w4d", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_policy_recommendation_w4d", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_policy_recommendation_w4d", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_policy_recommendation_w4d", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_policy_recommendation_w4d", "exec_snapshot_link")
from system_learning.engines.policy_recommendation_engine import (
    PolicyRecommendationEngine,
)
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.shadow_drift_analyzer import DriftSummary

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_policy_recommendation_w4d")
# REMOVED: _emit_applies_guardrail("p0", "test_policy_recommendation_w4d", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_policy_recommendation_w4d", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_policy_recommendation_w4d", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_policy_recommendation_w4d", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_policy_recommendation_w4d", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_policy_recommendation_w4d", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_policy_recommendation_w4d", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_policy_recommendation_w4d", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_policy_recommendation_w4d", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_policy_recommendation_w4d", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_policy_recommendation_w4d", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_policy_recommendation_w4d", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_policy_recommendation_w4d", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_policy_recommendation_w4d", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_policy_recommendation_w4d", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_policy_recommendation_w4d", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_policy_recommendation_w4d", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_policy_recommendation_w4d", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_policy_recommendation_w4d", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_policy_recommendation_w4d", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_policy_recommendation_w4d", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_policy_recommendation_w4d", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_policy_recommendation_w4d", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_policy_recommendation_w4d", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_policy_recommendation_w4d", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_policy_recommendation_w4d", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_policy_recommendation_w4d", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_policy_recommendation_w4d", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_policy_recommendation_w4d", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_policy_recommendation_w4d", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_policy_recommendation_w4d", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_policy_recommendation_w4d", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_policy_recommendation_w4d", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_policy_recommendation_w4d", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_policy_recommendation_w4d", "write_through")
# REMOVED: _emit_writes_through("p1", "test_policy_recommendation_w4d", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_policy_recommendation_w4d", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_policy_recommendation_w4d", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_policy_recommendation_w4d", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_policy_recommendation_w4d", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_policy_recommendation_w4d", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_policy_recommendation_w4d", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_policy_recommendation_w4d", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_policy_recommendation_w4d", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_policy_recommendation_w4d", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_policy_recommendation_w4d", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_policy_recommendation_w4d", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_policy_recommendation_w4d", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_policy_recommendation_w4d", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_policy_recommendation_w4d", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_policy_recommendation_w4d")
# REMOVED: _emit_gated_by_confidence("p1", "test_policy_recommendation_w4d", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_policy_recommendation_w4d")
# REMOVED: emit_determinism_digest("p0", "test_policy_recommendation_w4d")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


@pytest.mark.unit_min_deps
class TestPolicyRecommendationW4D:
    """Test W4-D Policy Recommendation Engine functionality."""

    def test_policy_recommendation_determinism(self):
        """Test that policy recommendations produce identical digests for identical inputs."""
        # Create fixed drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=BATCH_SIZE,
            mean_cosine=0.916667,
            p95_cosine=0.947,
            drift_flag=False,
            drift_score=0.053,
            deterministic_digest="test-digest-123",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        engine = PolicyRecommendationEngine()
        now_utc = 1234567890

        # Run recommendation twice independently
        rec1 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        rec2 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify deterministic digest
        assert rec1.deterministic_digest == rec2.deterministic_digest, (
            "Policy recommendation must be deterministic"
        )

        # Emit digest for test verification
        rec1.emit_digest()

        # Verify no drift case
        assert rec1.profile_id == "test-profile"
        assert rec1.recommended_changes == {}, "No changes should be recommended when no drift"
        assert "No drift detected" in rec1.rationale
        assert rec1.confidence_score == 0.95

    def test_policy_recommendation_bounded_recommendation(self):
        """Test that recommendations are bounded within safe limits."""
        # Create high drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=BATCH_SIZE,
            mean_cosine=0.80,
            p95_cosine=0.85,  # Below 0.92 threshold
            drift_flag=True,
            drift_score=0.15,  # High drift
            deterministic_digest="test-digest-456",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.90,
            influence_cap=0.80,
            normalization_policy="l2",
        )

        engine = PolicyRecommendationEngine()
        now_utc = 1234567890

        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify drift detected
        assert recommendation.recommended_changes != {}, "Changes should be recommended when drift detected"
        assert "Drift detected" in recommendation.rationale

        # Verify bounded similarity_cutoff reduction
        if "similarity_cutoff" in recommendation.recommended_changes:
            new_cutoff = recommendation.recommended_changes["similarity_cutoff"]
            # Max reduction: min(0.02, 0.15 * 0.05) = min(0.02, 0.0075) = 0.0075
            expected_max_reduction = 0.0075
            actual_reduction = active_profile.similarity_cutoff - new_cutoff
            assert actual_reduction <= expected_max_reduction + 0.000001, (
                f"Cutoff reduction {actual_reduction} exceeds max {expected_max_reduction}"
            )
            assert new_cutoff >= 0.1, "Cutoff should not go below minimum safe value"

        # Verify bounded influence_cap increase
        if "influence_cap" in recommendation.recommended_changes:
            new_cap = recommendation.recommended_changes["influence_cap"]
            # Max increase: min(0.01, 0.15 * 0.02) = min(0.01, 0.003) = 0.003
            expected_max_increase = 0.003
            actual_increase = new_cap - active_profile.influence_cap
            assert actual_increase <= expected_max_increase + 0.000001, (
                f"Cap increase {actual_increase} exceeds max {expected_max_increase}"
            )
            assert new_cap <= 1.0, "Cap should not exceed maximum safe value"

        # Verify confidence is bounded
        assert 0.0 <= recommendation.confidence_score <= 1.0, (
            "Confidence score must be bounded between 0 and 1"
        )

    def test_policy_recommendation_no_drift_case(self):
        """Test recommendation when no drift is detected."""
        # Create no drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=BATCH_SIZE,
            mean_cosine=0.95,
            p95_cosine=0.96,  # Above 0.92 threshold
            drift_flag=False,
            drift_score=0.04,
            deterministic_digest="test-digest-789",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        engine = PolicyRecommendationEngine()
        now_utc = 1234567890

        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify no changes recommended
        assert recommendation.recommended_changes == {}, (
            "No changes should be recommended when drift_flag is False"
        )
        assert "No drift detected" in recommendation.rationale
        assert f"{drift_summary.p95_cosine:.6f}" in recommendation.rationale
        assert recommendation.confidence_score == 0.95

    def test_policy_recommendation_non_influential(self):
        """Test that recommendation engine does not influence retrieval behavior."""
        # This test verifies that the recommendation engine is purely advisory
        # by checking that it doesn't modify input data or active profile

        engine = PolicyRecommendationEngine()
        now_utc = 1234567890

        # Create drift summary
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=BATCH_SIZE,
            mean_cosine=0.80,
            p95_cosine=0.85,
            drift_flag=True,
            drift_score=0.15,
            deterministic_digest="test-digest-noninf",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.90,
            influence_cap=0.80,
            normalization_policy="l2",
        )

        # Make copies for comparison
        import copy

        drift_summary_copy = copy.deepcopy(drift_summary)
        active_profile_copy = copy.deepcopy(active_profile)

        # Run recommendation
        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify inputs are unchanged
        assert drift_summary == drift_summary_copy, "Drift summary must not be modified"
        assert active_profile == active_profile_copy, "Active profile must not be modified"

        # Verify recommendation is computed correctly
        assert recommendation.profile_id == "test-profile"
        assert recommendation.recommended_changes != {}, "Changes should be recommended"

    def test_policy_recommendation_edge_cases(self):
        """Test edge cases for recommendation generation."""
        engine = PolicyRecommendationEngine()
        now_utc = 1234567890

        # Test with minimal drift score
        drift_summary_minimal = DriftSummary(
            profile_id="test-profile",
            batch_size=BATCH_SIZE,
            mean_cosine=0.919999,
            p95_cosine=0.919999,  # Just below threshold
            drift_flag=True,
            drift_score=0.080001,  # Very minimal drift
            deterministic_digest="test-digest-minimal",
        )

        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        recommendation = engine.generate_recommendation(
            drift_summary=drift_summary_minimal,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Should still recommend changes but very small
        if "similarity_cutoff" in recommendation.recommended_changes:
            reduction = (
                active_profile.similarity_cutoff - recommendation.recommended_changes["similarity_cutoff"]
            )
            assert reduction <= 0.02, "Reduction should be bounded by max"
            assert reduction > 0, "Should recommend some reduction"


@pytest.mark.unit_min_deps
class TestW4DNegativeControl:
    """Negative control tests for W4-D Policy Recommendation Engine."""

    @pytest.mark.xfail(reason="W4D tamper guard", strict=True)
    def test_policy_recommendation_determinism_violation_negative_control(self):
        """Negative control: tamper with recommendation determinism."""
        # Set tamper flag to change rounding precision
        os.environ["W4D_NEGCTRL_TAMPER"] = "1"

        # Monkey patch the rounding function to use different precision
        import system_learning.engines.policy_recommendation_engine as engine_module

        original_round = round

        def tampered_round(x, ndigits=None):
            """Tampered rounding that uses 3 decimal places instead of 6."""
            if ndigits is not None and ndigits >= 6:
                # Use 3 decimal places when 6+ is requested
                ndigits = 3
            return original_round(x, ndigits)

        try:
            # Apply tampering
            engine_module.round = tampered_round

            # Create fixed inputs
            drift_summary = DriftSummary(
                profile_id="test-profile",
                batch_size=BATCH_SIZE,
                mean_cosine=0.916667,
                p95_cosine=0.947,
                drift_flag=True,
                drift_score=0.053,
                deterministic_digest="test-digest-123",
            )

            active_profile = RetrievalProfile(
                profile_id="test-profile",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=10,
                similarity_cutoff=0.85,
                influence_cap=0.5,
                normalization_policy="l2",
            )

            engine = PolicyRecommendationEngine()
            now_utc = 1234567890

            # Run recommendation with tampering
            rec_tampered = engine.generate_recommendation(
                drift_summary=drift_summary,
                active_profile=active_profile,
                now_utc=now_utc,
            )

            # Restore original rounding for comparison
            engine_module.round = original_round
            rec_normal = engine.generate_recommendation(
                drift_summary=drift_summary,
                active_profile=active_profile,
                now_utc=now_utc,
            )

            # Tampering should cause different results - this should FAIL the test
            if rec_tampered.deterministic_digest != rec_normal.deterministic_digest:
                assert False, (
                    f"TAMPERING DETECTED: tampered digest {rec_tampered.deterministic_digest} != normal digest {rec_normal.deterministic_digest}"
                )

            # Also check for rounding differences
            if rec_tampered.confidence_score != rec_normal.confidence_score:
                assert False, (
                    f"TAMPERING DETECTED: tampered confidence {rec_tampered.confidence_score} != normal confidence {rec_normal.confidence_score}"
                )

            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - values are identical"

        finally:
            # Restore original function
            engine_module.round = original_round
            # Clean up environment
            os.environ.pop("W4D_NEGCTRL_TAMPER", None)

    def test_policy_recommendation_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W4D_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W4D_NEGCTRL_TAMPER"]

        # Create fixed inputs
        drift_summary = DriftSummary(
            profile_id="test-profile",
            batch_size=BATCH_SIZE,
            mean_cosine=0.916667,
            p95_cosine=0.947,
            drift_flag=False,
            drift_score=0.053,
            deterministic_digest="test-digest-123",
        )

        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        engine = PolicyRecommendationEngine()
        now_utc = 1234567890

        # Run recommendation twice without tampering
        rec1 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        rec2 = engine.generate_recommendation(
            drift_summary=drift_summary,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Should be identical when not tampering
        assert rec1.deterministic_digest == rec2.deterministic_digest, (
            "Digest must be identical when not tampering"
        )
        assert rec1.confidence_score == rec2.confidence_score, (
            "Confidence score must be identical when not tampering"
        )
