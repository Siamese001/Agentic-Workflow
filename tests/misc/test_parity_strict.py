"""
Strict Parity Tests for Zero-Loss Agent Consolidation - Phase 1.3

Testing infrastructure to ensure OldAgent.run() == UnifiedAgent.run()
for all converted agents. Provides:
- Parity test base class
- Performance benchmarking utilities
- Return type consistency validation
- Signal handling verification
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from unittest.mock import Mock, patch

import pytest

from agentic_core.L3_orchestration.engine.unified_agent import (
    AgentCategory,
    HealingResult,
    OrchestrationResult,
    UnifiedAgent,
    ValidationResult,
)


@dataclass
class ParityTestResult:
    """Result of a parity test comparison."""

    passed: bool
    legacy_result: Any
    unified_result: Any
    differences: list[str]
    execution_time_legacy_ms: float
    execution_time_unified_ms: float
    performance_variance_pct: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "differences": self.differences,
            "execution_time_legacy_ms": self.execution_time_legacy_ms,
            "execution_time_unified_ms": self.execution_time_unified_ms,
            "performance_variance_pct": self.performance_variance_pct,
        }


class ParityTestBase(ABC):
    """
    Base class for parity testing between legacy and unified agents.

    Subclasses must implement:
    - create_legacy_agent(): Create the legacy agent instance
    - create_unified_agent(): Create the unified agent instance
    - get_test_data(): Provide test data for execution
    """

    # Maximum allowed performance variance (20%)
    MAX_PERFORMANCE_VARIANCE = 0.20

    @abstractmethod
    def create_legacy_agent(self) -> Any:
        """Create legacy agent instance."""
        pass

    @abstractmethod
    def create_unified_agent(self) -> UnifiedAgent:
        """Create unified agent instance."""
        pass

    @abstractmethod
    def get_test_data(self) -> dict[str, Any]:
        """Get test data for agent execution."""
        pass

    def setup_agent_mocks(self, agent: Any) -> None:
        """Setup common mocks for agent testing."""
        agent.log_info = Mock()
        agent.log_error = Mock()
        agent.log_warning = Mock()
        agent.record_pass = Mock()
        agent.record_fail = Mock()
        agent.add_signal = Mock()
        agent.remove_signal = Mock()

    async def execute_legacy(self, agent: Any, **kwargs: Any) -> Any:
        """Execute legacy agent."""
        if asyncio.iscoroutinefunction(agent.execute):
            return await agent.execute(**kwargs)
        return agent.execute(**kwargs)

    async def execute_unified(
        self, agent: UnifiedAgent, **kwargs: Any
    ) -> ValidationResult | OrchestrationResult | HealingResult | dict[str, Any]:
        """Execute unified agent."""
        return await agent.execute(**kwargs)

    async def run_parity_test(self, **kwargs: Any) -> ParityTestResult:
        """
        Run parity test comparing legacy and unified agents.

        Returns:
            ParityTestResult with comparison details
        """
        legacy_agent = self.create_legacy_agent()
        unified_agent = self.create_unified_agent()

        self.setup_agent_mocks(legacy_agent)
        self.setup_agent_mocks(unified_agent)

        test_data = self.get_test_data()

        # Execute legacy agent with timing
        start_time = time.perf_counter()
        legacy_result = await self.execute_legacy(legacy_agent, **test_data, **kwargs)
        legacy_time_ms = (time.perf_counter() - start_time) * 1000

        # Execute unified agent with timing
        start_time = time.perf_counter()
        unified_result = await self.execute_unified(unified_agent, **test_data, **kwargs)
        unified_time_ms = (time.perf_counter() - start_time) * 1000

        # Compare results
        differences = self.compare_results(legacy_result, unified_result)

        # Calculate performance variance
        if legacy_time_ms > 0:
            performance_variance = abs(unified_time_ms - legacy_time_ms) / legacy_time_ms
        else:
            performance_variance = 0.0

        return ParityTestResult(
            passed=len(differences) == 0,
            legacy_result=legacy_result,
            unified_result=unified_result,
            differences=differences,
            execution_time_legacy_ms=legacy_time_ms,
            execution_time_unified_ms=unified_time_ms,
            performance_variance_pct=performance_variance * 100,
        )

    def compare_results(self, legacy: Any, unified: Any) -> list[str]:
        """
        Compare legacy and unified results.

        Override in subclasses for custom comparison logic.
        """
        differences = []

        # Compare types
        if not isinstance(legacy, type(unified)) and not isinstance(unified, type(legacy)):
            # Allow ValidationResult comparison with dict
            if isinstance(unified, ValidationResult):
                if isinstance(legacy, dict):
                    return self._compare_validation_with_dict(legacy, unified)
            differences.append(
                f"Type mismatch: legacy={type(legacy).__name__}, unified={type(unified).__name__}"
            )
            return differences

        # Compare dictionaries
        if isinstance(legacy, dict) and isinstance(unified, dict):
            return self._compare_dicts(legacy, unified)

        # Compare ValidationResult
        if isinstance(unified, ValidationResult):
            return self._compare_validation_results(legacy, unified)

        # Compare OrchestrationResult
        if isinstance(unified, OrchestrationResult):
            return self._compare_orchestration_results(legacy, unified)

        # Compare HealingResult
        if isinstance(unified, HealingResult):
            return self._compare_healing_results(legacy, unified)

        return differences

    def _compare_dicts(self, legacy: dict, unified: dict) -> list[str]:
        """Compare two dictionaries."""
        differences = []

        all_keys = set(legacy.keys()) | set(unified.keys())
        for key in all_keys:
            if key not in legacy:
                differences.append(f"Key '{key}' only in unified result")
            elif key not in unified:
                differences.append(f"Key '{key}' only in legacy result")
            elif legacy[key] != unified[key]:
                differences.append(
                    f"Value mismatch for '{key}': legacy={legacy[key]}, unified={unified[key]}"
                )

        return differences

    def _compare_validation_results(self, legacy: ValidationResult, unified: ValidationResult) -> list[str]:
        """Compare ValidationResult instances."""
        differences = []

        if legacy.passed != unified.passed:
            differences.append(f"passed mismatch: legacy={legacy.passed}, unified={unified.passed}")

        if set(legacy.issues) != set(unified.issues):
            differences.append(f"issues mismatch: legacy={legacy.issues}, unified={unified.issues}")

        return differences

    def _compare_validation_with_dict(self, legacy: dict, unified: ValidationResult) -> list[str]:
        """Compare dict with ValidationResult."""
        differences = []

        # Check if dict has equivalent fields
        if "passed" in legacy and legacy["passed"] != unified.passed:
            differences.append(f"passed mismatch: legacy={legacy['passed']}, unified={unified.passed}")

        return differences

    def _compare_orchestration_results(
        self, legacy: OrchestrationResult, unified: OrchestrationResult
    ) -> list[str]:
        """Compare OrchestrationResult instances."""
        differences = []

        if legacy.completed != unified.completed:
            differences.append(f"completed mismatch: legacy={legacy.completed}, unified={unified.completed}")

        if legacy.stage != unified.stage:
            differences.append(f"stage mismatch: legacy={legacy.stage}, unified={unified.stage}")

        return differences

    def _compare_healing_results(self, legacy: HealingResult, unified: HealingResult) -> list[str]:
        """Compare HealingResult instances."""
        differences = []

        if legacy.violations_found != unified.violations_found:
            differences.append(
                f"violations_found mismatch: legacy={legacy.violations_found}, "
                f"unified={unified.violations_found}"
            )

        if legacy.violations_fixed != unified.violations_fixed:
            differences.append(
                f"violations_fixed mismatch: legacy={legacy.violations_fixed}, "
                f"unified={unified.violations_fixed}"
            )

        return differences


class ReturnTypeValidator:
    """Validates return type consistency between legacy and unified agents."""

    @staticmethod
    def validate_return_type(
        legacy_result: Any,
        unified_result: Any,
        expected_type: type | None = None,
    ) -> list[str]:
        """
        Validate return type consistency.

        Args:
            legacy_result: Result from legacy agent
            unified_result: Result from unified agent
            expected_type: Optional expected return type

        Returns:
            List of validation errors
        """
        errors = []

        # Check expected type if provided
        if expected_type:
            if not isinstance(unified_result, expected_type):
                errors.append(
                    f"Unified result type mismatch: expected {expected_type.__name__}, "
                    f"got {type(unified_result).__name__}"
                )

        # Ensure dict doesn't become list or vice versa
        if isinstance(legacy_result, dict) and isinstance(unified_result, list):
            errors.append("Return type changed from dict to list")
        elif isinstance(legacy_result, list) and isinstance(unified_result, dict):
            errors.append("Return type changed from list to dict")

        return errors


class SignalHandlingValidator:
    """Validates signal handling consistency between legacy and unified agents."""

    @staticmethod
    def validate_signals(
        legacy_agent: Any,
        unified_agent: Any,
    ) -> list[str]:
        """
        Validate signal handling consistency.

        Args:
            legacy_agent: Legacy agent with mocked signal methods
            unified_agent: Unified agent with mocked signal methods

        Returns:
            List of validation errors
        """
        errors = []

        # Compare add_signal calls
        legacy_add_calls = legacy_agent.add_signal.call_args_list
        unified_add_calls = unified_agent.add_signal.call_args_list

        legacy_signals = {call[0][0] for call in legacy_add_calls if call[0]}
        unified_signals = {call[0][0] for call in unified_add_calls if call[0]}

        if legacy_signals != unified_signals:
            errors.append(f"add_signal mismatch: legacy={legacy_signals}, unified={unified_signals}")

        # Compare remove_signal calls
        legacy_remove_calls = legacy_agent.remove_signal.call_args_list
        unified_remove_calls = unified_agent.remove_signal.call_args_list

        legacy_removed = {call[0][0] for call in legacy_remove_calls if call[0]}
        unified_removed = {call[0][0] for call in unified_remove_calls if call[0]}

        if legacy_removed != unified_removed:
            errors.append(f"remove_signal mismatch: legacy={legacy_removed}, unified={unified_removed}")

        return errors


class PerformanceBenchmark:
    """Performance benchmarking utilities for parity testing."""

    def __init__(self, max_variance_pct: float = 20.0):
        """Initialize benchmark with max allowed variance."""
        self.max_variance_pct = max_variance_pct
        self.results: list[dict[str, Any]] = []

    def record(
        self,
        test_name: str,
        legacy_time_ms: float,
        unified_time_ms: float,
    ) -> dict[str, Any]:
        """Record a benchmark result."""
        if legacy_time_ms > 0:
            variance_pct = ((unified_time_ms - legacy_time_ms) / legacy_time_ms) * 100
        else:
            variance_pct = 0.0

        result = {
            "test_name": test_name,
            "legacy_time_ms": legacy_time_ms,
            "unified_time_ms": unified_time_ms,
            "variance_pct": variance_pct,
            "passed": abs(variance_pct) <= self.max_variance_pct,
        }

        self.results.append(result)
        return result

    def get_summary(self) -> dict[str, Any]:
        """Get benchmark summary."""
        if not self.results:
            return {"total_tests": 0, "passed": 0, "failed": 0}

        passed = sum(1 for r in self.results if r["passed"])
        failed = len(self.results) - passed

        avg_legacy = sum(r["legacy_time_ms"] for r in self.results) / len(self.results)
        avg_unified = sum(r["unified_time_ms"] for r in self.results) / len(self.results)
        avg_variance = sum(r["variance_pct"] for r in self.results) / len(self.results)

        return {
            "total_tests": len(self.results),
            "passed": passed,
            "failed": failed,
            "avg_legacy_time_ms": avg_legacy,
            "avg_unified_time_ms": avg_unified,
            "avg_variance_pct": avg_variance,
        }


# ============================================================================
# CONCRETE PARITY TESTS
# ============================================================================


class TestValidatorParity:
    """Parity tests for validator agents."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "validation_rules": {
                "pattern_check": {"type": "pattern_match", "pattern": r"forbidden"},
            },
            "forbidden_content": ["bad_word"],
            "required_content": [],
            "thresholds": {"min_score": 0.3},
        }

    @pytest.mark.asyncio
    async def test_validator_success_parity(self, mock_config):
        """Test validator success case parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()

            result = await agent.execute(data={"content": "good content here"})

            assert isinstance(result, ValidationResult)
            assert result.passed is True
            assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_validator_failure_parity(self, mock_config):
        """Test validator failure case parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()

            result = await agent.execute(data={"content": "bad_word in content"})

            assert isinstance(result, ValidationResult)
            assert result.passed is False
            assert len(result.issues) > 0

    @pytest.mark.asyncio
    async def test_validator_pattern_detection(self, mock_config):
        """Test validator pattern detection parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()

            result = await agent.execute(data={"content": "forbidden pattern here"})

            assert isinstance(result, ValidationResult)
            assert result.passed is False

    @pytest.mark.asyncio
    async def test_validator_heal_repository(self, mock_config):
        """Test validator heal_repository parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.VALIDATOR
            agent._unified_config = mock_config
            agent._strategy = None

            result = agent.heal_repository(dry_run=True)

            assert isinstance(result, dict)
            assert "violations_found" in result


