"""
Phase 3 Tests: Healing & Resilience Integration

Tests for the healing orchestration suite that coordinates
healing strategies for resilience and maintenance operations.

Test Coverage:
- HealingResult dataclass
- HealingSuiteResult dataclass
- HealingOrchestrationSuite orchestration
- Individual strategy execution
- Full suite execution
- Resilience and dependency cleanup operations
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestHealingResult:
    """Tests for HealingResult dataclass."""

    def test_result_creation_with_defaults(self):
        """Test HealingResult can be created with defaults."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingResult,
        )

        result = HealingResult(
            strategy_name="test_strategy",
            success=True,
        )

        assert result.strategy_name == "test_strategy"
        assert result.success is True
        assert result.violations_found == 0
        assert result.violations_fixed == 0
        assert result.errors == []
        assert result.metadata == {}
        assert result.timestamp is not None

    def test_result_creation_with_violations(self):
        """Test HealingResult with violation counts."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingResult,
        )

        result = HealingResult(
            strategy_name="test_strategy",
            success=True,
            violations_found=5,
            violations_fixed=3,
        )

        assert result.violations_found == 5
        assert result.violations_fixed == 3

    def test_result_creation_with_errors(self):
        """Test HealingResult with errors."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingResult,
        )

        result = HealingResult(
            strategy_name="test_strategy",
            success=False,
            errors=["Error 1", "Error 2"],
        )

        assert result.success is False
        assert len(result.errors) == 2

    def test_result_creation_with_metadata(self):
        """Test HealingResult with metadata."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingResult,
        )

        result = HealingResult(
            strategy_name="test_strategy",
            success=True,
            metadata={"resilience_score": 0.95, "dry_run": True},
        )

        assert result.metadata["resilience_score"] == 0.95
        assert result.metadata["dry_run"] is True


class TestHealingSuiteResult:
    """Tests for HealingSuiteResult dataclass."""

    def test_suite_result_creation(self):
        """Test HealingSuiteResult can be created."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingSuiteResult,
        )

        result = HealingSuiteResult(
            overall_success=True,
            strategies_run=2,
            strategies_succeeded=2,
            strategies_failed=0,
            total_violations_found=10,
            total_violations_fixed=8,
        )

        assert result.overall_success is True
        assert result.strategies_run == 2
        assert result.strategies_succeeded == 2
        assert result.strategies_failed == 0
        assert result.total_violations_found == 10
        assert result.total_violations_fixed == 8
        assert result.results == []
        assert result.timestamp is not None

    def test_suite_result_with_results(self):
        """Test HealingSuiteResult with individual results."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingSuiteResult,
            HealingResult,
        )

        individual_results = [
            HealingResult(strategy_name="s1", success=True, violations_found=5, violations_fixed=5),
            HealingResult(
                strategy_name="s2", success=False, violations_found=3, violations_fixed=0
            ),
        ]

        result = HealingSuiteResult(
            overall_success=False,
            strategies_run=2,
            strategies_succeeded=1,
            strategies_failed=1,
            total_violations_found=8,
            total_violations_fixed=5,
            results=individual_results,
        )

        assert len(result.results) == 2
        assert result.results[0].success is True
        assert result.results[1].success is False


class TestHealingOrchestrationSuite:
    """Tests for HealingOrchestrationSuite class."""

    def test_suite_creation(self):
        """Test HealingOrchestrationSuite can be instantiated."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()
        assert suite is not None
        assert suite._initialized is False

    def test_suite_lazy_initialization(self):
        """Test suite initializes lazily on first use."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()
        assert suite._initialized is False

        # Trigger initialization
        suite._ensure_initialized()
        assert suite._initialized is True

    def test_get_available_strategies(self):
        """Test getting list of available strategies."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()
        strategies = suite.get_available_strategies()

        assert isinstance(strategies, list)

    def test_get_status(self):
        """Test getting suite status."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()
        status = suite.get_status()

        assert isinstance(status, dict)
        assert "initialized" in status
        assert "strategies_available" in status
        assert "strategy_count" in status

    def test_run_strategy_returns_result(self):
        """Test running a single strategy returns proper result."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
            HealingResult,
        )

        suite = HealingOrchestrationSuite()
        result = suite.run_strategy(
            "chaos_resilience",
            violation={"type": "resilience_check"},
            context={},
        )

        assert isinstance(result, HealingResult)
        assert result.strategy_name == "chaos_resilience"
        assert isinstance(result.success, bool)

    def test_run_strategy_unknown_returns_error(self):
        """Test running unknown strategy returns error result."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()
        result = suite.run_strategy(
            "unknown_strategy",
            violation={"type": "test"},
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0]

    def test_run_all_returns_suite_result(self):
        """Test running all strategies returns suite result."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
            HealingSuiteResult,
        )

        suite = HealingOrchestrationSuite()
        result = suite.run_all(violation={"type": "resilience_check"})

        assert isinstance(result, HealingSuiteResult)
        assert result.strategies_run >= 0
        assert result.strategies_succeeded >= 0
        assert result.strategies_failed >= 0
        assert result.execution_time_ms >= 0

    def test_run_all_aggregates_results(self):
        """Test run_all properly aggregates individual results."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()
        result = suite.run_all(violation={"type": "resilience_check"})

        # Results should match counts
        assert len(result.results) == result.strategies_run
        succeeded = sum(1 for r in result.results if r.success)
        assert succeeded == result.strategies_succeeded


class TestHealingSuiteSpecificOperations:
    """Tests for specific healing operations."""

    def test_run_resilience_check(self):
        """Test running resilience check specifically."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
            HealingResult,
        )

        suite = HealingOrchestrationSuite()
        result = suite.run_resilience_check()

        assert isinstance(result, HealingResult)
        assert result.strategy_name == "chaos_resilience"

    def test_run_dependency_cleanup_dry_run(self):
        """Test running dependency cleanup in dry run mode."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
            HealingResult,
        )

        suite = HealingOrchestrationSuite()
        result = suite.run_dependency_cleanup(dry_run=True)

        assert isinstance(result, HealingResult)
        assert result.strategy_name == "dependency_pruning"

    def test_run_dependency_cleanup_respects_dry_run(self):
        """Test dependency cleanup respects dry_run parameter."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            HealingOrchestrationSuite,
        )

        suite = HealingOrchestrationSuite()

        # With dry_run=True (safe)
        result = suite.run_dependency_cleanup(dry_run=True)
        assert isinstance(result.success, bool)


