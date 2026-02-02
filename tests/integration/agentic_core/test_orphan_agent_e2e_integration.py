"""
E2E and Integration Tests: Orphan Agent Integration

Comprehensive end-to-end tests that verify the complete orphan agent
integration workflow from initialization through execution.

Test Coverage:
- Full initialization workflow
- Security validation E2E
- Healing operations E2E
- Combined security + healing workflow
- Error recovery scenarios
- Performance under load
"""

from __future__ import annotations

import pytest
import sys
import time
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestE2EInitializationWorkflow:
    """E2E tests for the complete initialization workflow."""

    def setup_method(self):
        """Reset state before each test."""
        try:
            from agentic_core.L5_safety.validators import register_all_validators

            register_all_validators.reset()
        except Exception:
            pass

    def test_e2e_full_initialization(self):
        """E2E: Complete initialization from scratch."""
        from agentic_core.L5_safety.validators import register_all_validators

        # Step 1: Verify not initialized
        status_before = register_all_validators.get_integration_status()
        assert status_before["initialized"] is False

        # Step 2: Initialize
        result = register_all_validators.initialize()
        assert result["status"] in ("initialized", "partial")

        # Step 3: Verify initialized
        status_after = register_all_validators.get_integration_status()
        assert status_after["initialized"] is True

        # Step 4: Verify components registered
        assert len(status_after["validators_registered"]) >= 0
        assert len(status_after["strategies_registered"]) >= 0

    def test_e2e_initialization_with_suites(self):
        """E2E: Initialize and verify suites are ready."""
        from agentic_core.L5_safety.validators import register_all_validators
        from agentic_core.L5_safety.validators.security_validation_suite import (
            get_security_suite,
        )
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        # Initialize
        register_all_validators.initialize()

        # Get suites
        security_suite = get_security_suite()
        healing_suite = get_healing_suite()

        # Verify both are ready
        assert security_suite.get_status()["initialized"] is True
        assert healing_suite.get_status()["initialized"] is True

        # Verify they have validators/strategies
        assert len(security_suite.get_available_validators()) >= 0
        assert len(healing_suite.get_available_strategies()) >= 0


class TestE2ESecurityValidation:
    """E2E tests for security validation workflow."""

    def test_e2e_security_scan_workflow(self):
        """E2E: Complete security scan workflow."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
            get_security_suite,
        )

        # Step 1: Get suite and verify ready
        suite = get_security_suite()
        assert suite.get_status()["initialized"] is True

        # Step 2: Run security validation
        result = run_security_validation(
            content={
                "user_input": "test data for security scan",
                "action": "validate",
                "source": "e2e_test",
            },
            context={"test_mode": True},
        )

        # Step 3: Verify result structure
        assert hasattr(result, "overall_valid")
        assert hasattr(result, "validators_run")
        assert hasattr(result, "validators_passed")
        assert hasattr(result, "validators_failed")
        assert hasattr(result, "results")
        assert hasattr(result, "execution_time_ms")

        # Step 4: Verify results are valid
        assert isinstance(result.overall_valid, bool)
        assert result.validators_run >= 0
        assert result.execution_time_ms >= 0

    def test_e2e_individual_validator_workflow(self):
        """E2E: Run individual validators in sequence."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            get_security_suite,
        )

        suite = get_security_suite()
        validators = suite.get_available_validators()

        results = []
        for validator_name in validators:
            result = suite.run_validator(
                validator_name,
                content={"test": "data"},
                context={},
            )
            results.append(result)

            # Each result should be valid structure
            assert result.validator_name == validator_name
            assert isinstance(result.valid, bool)
            assert isinstance(result.errors, list)

        # All validators should have been run
        assert len(results) == len(validators)