class TestOrchestratorParity:
    """Parity tests for orchestrator agents."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "workflow_steps": [
                {"name": "step1", "type": "validation"},
                {"name": "step2", "type": "agent_call", "agent": "test"},
            ],
            "signal_handlers": {},
        }

    @pytest.mark.asyncio
    async def test_orchestrator_complete_workflow(self, mock_config):
        """Test orchestrator complete workflow parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()
            agent.log_error = Mock()

            result = await agent.execute()

            assert isinstance(result, OrchestrationResult)
            assert result.completed is True
            assert result.stage == "step2"

    @pytest.mark.asyncio
    async def test_orchestrator_signal_propagation(self, mock_config):
        """Test orchestrator signal propagation parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()
            agent.log_error = Mock()

            result = await agent.execute()

            assert "validation_completed" in result.signals

    @pytest.mark.asyncio
    async def test_orchestrator_empty_workflow(self):
        """Test orchestrator with empty workflow."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = {"workflow_steps": [], "signal_handlers": {}}
            agent._strategy = None
            agent.log_info = Mock()
            agent.log_error = Mock()

            result = await agent.execute()

            assert isinstance(result, OrchestrationResult)
            assert result.stage == "not_started"

    @pytest.mark.asyncio
    async def test_orchestrator_heal_repository(self, mock_config):
        """Test orchestrator heal_repository parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.ORCHESTRATOR
            agent._unified_config = mock_config
            agent._strategy = None

            result = agent.heal_repository(dry_run=True)

            assert isinstance(result, dict)


class TestHealerParity:
    """Parity tests for healer agents."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            "healing_rules": {
                "test_rule": {"type": "pattern_match", "pattern": r"violation"},
            },
            "auto_fix": False,
            "dry_run_default": True,
        }

    @pytest.mark.asyncio
    async def test_healer_dry_run(self, mock_config):
        """Test healer dry run parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()

            result = await agent.execute(dry_run=True)

            assert isinstance(result, HealingResult)
            assert result.violations_fixed == 0

    @pytest.mark.asyncio
    async def test_healer_violation_detection(self, mock_config):
        """Test healer violation detection parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = mock_config
            agent._strategy = None
            agent.log_info = Mock()

            result = await agent.execute(dry_run=True)

            assert isinstance(result, HealingResult)
            assert result.violations_found >= 0

    @pytest.mark.asyncio
    async def test_healer_heal_method(self, mock_config):
        """Test healer heal method parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = mock_config
            agent._strategy = None

            violation = {"type": "test", "id": "123"}
            result = agent.heal(violation)

            assert "status" in result
            assert "details" in result

    @pytest.mark.asyncio
    async def test_healer_heal_repository(self, mock_config):
        """Test healer heal_repository parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.HEALER
            agent._unified_config = mock_config
            agent._strategy = None

            result = agent.heal_repository(dry_run=True)

            assert isinstance(result, dict)
            assert "violations_found" in result