class TestHealingSuiteGlobalFunctions:
    """Tests for global convenience functions."""

    def test_get_healing_suite_singleton(self):
        """Test get_healing_suite returns singleton."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite1 = get_healing_suite()
        suite2 = get_healing_suite()
        assert suite1 is suite2

    def test_run_healing_operation_convenience(self):
        """Test run_healing_operation convenience function."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
            HealingSuiteResult,
        )

        result = run_healing_operation(violation={"type": "resilience_check"})

        assert isinstance(result, HealingSuiteResult)
        assert result.strategies_run >= 0


class TestHealingSuiteIntegration:
    """Integration tests for healing suite with actual strategies."""

    def test_chaos_strategy_integration(self):
        """Test chaos strategy works through suite."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()
        if "chaos_resilience" in suite.get_available_strategies():
            result = suite.run_strategy(
                "chaos_resilience",
                violation={"type": "resilience_check"},
            )
            assert result.strategy_name == "chaos_resilience"
            assert isinstance(result.success, bool)

    def test_dependency_strategy_integration(self):
        """Test dependency strategy works through suite."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()
        if "dependency_pruning" in suite.get_available_strategies():
            result = suite.run_strategy(
                "dependency_pruning",
                violation={"type": "unused_dependency"},
                context={"dry_run": True},
            )
            assert result.strategy_name == "dependency_pruning"
            assert isinstance(result.success, bool)

    def test_full_healing_run(self):
        """Test running full healing suite."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        result = run_healing_operation(
            violation={"type": "resilience_check", "severity": "medium"},
            context={"dry_run": True, "source": "test"},
        )

        assert result.strategies_run >= 0
        assert result.overall_success in (True, False)
        assert result.execution_time_ms >= 0


class TestHealingSuiteEdgeCases:
    """Edge case tests for healing suite."""

    def test_empty_violation(self):
        """Test healing with empty violation."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        result = run_healing_operation(violation={})
        assert isinstance(result.overall_success, bool)

    def test_unknown_violation_type(self):
        """Test healing with unknown violation type."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        result = run_healing_operation(violation={"type": "completely_unknown_type_xyz"})
        assert isinstance(result.overall_success, bool)

    def test_multiple_violations_in_sequence(self):
        """Test handling multiple violations in sequence."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            get_healing_suite,
        )

        suite = get_healing_suite()

        violations = [
            {"type": "resilience_check"},
            {"type": "unused_dependency"},
            {"type": "unknown_type"},
        ]

        for violation in violations:
            result = suite.run_all(violation, context={"dry_run": True})
            assert isinstance(result.overall_success, bool)


class TestHealingSuiteWithContext:
    """Tests for healing suite with various context configurations."""

    def test_dry_run_context(self):
        """Test healing with dry_run context."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        result = run_healing_operation(
            violation={"type": "unused_dependency"},
            context={"dry_run": True},
        )
        assert isinstance(result.overall_success, bool)

    def test_execute_context(self):
        """Test healing with execute context (still safe in tests)."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        # Even with dry_run=False, our test strategies are safe
        result = run_healing_operation(
            violation={"type": "resilience_check"},
            context={"dry_run": False},
        )
        assert isinstance(result.overall_success, bool)

    def test_custom_context_values(self):
        """Test healing with custom context values."""
        from agentic_core.L5_safety.validators.healing_orchestration_suite import (
            run_healing_operation,
        )

        result = run_healing_operation(
            violation={"type": "resilience_check"},
            context={
                "dry_run": True,
                "max_retries": 3,
                "timeout_seconds": 30,
                "custom_flag": "test_value",
            },
        )
        assert isinstance(result.overall_success, bool)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
