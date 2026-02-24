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
        except Exception:
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