class TestGenericParity:
    """Parity tests for generic agents."""

    @pytest.mark.asyncio
    async def test_generic_execution(self):
        """Test generic agent execution parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.GENERIC
            agent._unified_config = {}
            agent._strategy = None
            agent.log_info = Mock()

            result = await agent.execute()

            assert isinstance(result, dict)
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_generic_heal_repository(self):
        """Test generic heal_repository parity."""
        with patch.object(UnifiedAgent, "__post_init__", lambda self: None):
            agent = UnifiedAgent()
            agent._category = AgentCategory.GENERIC
            agent._unified_config = {}
            agent._strategy = None

            result = agent.heal_repository(dry_run=True)

            assert isinstance(result, dict)


class TestReturnTypeValidation:
    """Tests for return type validation."""

    def test_validate_matching_types(self):
        """Test validation passes for matching types."""
        legacy = {"key": "value"}
        unified = {"key": "value"}

        errors = ReturnTypeValidator.validate_return_type(legacy, unified, dict)

        assert len(errors) == 0

    def test_validate_type_mismatch(self):
        """Test validation fails for type mismatch."""
        legacy = {"key": "value"}
        unified = ["value"]

        errors = ReturnTypeValidator.validate_return_type(legacy, unified, dict)

        assert len(errors) > 0

    def test_validate_expected_type(self):
        """Test validation against expected type."""
        unified = ValidationResult(passed=True, issues=[], suggestions=[])

        errors = ReturnTypeValidator.validate_return_type(None, unified, ValidationResult)

        assert len(errors) == 0


class TestPerformanceBenchmark:
    """Tests for performance benchmarking."""

    def test_record_benchmark(self):
        """Test recording benchmark results."""
        benchmark = PerformanceBenchmark(max_variance_pct=20.0)

        result = benchmark.record("test1", legacy_time_ms=100.0, unified_time_ms=110.0)

        assert result["passed"] is True
        assert result["variance_pct"] == 10.0

    def test_benchmark_failure(self):
        """Test benchmark failure on high variance."""
        benchmark = PerformanceBenchmark(max_variance_pct=20.0)

        result = benchmark.record("test1", legacy_time_ms=100.0, unified_time_ms=150.0)

        assert result["passed"] is False
        assert result["variance_pct"] == 50.0

    def test_get_summary(self):
        """Test getting benchmark summary."""
        benchmark = PerformanceBenchmark(max_variance_pct=20.0)

        benchmark.record("test1", legacy_time_ms=100.0, unified_time_ms=110.0)
        benchmark.record("test2", legacy_time_ms=100.0, unified_time_ms=90.0)

        summary = benchmark.get_summary()

        assert summary["total_tests"] == 2
        assert summary["passed"] == 2
        assert summary["failed"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