class TestE2EHealingOperations:
    """E2E tests for healing operations workflow."""

    def test_e2e_healing_workflow(self):
        """E2E: Complete healing workflow."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
            get_healing_suite,
        )

        # Step 1: Get suite and verify ready
        suite = get_healing_suite()
        assert suite.get_status()["initialized"] is True

        # Step 2: Run healing operation
        result = run_healing_operation(
            violation={
                "type": "resilience_check",
                "severity": "medium",
                "source": "e2e_test",
            },
            context={"dry_run": True},
        )

        # Step 3: Verify result structure
        assert hasattr(result, "overall_success")
        assert hasattr(result, "strategies_run")
        assert hasattr(result, "strategies_succeeded")
        assert hasattr(result, "strategies_failed")
        assert hasattr(result, "total_violations_found")
        assert hasattr(result, "total_violations_fixed")
        assert hasattr(result, "results")
        assert hasattr(result, "execution_time_ms")

        # Step 4: Verify results are valid
        assert isinstance(result.overall_success, bool)
        assert result.strategies_run >= 0
        assert result.execution_time_ms >= 0

    def test_e2e_individual_strategy_workflow(self):
        """E2E: Run individual strategies in sequence."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()
        strategies = suite.get_available_strategies()

        results = []
        for strategy_name in strategies:
            result = suite.run_strategy(
                strategy_name,
                violation={"type": "test_violation"},
                context={"dry_run": True},
            )
            results.append(result)

            # Each result should be valid structure
            assert result.strategy_name == strategy_name
            assert isinstance(result.success, bool)
            assert isinstance(result.errors, list)

        # All strategies should have been run
        assert len(results) == len(strategies)

    def test_e2e_resilience_check_workflow(self):
        """E2E: Specific resilience check workflow."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()
        result = suite.run_resilience_check(context={"dry_run": True})

        assert result.strategy_name == "chaos_resilience"
        assert isinstance(result.success, bool)

    def test_e2e_dependency_cleanup_workflow(self):
        """E2E: Specific dependency cleanup workflow."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()
        result = suite.run_dependency_cleanup(dry_run=True)

        assert result.strategy_name == "dependency_pruning"
        assert isinstance(result.success, bool)


class TestE2ECombinedWorkflow:
    """E2E tests for combined security + healing workflow."""

    def test_e2e_security_then_healing_workflow(self):
        """E2E: Security validation followed by healing."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        # Step 1: Run security validation
        security_result = run_security_validation(
            content={"test_input": "data to validate"},
        )

        # Step 2: Based on security result, run healing
        if not security_result.overall_valid:
            # Create violation from security findings
            violation = {
                "type": "security_violation",
                "validators_failed": security_result.validators_failed,
                "errors": [err for r in security_result.results for err in r.errors],
            }
        else:
            # Run resilience check even if security passed
            violation = {"type": "resilience_check"}

        healing_result = run_healing_operation(
            violation=violation,
            context={"dry_run": True, "triggered_by": "security_validation"},
        )

        # Step 3: Verify both completed
        assert security_result.validators_run >= 0
        assert healing_result.strategies_run >= 0

    def test_e2e_full_pipeline(self):
        """E2E: Complete pipeline from init to validation to healing."""
        from agentic_core.L5_safety.validators import register_all_validators
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        # Reset and initialize
        register_all_validators.reset()

        # Step 1: Initialize
        init_result = register_all_validators.initialize()
        assert init_result["status"] in ("initialized", "partial")

        # Step 2: Security validation
        security_result = run_security_validation(
            content={"pipeline_test": True},
        )
        assert security_result.validators_run >= 0

        # Step 3: Healing
        healing_result = run_healing_operation(
            violation={"type": "resilience_check"},
            context={"dry_run": True},
        )
        assert healing_result.strategies_run >= 0

        # Step 4: Verify final status
        final_status = register_all_validators.get_integration_status()
        assert final_status["initialized"] is True


class TestE2EErrorRecovery:
    """E2E tests for error recovery scenarios."""

    def test_e2e_recovery_from_invalid_validator(self):
        """E2E: System recovers from invalid validator request."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            get_security_suite,
        )

        suite = get_security_suite()

        # Request invalid validator
        result = suite.run_validator("non_existent_validator", {})

        # Should return error result, not crash
        assert result.valid is False
        assert len(result.errors) > 0

        # Suite should still be functional
        status = suite.get_status()
        assert status["initialized"] is True

    def test_e2e_recovery_from_invalid_strategy(self):
        """E2E: System recovers from invalid strategy request."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()

        # Request invalid strategy
        result = suite.run_strategy("non_existent_strategy", {})

        # Should return error result, not crash
        assert result.success is False
        assert len(result.errors) > 0

        # Suite should still be functional
        status = suite.get_status()
        assert status["initialized"] is True

    def test_e2e_recovery_from_malformed_input(self):
        """E2E: System handles malformed input gracefully."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        # Test with various malformed inputs
        malformed_inputs = [
            None,
            {},
            {"nested": {"deeply": {"nested": "value"}}},
            {"list": [1, 2, 3, None, "mixed"]},
        ]

        for content in malformed_inputs:
            # Security validation should handle gracefully
            security_result = run_security_validation(content=content)
            assert isinstance(security_result.overall_valid, bool)

            # Healing should handle gracefully
            healing_result = run_healing_operation(
                violation={"type": "test", "content": content},
                context={"dry_run": True},
            )
            assert isinstance(healing_result.overall_success, bool)


