"""
Authority Hardening Enforcement Tests

Tests for L1 purity, L2 envelope separation, and L5 Guardian enforcement.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L1_cognition.types.execution_intent import (
    ExecutionIntent,
    L1Result,
    assert_l1_purity,
    get_mutation_count,
    increment_mutation_guard,
    reset_mutation_guard,
)
from agentic_core.L2_execution.enforcement.durable_write_wrapper import (
    durable_write,
    reset_mutation_counter,
    set_phase,
)
from agentic_core.L2_execution.enforcement.durable_write_wrapper import (
    get_mutation_count as get_durable_mutation_count,
)
from agentic_core.L5_safety.reasoning.guardian_decision import (
    GuardianDecision,
    GuardianViolationError,
    L5Guardian,
)


class TestL1Purity:
    """Test L1 cognition purity enforcement."""

    def test_execution_intent_creation(self) -> None:
        """Test ExecutionIntent dataclass creation."""
        intent = ExecutionIntent(
            tool_name="test_tool",
            args={"param": "value"},
            metadata={"trace_id": "test"},
            requires_commit=True,
        )

        assert intent.tool_name == "test_tool"
        assert intent.requires_commit is True

    def test_l1_result_creation(self) -> None:
        """Test L1Result with execution intents."""
        intents = [ExecutionIntent("tool1", {}, {})]
        result = L1Result(
            success=True,
            output="test_output",
            execution_intents=intents,
        )

        assert result.success is True
        assert len(result.execution_intents) == 1

    def test_assert_l1_purity_passes(self) -> None:
        """Test purity assertion passes for clean instances."""
        clean_instance = Mock()
        del clean_instance.redis
        del clean_instance.pinecone
        del clean_instance.subprocess
        del clean_instance.filesystem

        # Should not raise
        assert_l1_purity(clean_instance)

    def test_assert_l1_purity_fails(self) -> None:
        """Test purity assertion fails for instances with mutation capabilities."""
        dirty_instance = Mock()
        dirty_instance.redis = Mock()

        with pytest.raises(AssertionError, match="L1 instance cannot have redis client"):
            assert_l1_purity(dirty_instance)

    def test_mutation_guard_tracking(self) -> None:
        """Test global mutation guard tracking."""
        reset_mutation_guard()

        initial_count = get_mutation_count()
        assert initial_count == 0

        increment_mutation_guard()
        assert get_mutation_count() == 1

        increment_mutation_guard()
        assert get_mutation_count() == 2


class TestL2Envelope:
    """Test L2 explicit envelope separation."""

    def test_durable_write_enforces_phase(self) -> None:
        """Test durable write wrapper enforces L2.2 phase only."""
        mock_operation = Mock(return_value="success")

        # Should fail in wrong phase
        set_phase("L2.1")
        with pytest.raises(AssertionError, match="Durable write attempted in phase L2.1"):
            durable_write(mock_operation)

        # Should succeed in L2.2
        set_phase("L2.2")
        result = durable_write(mock_operation)
        assert result == "success"
        assert get_durable_mutation_count() > 0

    def test_mutation_counter_tracking(self) -> None:
        """Test mutation counter tracks writes correctly."""
        reset_mutation_counter()
        set_phase("L2.2")

        mock_operation = Mock()

        initial_count = get_durable_mutation_count()
        durable_write(mock_operation)
        assert get_durable_mutation_count() == initial_count + 1

        durable_write(mock_operation)
        durable_write(mock_operation)
        assert get_durable_mutation_count() == initial_count + 3


class TestL5Guardian:
    """Test L5 active Guardian enforcement."""

    def test_guardian_decision_creation(self) -> None:
        """Test GuardianDecision creation and serialization."""
        decision = GuardianDecision(
            allow=True,
            escalate=False,
            violations=[],
            budget_remaining=1000,
            policy_version="1.0",
        )

        serialized = decision.to_dict()
        assert serialized["allow"] is True
        assert serialized["policy_version"] == "1.0"

    def test_guardian_allows_valid_execution(self) -> None:
        """Test Guardian allows valid execution."""
        guardian = L5Guardian()

        manifest = Mock()
        manifest.tool_name = "file_read"
        manifest.token_usage = 100
        manifest.agent_layer = "L1_cognition"
        manifest.required_permission = "read"

        decision = guardian.validate(manifest, None, "1.0")

        assert decision.allow is True
        assert decision.escalate is False
        assert len(decision.violations) == 0

    def test_guardian_blocks_disallowed_tool(self) -> None:
        """Test Guardian blocks disallowed tools."""
        guardian = L5Guardian()

        manifest = Mock()
        manifest.tool_name = "malicious_tool"
        manifest.token_usage = 100
        manifest.agent_layer = "L1_cognition"
        manifest.required_permission = "read"

        decision = guardian.validate(manifest, None, "1.0")

        assert decision.allow is False
        assert "malicious_tool" in str(decision.violations)

    def test_guardian_blocks_excess_budget(self) -> None:
        """Test Guardian blocks excessive token usage."""
        guardian = L5Guardian()

        manifest = Mock()
        manifest.tool_name = "file_read"
        manifest.token_usage = 2000000  # Exceeds budget
        manifest.agent_layer = "L1_cognition"
        manifest.required_permission = "read"

        decision = guardian.validate(manifest, None, "1.0")

        assert decision.allow is False
        assert decision.escalate is True
        assert decision.budget_remaining == 0

    def test_guardian_blocks_unauthorized_agent(self) -> None:
        """Test Guardian blocks unauthorized agent permissions."""
        guardian = L5Guardian()

        manifest = Mock()
        manifest.tool_name = "file_read"
        manifest.token_usage = 100
        manifest.agent_layer = "L1_cognition"
        manifest.required_permission = "write"  # L1 cannot write

        decision = guardian.validate(manifest, None, "1.0")

        assert decision.allow is False
        assert "lacks permission" in str(decision.violations)

    def test_guardian_violation_error(self) -> None:
        """Test GuardianViolationError creation."""
        decision = GuardianDecision(
            allow=False,
            escalate=False,
            violations=["test violation"],
            budget_remaining=1000,
            policy_version="1.0",
        )

        error = GuardianViolationError(decision)
        assert "test violation" in str(error)
        assert error.decision == decision


class TestIntegration:
    """Integration tests for authority hardening."""

    def test_no_durable_writes_outside_commit(self) -> None:
        """Test that durable writes fail outside L2.2."""
        reset_mutation_counter()

        # Test all phases except L2.2
        for phase in ["L2.0", "L2.1", "L2.3", "UNKNOWN"]:
            set_phase(phase)
            mock_operation = Mock()

            with pytest.raises(AssertionError):
                durable_write(mock_operation)

    def test_atomicity_and_rollback_integrity(self) -> None:
        """Test atomic snapshot and rollback integrity."""
        # This would test the full snapshot/rollback mechanism
        # Simplified version for demonstration
        reset_mutation_counter()
        set_phase("L2.2")

        mock_operation = Mock(side_effect=["success", "failure"])

        # First operation succeeds
        result1 = durable_write(mock_operation)
        assert result1 == "success"
        assert get_durable_mutation_count() == 1

        # Second operation fails but mutation count still increments
        # In real implementation, rollback would restore state
        try:
            durable_write(mock_operation, raise_exception=True)
        except Exception:
            pass  # Expected failure

        # Rollback logic would restore to initial state
        # This is a simplified test - full implementation would verify snapshots

    def test_healing_cannot_mutate_state(self) -> None:
        """Test healing loop cannot perform mutations."""
        reset_mutation_counter()
        set_phase("L2.3")  # Healing phase

        mock_operation = Mock()

        # Healing should not be able to perform durable writes
        with pytest.raises(AssertionError, match="Durable write attempted in phase L2.3"):
            durable_write(mock_operation)

        # Mutation count should remain unchanged
        assert get_durable_mutation_count() == 0
