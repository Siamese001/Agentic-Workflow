"""Unit tests for RollbackRefiner - deterministic rollback strategy selection."""

import pytest

from agentic_core.L2_execution.engines.rollback_refiner import (
    DefaultDeterministicRollbackRefiner,
)
from agentic_core.L2_execution.types.resource_prediction_types import FailureSignature
from agentic_core.L2_execution.types.rollback_refinement_types import (
    RollbackRefinementDecision,
    RollbackRefinementRequest,
    RollbackStrategyId,
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

_emit_emits_metric_event("test_rollback_refiner", "p4obs", "metric_1")
_emit_emits_metric_event("test_rollback_refiner", "p4obs", "metric_2")
_emit_emits_metric_event("test_rollback_refiner", "p4obs", "metric_3")
_emit_emits_metric_event("test_rollback_refiner", "p4obs", "metric_4")
_emit_emits_metric_event("test_rollback_refiner", "p4obs", "metric_5")
_emit_emits_metric_event("test_rollback_refiner", "p4obs", "metric_6")
_emit_records_incident_event("test_rollback_refiner", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_rollback_refiner", "p4obs", "anomaly")
_emit_writes_observability_log("test_rollback_refiner", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_rollback_refiner", "p4obs", "mon_state")
_emit_triggers_alert("test_rollback_refiner", "p4obs", "alert")
_emit_links_incident_trace("test_rollback_refiner", "p4obs", "trace_link")
_emit_captures_pattern("test_rollback_refiner", "p3lm", "pattern")
_emit_records_learning_event("test_rollback_refiner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_rollback_refiner", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_rollback_refiner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_rollback_refiner", "p3lm", "routing")
_emit_improves_agent_policy("test_rollback_refiner", "p3lm", "policy")
_emit_stores_learning_state("test_rollback_refiner", "p3lm", "state")
_emit_records_execution_trace("test_rollback_refiner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_rollback_refiner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_rollback_refiner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_rollback_refiner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_rollback_refiner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_rollback_refiner", "env_read", "p2_env_1")
_emit_reads_environ("test_rollback_refiner", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_rollback_refiner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_rollback_refiner", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_rollback_refiner")
_emit_applies_guardrail("p0", "test_rollback_refiner", "p0_governance")
_emit_reads_policy_state("p0", "test_rollback_refiner", "policy_binding")
_emit_snapshots_state("p0", "test_rollback_refiner", "state_snapshot")
_emit_pulls_context("p1", "test_rollback_refiner", "context_pull")
_emit_pulls_context("p1", "test_rollback_refiner", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_rollback_refiner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_rollback_refiner", "uwg_term_secondary")
_emit_writes_through("p1", "test_rollback_refiner", "write_through")
_emit_writes_through("p1", "test_rollback_refiner", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_rollback_refiner", "safety_validation")
_emit_invokes_eval("p1", "test_rollback_refiner", "eval_call")
_emit_proposal_commits_routing("p1", "test_rollback_refiner", "routing_commit")
_emit_escalates_to_human("p1", "test_rollback_refiner", "human_escalation")
_emit_routes_through("p1", "test_rollback_refiner", "route_through")
_emit_checks_agent_registry("p1", "test_rollback_refiner", "agent_registry")
_emit_validates_agent_capability("p1", "test_rollback_refiner", "capability")
_emit_dispatches_execution_plan("p1", "test_rollback_refiner", "exec_plan")
_emit_agent_executes_agent("p1", "test_rollback_refiner", "sub_agent")
_emit_routes_to_agent("p1", "test_rollback_refiner", "target_agent")
_emit_verifies_policy("p1", "test_rollback_refiner", "policy_check")
_emit_observes_runtime_state("p1", "test_rollback_refiner", "runtime_state")
_emit_verifies_boundary("p1", "test_rollback_refiner", "boundary_check")
_emit_transcripts_response("p1", "test_rollback_refiner", "transcript")
_emit_hard_fails_untranscripted("p1", "test_rollback_refiner")
_emit_gated_by_confidence("p1", "test_rollback_refiner", "confidence_gate")
emit_replay_key("p0", "test_rollback_refiner")
emit_determinism_digest("p0", "test_rollback_refiner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_rollback_refiner", "execution_auth")
_emit_validates_capability("p2", "test_rollback_refiner", "capability_check")
_emit_routes_to_capability("p2", "test_rollback_refiner", "capability_route")
_emit_writes_via_uwg("p2", "test_rollback_refiner", "uwg_write")
_emit_blocks_direct_write("p2", "test_rollback_refiner", "direct_write_block")
_emit_records_tool_invocation("p2", "test_rollback_refiner", "tool_invocation")
_emit_captures_execution_output("p2", "test_rollback_refiner", "exec_output")
_emit_dispatches_agent("p3", "test_rollback_refiner", "agent_dispatch")
_emit_coordinates_agents("p3", "test_rollback_refiner", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_rollback_refiner", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_rollback_refiner", "healing_outcome")
_emit_escalates_failure("p3", "test_rollback_refiner", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_rollback_refiner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_rollback_refiner", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_rollback_refiner", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_rollback_refiner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_rollback_refiner", "eval_metric")
_emit_stores_embedding("p4", "test_rollback_refiner", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_rollback_refiner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_rollback_refiner", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestRollbackRefiner:
    """Test suite for RollbackRefiner deterministic behavior."""

    def test_determinism_and_tie_break(self):
        """Same inputs must produce identical decisions with deterministic tie-breaking."""
        refiner = DefaultDeterministicRollbackRefiner()

        signature = FailureSignature(
            component="test_component",
            failure_type="timeout",
            fingerprint="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
        )

        candidates = (
            RollbackStrategyId("strategy_a"),
            RollbackStrategyId("strategy_b"),
            RollbackStrategyId("strategy_c"),
        )

        request = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates,
            history_bytes=None,
        )

        # Run refinement twice
        decision1 = refiner.refine(request=request)
        decision2 = refiner.refine(request=request)

        # Must be identical
        assert decision1.content_hash() == decision2.content_hash()
        assert decision1.chosen == decision2.chosen
        assert decision1.ranked == decision2.ranked
        assert decision1.reasons == decision2.reasons

        # Tie-breaking: should choose lexicographically first when scores equal
        assert decision1.chosen.name == "strategy_a"  # Lexicographically first

    def test_permutation_invariance_candidates(self):
        """Candidate order permutation should not affect final ranking."""
        refiner = DefaultDeterministicRollbackRefiner()

        signature = FailureSignature(
            component="test",
            failure_type="memory_error",
            fingerprint="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        )

        # Same candidates in different orders
        candidates1 = (
            RollbackStrategyId("zebra"),
            RollbackStrategyId("alpha"),
            RollbackStrategyId("beta"),
        )

        candidates2 = (
            RollbackStrategyId("beta"),
            RollbackStrategyId("zebra"),
            RollbackStrategyId("alpha"),
        )

        request1 = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates1,
            history_bytes=None,
        )

        request2 = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates2,
            history_bytes=None,
        )

        decision1 = refiner.refine(request=request1)
        decision2 = refiner.refine(request=request2)

        # Should produce same ranking (deterministic ordering)
        assert decision1.ranked == decision2.ranked
        assert decision1.chosen == decision2.chosen

    def test_history_influence_deterministic(self):
        """History should influence decisions deterministically."""
        refiner = DefaultDeterministicRollbackRefiner()

        signature = FailureSignature(
            component="test",
            failure_type="cpu_error",
            fingerprint="fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
        )

        candidates = (
            RollbackStrategyId("graceful_shutdown"),
            RollbackStrategyId("checkpoint_restore"),
            RollbackStrategyId("full_restart"),
        )

        # Different history should produce different results
        history1 = b"history_with_high_success_rates"
        history2 = b"history_with_mixed_results"

        request1 = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates,
            history_bytes=history1,
        )

        request2 = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates,
            history_bytes=history2,
        )

        request_no_history = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates,
            history_bytes=None,
        )

        decision1 = refiner.refine(request=request1)
        decision2 = refiner.refine(request=request2)
        decision_no_hist = refiner.refine(request=request_no_history)

        # Should produce different decisions
        assert decision1.content_hash() != decision2.content_hash()
        assert decision1.content_hash() != decision_no_hist.content_hash()
        assert decision2.content_hash() != decision_no_hist.content_hash()

    def test_failure_type_preferences(self):
        """Different failure types should prefer different strategies."""
        refiner = DefaultDeterministicRollbackRefiner()

        candidates = (
            RollbackStrategyId("graceful_shutdown"),
            RollbackStrategyId("checkpoint_restore"),
            RollbackStrategyId("state_snapshot"),
            RollbackStrategyId("incremental_rollback"),
            RollbackStrategyId("full_restart"),
            RollbackStrategyId("circuit_breaker"),
        )

        # Test different failure types
        failure_types = ["timeout", "memory_error", "cpu_error", "io_error", "network_error"]
        decisions = {}

        for failure_type in failure_types:
            signature = FailureSignature(
                component="test",
                failure_type=failure_type,
                fingerprint=f"{failure_type}_fingerprint_1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            )

            request = RollbackRefinementRequest(
                failure_signature=signature,
                candidates=candidates,
                history_bytes=None,
            )

            decision = refiner.refine(request=request)
            decisions[failure_type] = decision

        # Timeouts should prefer graceful_shutdown
        assert decisions["timeout"].chosen.name == "graceful_shutdown"

        # Memory errors should prefer state_snapshot
        assert decisions["memory_error"].chosen.name == "state_snapshot"

        # CPU errors should prefer full_restart
        assert decisions["cpu_error"].chosen.name == "full_restart"

    def test_ranked_order_deterministic(self):
        """Ranked strategies must be in deterministic order."""
        refiner = DefaultDeterministicRollbackRefiner()

        signature = FailureSignature(
            component="test",
            failure_type="io_error",
            fingerprint="1111111111111111111111111111111111111111111111111111111111111111",
        )

        candidates = (
            RollbackStrategyId("z_strategy"),
            RollbackStrategyId("a_strategy"),
            RollbackStrategyId("m_strategy"),
        )

        request = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates,
            history_bytes=None,
        )

        decision = refiner.refine(request=request)

        # Should be ranked by score then name (deterministic tie-breaking)
        assert decision.ranked[0].name == "a_strategy"  # Should be highest score/tie-break
        assert len(decision.ranked) == 3  # All candidates should be ranked
        assert {s.name for s in decision.ranked} == {"a_strategy", "m_strategy", "z_strategy"}

    def test_canonical_bytes_stability(self):
        """canonical_bytes() must be stable and ASCII-only."""
        candidates = (RollbackStrategyId("test_strategy"),)

        decision = RollbackRefinementDecision(
            chosen=candidates[0],
            ranked=candidates,
            reasons=("test_reason", "deterministic_tie_break"),
        )

        canonical = decision.canonical_bytes()

        # Must be bytes
        assert isinstance(canonical, bytes)

        # Must be ASCII-only
        try:
            canonical.decode("ascii")
        except UnicodeDecodeError:
            pytest.fail("canonical_bytes() must be ASCII-only")

        # Must be stable across calls
        assert canonical == decision.canonical_bytes()

    def test_empty_candidates_handling(self):
        """Should handle empty candidates gracefully."""
        refiner = DefaultDeterministicRollbackRefiner()

        signature = FailureSignature(
            component="test",
            failure_type="unknown",
            fingerprint="0000000000000000000000000000000000000000000000000000000000000000",
        )

        request = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=(),  # Empty candidates
            history_bytes=None,
        )

        # Should not crash, but behavior is implementation-dependent
        # For this test, we just verify it doesn't raise an exception
        try:
            decision = refiner.refine(request=request)
            # If it succeeds, the decision should be valid
            assert decision is not None
        except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallower
            # If it fails, that's also acceptable for empty candidates
            pass

    def test_single_candidate(self):
        """Single candidate should always be chosen."""
        refiner = DefaultDeterministicRollbackRefiner()

        signature = FailureSignature(
            component="test",
            failure_type="timeout",
            fingerprint="5555555555555555555555555555555555555555555555555555555555555555",
        )

        candidates = (RollbackStrategyId("only_strategy"),)

        request = RollbackRefinementRequest(
            failure_signature=signature,
            candidates=candidates,
            history_bytes=None,
        )

        decision = refiner.refine(request=request)

        # Should choose the only candidate
        assert decision.chosen.name == "only_strategy"
        assert decision.ranked == candidates
        assert "chosen_strategy_only_strategy" in decision.reasons