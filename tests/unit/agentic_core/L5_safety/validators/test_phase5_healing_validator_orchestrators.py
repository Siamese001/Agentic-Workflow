"""
Test Suite for Phase 5 Healing and Validator Orchestrators

Tests TC-PHASE5-001 through TC-PHASE5-004:
- Healing strategy dispatch
- Recursion guard
- Validator registry
- Audit rotation (memory safety)
"""

import pytest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


class TestHealingSovereignOrchestrator:
    """Tests for HealingSovereignOrchestrator."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()

    def teardown_method(self):
        """Clean up singleton after each test."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()

    @pytest.mark.asyncio
    async def test_tc_phase5_001_heal_strategy_dispatch(self):
        """
        TC-PHASE5-001: Heal Strategy Dispatch

        Procedure:
        1. Create a mock strategy returning True for can_heal
        2. Register it with HealingSovereignOrchestrator
        3. Call heal(violation)

        Expected:
        - Strategy heal method called
        - Audit log contains entry
        - Returns {"status": "healed"}
        """
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()

        # Create mock strategy
        mock_strategy = MagicMock()
        mock_strategy.can_heal.return_value = True
        mock_strategy.heal.return_value = {"success": True, "fixed": "test_issue"}

        # Register strategy
        orchestrator.register_strategy("test_strategy", mock_strategy)

        # Execute heal
        violation = {"type": "test_violation", "details": "something wrong"}
        result = await orchestrator.heal(violation)

        # Assertions
        assert result["status"] == "healed", f"Expected 'healed', got {result['status']}"
        assert result["strategy"] == "test_strategy"
        mock_strategy.can_heal.assert_called_once_with(violation)
        mock_strategy.heal.assert_called_once()

        # Verify audit log
        assert len(orchestrator.audit_log) == 1
        assert orchestrator.audit_log[0]["strategy"] == "test_strategy"
        assert orchestrator.audit_log[0]["success"] is True

        # Verify stats
        assert orchestrator.operation_stats["total_heals"] == 1
        assert orchestrator.operation_stats["successful_heals"] == 1

    @pytest.mark.asyncio
    async def test_tc_phase5_002_recursion_guard(self):
        """
        TC-PHASE5-002: Recursion Guard

        Procedure:
        1. Create a strategy that would call heal recursively
        2. Set MAX_HEALING_ATTEMPTS = 2 via env
        3. Trigger strategy with deep context

        Expected:
        - Returns "failed" with reason "max_depth_exceeded"
        - Does not loop infinitely
        """
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            get_healing_orchestrator,
        )
        from unittest import mock

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_HEALING_ATTEMPTS": "2"}):
            orchestrator = get_healing_orchestrator()

            # Simulate already being at max depth
            violation = {"type": "recursive_issue"}
            context = {"_healing_depth": 2}  # Already at max

            result = await orchestrator.heal(violation, context)

            assert result["status"] == "failed"
            assert result["reason"] == "max_depth_exceeded"

    @pytest.mark.asyncio
    async def test_recursion_depth_increments(self):
        """Test that healing depth increments correctly."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()
        orchestrator.MAX_HEALING_ATTEMPTS = 5

        captured_context = {}

        # Create strategy that captures context
        mock_strategy = MagicMock()
        mock_strategy.can_heal.return_value = True

        def capture_heal(violation, context):
            captured_context.update(context)
            return {"success": True}

        mock_strategy.heal.side_effect = capture_heal

        orchestrator.register_strategy("capture_strategy", mock_strategy)

        # Call with initial depth 0
        await orchestrator.heal({"type": "test"}, {"_healing_depth": 0})

        # Context should have incremented depth
        assert captured_context["_healing_depth"] == 1

    @pytest.mark.asyncio
    async def test_no_strategy_found(self):
        """Test behavior when no strategy can heal the violation."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()

        # Create strategy that can't heal
        mock_strategy = MagicMock()
        mock_strategy.can_heal.return_value = False

        orchestrator.register_strategy("unhelpful_strategy", mock_strategy)

        result = await orchestrator.heal({"type": "unknown_issue"})

        assert result["status"] == "no_strategy"
        assert "violation" in result

    def test_healing_singleton_reset(self):
        """Test that reset_instance works."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
            get_healing_orchestrator,
        )

        orch1 = get_healing_orchestrator()
        orch2 = get_healing_orchestrator()

        assert id(orch1) == id(orch2)

        HealingSovereignOrchestrator.reset_instance()

        orch3 = get_healing_orchestrator()
        assert id(orch3) != id(orch1)


class TestValidatorOrchestrator:
    """Tests for ValidatorOrchestrator."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()

    def teardown_method(self):
        """Clean up singleton after each test."""
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()

    @pytest.mark.asyncio
    async def test_tc_phase5_003_validator_registry(self):
        """
        TC-PHASE5-003: Validator Registry

        Procedure:
        1. Register a mock validator "code_check"
        2. Call validate(content, "code_check")
        3. Call validate(content, "missing_check")

        Expected:
        - First call succeeds (calls mock)
        - Second call returns error "Validator not found"
        """
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import (
            get_validator_orchestrator,
        )

        orchestrator = get_validator_orchestrator()

        # Create mock validator
        mock_validator = MagicMock()
        mock_validator.validate.return_value = {"valid": True, "errors": []}

        # Register validator
        orchestrator.register_validator("code_check", mock_validator)

        # Test registered validator
        result1 = await orchestrator.validate("some code", "code_check")

        assert result1["valid"] is True
        mock_validator.validate.assert_called_once()

        # Test missing validator
        result2 = await orchestrator.validate("some code", "missing_check")

        assert result2["valid"] is False
        assert "Validator missing_check not found" in result2["errors"]

    def test_tc_phase5_004_audit_rotation(self):
        """
        TC-PHASE5-004: Audit Rotation

        Procedure:
        1. Set MAX_AUDIT_LOG_SIZE = 5 via env
        2. Run 10 validations (via _audit directly)
        3. Check log length

        Expected:
        - Length <= 5
        - Oldest entries pruned
        - Verifies memory safety
        """
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import (
            get_validator_orchestrator,
        )
        from unittest import mock

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "5"}):
            orchestrator = get_validator_orchestrator()

            # Flood the audit log
            for i in range(10):
                orchestrator._audit(f"validator_{i}", True, 10.0 + i)

            # Verify FIFO rotation
            assert len(orchestrator.audit_log) <= 5, (
                f"Expected max 5, got {len(orchestrator.audit_log)}"
            )
            assert orchestrator.operation_stats["total_validations"] == 10

            # Verify oldest entries were pruned
            validators_in_log = [entry["validator"] for entry in orchestrator.audit_log]
            assert "validator_0" not in validators_in_log, "Oldest entry should be pruned"

    def test_healing_audit_rotation(self):
        """Test FIFO rotation in healing orchestrator audit log."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
            get_healing_orchestrator,
        )
        from unittest import mock

        HealingSovereignOrchestrator.reset_instance()

        with mock.patch.dict(os.environ, {"SOVEREIGN_MAX_AUDIT_LOG_SIZE": "5"}):
            orchestrator = get_healing_orchestrator()

            # Flood the log
            for i in range(10):
                orchestrator._audit(f"strategy_{i}", f"type_{i}", True, 10.0 + i)

            assert len(orchestrator.audit_log) <= 5
            assert orchestrator.operation_stats["total_heals"] == 10

        HealingSovereignOrchestrator.reset_instance()

    def test_validator_singleton_reset(self):
        """Test that reset_instance works for ValidatorOrchestrator."""
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import (
            ValidatorOrchestrator,
            get_validator_orchestrator,
        )

        orch1 = get_validator_orchestrator()
        orch2 = get_validator_orchestrator()

        assert id(orch1) == id(orch2)

        ValidatorOrchestrator.reset_instance()

        orch3 = get_validator_orchestrator()
        assert id(orch3) != id(orch1)

    @pytest.mark.asyncio
    async def test_validator_exception_handling(self):
        """Test that validator exceptions are caught and logged."""
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import (
            get_validator_orchestrator,
        )

        orchestrator = get_validator_orchestrator()

        # Create validator that raises
        mock_validator = MagicMock()
        mock_validator.validate.side_effect = ValueError("Validation exploded")

        orchestrator.register_validator("exploding_validator", mock_validator)

        result = await orchestrator.validate("content", "exploding_validator")

        assert result["valid"] is False
        assert "Validation exploded" in result["errors"][0]
        assert orchestrator.operation_stats["errors"] == 1


class TestHealingStrategyMixin:
    """Tests for HealingStrategyMixin."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()

    def teardown_method(self):
        from agentic_core.L5_safety.validators.HealingSovereignOrchestrator import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()

    def test_mixin_lazy_loads_orchestrator(self):
        """Test that mixin lazy-loads the healing orchestrator."""

        class TestAgent(HealingStrategyMixin):
            pass

        agent = TestAgent()

        assert agent._healing_orchestrator is None

        orchestrator = agent.healing_orchestrator

        assert orchestrator is not None
        assert agent._healing_orchestrator is orchestrator


class TestValidatorMixin:
    """Tests for ValidatorMixin."""

    def setup_method(self):
        """Reset singleton before each test."""
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()

    def teardown_method(self):
        from agentic_core.L5_safety.validators.ValidatorOrchestrator import ValidatorOrchestrator

        ValidatorOrchestrator.reset_instance()

    def test_mixin_lazy_loads_orchestrator(self):
        """Test that mixin lazy-loads the validator orchestrator."""

        class TestAgent(ValidatorMixin):
            pass

        agent = TestAgent()

        assert agent._validator_orchestrator is None

        orchestrator = agent.validator_orchestrator

        assert orchestrator is not None
        assert agent._validator_orchestrator is orchestrator


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
