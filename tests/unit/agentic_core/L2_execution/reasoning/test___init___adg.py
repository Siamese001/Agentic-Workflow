"""Tests for L2 execution types and contracts."""

import unittest

from agentic_core.L2_execution.types.l2_execution_contract import (
    CanonicalAgentRole,
    FailureSignal,
    HealingDecision,
    HealingInput,
    HealingTier,
    L2ExecutionContext,
    L2ExecutionPhase,
    L2PhaseResult,
)


class TestL2ExecutionTypes(unittest.TestCase):
    """Test L2 execution type definitions."""

    def test_failure_signal_creation(self):
        """Test FailureSignal dataclass creation."""
        signal = FailureSignal(
            failure_type="TEST_ERROR",
            retry_count=1,
            blast_radius_estimate=0.8,
            metadata={"context": "test"},
        )
        self.assertEqual(signal.failure_type, "TEST_ERROR")
        self.assertEqual(signal.retry_count, 1)
        self.assertEqual(signal.blast_radius_estimate, 0.8)
        self.assertEqual(signal.metadata["context"], "test")

    def test_failure_signal_to_healing_input(self):
        """Test FailureSignal to HealingInput conversion."""
        signal = FailureSignal(
            failure_type="TEST_ERROR",
            retry_count=2,
            blast_radius_estimate=0.5,
        )
        healing_input = signal.to_healing_input()
        self.assertEqual(healing_input.failure_type, "TEST_ERROR")
        self.assertEqual(healing_input.blast_radius_estimate, 0.5)

    def test_healing_input_creation(self):
        """Test HealingInput dataclass creation."""
        healing_input = HealingInput(
            failure_type="RETRY_ERROR",
            blast_radius_estimate=0.3,
            metadata={"retry": 1},
        )
        self.assertEqual(healing_input.failure_type, "RETRY_ERROR")
        self.assertEqual(healing_input.blast_radius_estimate, 0.3)

    def test_healing_tier_enum(self):
        """Test HealingTier enum values."""
        self.assertEqual(HealingTier.LOCAL_AGENT.value, "local_agent")
        self.assertEqual(HealingTier.WORKFLOW.value, "workflow")
        self.assertEqual(HealingTier.ORCHESTRATION.value, "orchestration")
        self.assertEqual(HealingTier.MANUAL.value, "manual")

    def test_healing_decision_creation(self):
        """Test HealingDecision dataclass creation."""
        decision = HealingDecision(
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=["retry", "budget_ok"],
        )
        self.assertEqual(decision.tier, HealingTier.LOCAL_AGENT)
        self.assertEqual(decision.reason_codes, ["retry", "budget_ok"])

    def test_l2_execution_phase_enum(self):
        """Test L2ExecutionPhase enum has all phases."""
        phases = [p for p in L2ExecutionPhase]
        self.assertEqual(len(phases), 4)
        self.assertIn(L2ExecutionPhase.INIT, phases)
        self.assertIn(L2ExecutionPhase.EXECUTE, phases)
        self.assertIn(L2ExecutionPhase.EVALUATE_HEAL, phases)
        self.assertIn(L2ExecutionPhase.SYNTHESIZE, phases)

    def test_l2_phase_result_success(self):
        """Test L2PhaseResult for successful phase."""
        result = L2PhaseResult(
            phase=L2ExecutionPhase.INIT,
            success=True,
            output="initialized",
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output, "initialized")
        self.assertIsNone(result.failure_signal)

    def test_l2_phase_result_failure(self):
        """Test L2PhaseResult for failed phase with signal."""
        signal = FailureSignal(
            failure_type="VALIDATION_ERROR",
            retry_count=0,
        )
        result = L2PhaseResult(
            phase=L2ExecutionPhase.EXECUTE,
            success=False,
            failure_signal=signal,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.failure_signal.failure_type, "VALIDATION_ERROR")

    def test_l2_execution_context_creation(self):
        """Test L2ExecutionContext creation."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
            heal_enabled=True,
            max_retries=5,
        )
        self.assertEqual(context.agent_id, "test_agent")
        self.assertEqual(context.trace_id, "trace-123")
        self.assertTrue(context.heal_enabled)
        self.assertEqual(context.max_retries, 5)
        self.assertEqual(context.retry_count, 0)

    def test_l2_execution_context_record_phase_result(self):
        """Test recording phase result updates context."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
        )
        result = L2PhaseResult(
            phase=L2ExecutionPhase.INIT,
            success=True,
            output="done",
        )
        context.record_phase_result(result)
        self.assertIn(L2ExecutionPhase.INIT, context.phase_results)
        self.assertEqual(context.phase_results[L2ExecutionPhase.INIT], result)

    def test_l2_execution_context_record_with_failure_signal(self):
        """Test recording phase result with failure signal updates retry count."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
        )
        signal = FailureSignal(
            failure_type="RETRY_ERROR",
            retry_count=2,
        )
        result = L2PhaseResult(
            phase=L2ExecutionPhase.EXECUTE,
            success=False,
            failure_signal=signal,
        )
        context.record_phase_result(result)
        self.assertEqual(context.retry_count, 2)

    def test_should_attempt_heal_disabled(self):
        """Test should_attempt_heal returns False when healing disabled."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
            heal_enabled=False,
        )
        self.assertFalse(context.should_attempt_heal())

    def test_should_attempt_heal_budget_exhausted(self):
        """Test should_attempt_heal returns False when retry budget exhausted."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
            heal_enabled=True,
            max_retries=3,
            retry_count=3,
        )
        self.assertFalse(context.should_attempt_heal())

    def test_should_attempt_heal_no_failure(self):
        """Test should_attempt_heal returns False when no failure signal."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
            heal_enabled=True,
        )
        result = L2PhaseResult(
            phase=L2ExecutionPhase.EXECUTE,
            success=True,
        )
        context.record_phase_result(result)
        self.assertFalse(context.should_attempt_heal())

    def test_should_attempt_heal_recoverable_failure(self):
        """Test should_attempt_heal returns True for recoverable failure."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
            heal_enabled=True,
        )
        signal = FailureSignal(
            failure_type="TEMPORARY_ERROR",
            retry_count=0,
        )
        result = L2PhaseResult(
            phase=L2ExecutionPhase.EXECUTE,
            success=False,
            failure_signal=signal,
        )
        context.record_phase_result(result)
        self.assertTrue(context.should_attempt_heal())

    def test_should_attempt_heal_unrecoverable_failure(self):
        """Test should_attempt_heal returns False for unrecoverable failure."""
        context = L2ExecutionContext(
            agent_id="test_agent",
            trace_id="trace-123",
            heal_enabled=True,
        )
        signal = FailureSignal(
            failure_type="UNRECOVERABLE",
            retry_count=0,
        )
        result = L2PhaseResult(
            phase=L2ExecutionPhase.EXECUTE,
            success=False,
            failure_signal=signal,
        )
        context.record_phase_result(result)
        self.assertFalse(context.should_attempt_heal())

    def test_canonical_agent_role_enum(self):
        """Test CanonicalAgentRole enum has all roles."""
        roles = [r for r in CanonicalAgentRole]
        self.assertIn(CanonicalAgentRole.PLANNER, roles)
        self.assertIn(CanonicalAgentRole.ROUTER, roles)
        self.assertIn(CanonicalAgentRole.EXECUTION, roles)
        self.assertIn(CanonicalAgentRole.HEAL, roles)
        self.assertIn(CanonicalAgentRole.ORCHESTRATOR, roles)
        self.assertIn(CanonicalAgentRole.SAFETY, roles)
        self.assertIn(CanonicalAgentRole.OBSERVER, roles)


if __name__ == "__main__":
    unittest.main()