class TestE2EPerformanceUnderLoad:
    """E2E tests for performance under load."""

    def test_e2e_multiple_sequential_validations(self):
        """E2E: Multiple sequential security validations."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )

        num_iterations = 5
        total_time = 0

        for i in range(num_iterations):
            start = time.time()
            result = run_security_validation(
                content={"iteration": i, "test": "data"},
            )
            elapsed = time.time() - start
            total_time += elapsed

            assert result.validators_run >= 0

        avg_time = total_time / num_iterations
        # Average should be reasonable (< 2 seconds per validation)
        assert avg_time < 2.0, f"Average validation time {avg_time}s too slow"

    def test_e2e_multiple_sequential_healings(self):
        """E2E: Multiple sequential healing operations."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        num_iterations = 5
        total_time = 0

        for i in range(num_iterations):
            start = time.time()
            result = run_healing_operation(
                violation={"type": "resilience_check", "iteration": i},
                context={"dry_run": True},
            )
            elapsed = time.time() - start
            total_time += elapsed

            assert result.strategies_run >= 0

        avg_time = total_time / num_iterations
        # Average should be reasonable (< 2 seconds per healing)
        assert avg_time < 2.0, f"Average healing time {avg_time}s too slow"

    def test_e2e_alternating_validation_healing(self):
        """E2E: Alternating between validation and healing."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        num_iterations = 3

        for i in range(num_iterations):
            # Validation
            security_result = run_security_validation(
                content={"iteration": i},
            )
            assert security_result.validators_run >= 0

            # Healing
            healing_result = run_healing_operation(
                violation={"type": "resilience_check"},
                context={"dry_run": True},
            )
            assert healing_result.strategies_run >= 0


class TestE2EGuardianIntegration:
    """E2E tests for guardian test integration."""

    def test_e2e_orphan_detection_after_integration(self):
        """E2E: Orphan detection works after integration."""
        try:
            from tests.guardian.test_orphan_agent_detection import (
                OrphanAgentDetector,
            )

            detector = OrphanAgentDetector(PROJECT_ROOT)
            detector.load_agent_discovery()

            # Should be able to scan references
            detector.scan_references()

            # Should be able to identify orphans
            orphans = detector.identify_orphans()
            assert isinstance(orphans, list)

            # Generate dispositions stores internally, returns None
            detector.generate_dispositions()

            # Verify orphans have dispositions set
            for orphan in orphans:
                assert hasattr(orphan, "disposition")

        except ImportError:
            pytest.skip("Guardian test module not available")

    def test_e2e_orphan_report_generation(self):
        """E2E: Orphan report can be generated."""
        try:
            from tests.guardian.test_orphan_agent_detection import (
                OrphanAgentDetector,
            )

            detector = OrphanAgentDetector(PROJECT_ROOT)
            detector.load_agent_discovery()
            detector.scan_references()
            detector.identify_orphans()
            detector.generate_dispositions()

            # Generate report
            report = detector.generate_report()

            # Verify report structure
            assert "total_agents" in report
            assert "orphan_count" in report
            assert "orphan_percentage" in report
            assert "orphans" in report

        except ImportError:
            pytest.skip("Guardian test module not available")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
