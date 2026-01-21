#!/usr/bin/env python3
"""
Test Suite for Phase 1 Orchestrator Consolidation

Required Tests (100% pass required):
1. test_cache_persistence - Ensure repeated tasks retrieve from cache
2. test_recovery_exhaustion - Verify max_retries attempts before error
3. test_workflow_dependency_gate - Verify phase dependency validation
4. test_legacy_factory_mapping - Ensure deprecated factories return functional agents

Additional Tests:
5. test_intelligent_routing - Verify strategy pattern routing
6. test_workflow_state_machine - Verify phase transitions
7. test_deprecation_warnings - Verify warnings are raised
8. test_execution_stats - Verify statistics tracking
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path
from typing import Any

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L3_orchestration.unified.AppWorkflowOrchestratorAgent import (
    AppWorkflowOrchestratorAgent,
    PhaseResult,
    WorkflowPhase,
    WorkflowState,
    WorkflowType,
)
from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import (
    CoreOrchestrationAgent,
    OrchestrationStrategy,
    Result,
    Task,
    TaskType,
    create_legacy_cached_orchestrator,
    create_legacy_intelligent_orchestrator,
    create_legacy_self_recovering_orchestrator,
)


class TestCachePersistence:
    """Test 1: Ensure that if a task is repeated, the CoreOrchestrationAgent
    retrieves the result from the cache rather than re-executing."""

    @pytest.mark.asyncio
    async def test_cache_persistence(self):
        """REQUIRED: Cache hit on repeated task execution."""
        # Arrange
        agent = CoreOrchestrationAgent(cache_enabled=True, max_retries=1)
        task = Task(
            task_id="cache_test_1",
            task_type=TaskType.VALIDATION,
            payload={"test": "data"},
            cache_ttl=3600,
        )

        # Act - First execution
        result1 = await agent.orchestrate(task)

        # Act - Second execution (should hit cache)
        result2 = await agent.orchestrate(task)

        # Assert
        assert result1.success, "First execution should succeed"
        assert result2.success, "Second execution should succeed"
        assert not result1.from_cache, "First result should NOT be from cache"
        assert result2.from_cache, "Second result MUST be from cache"
        assert result1.data == result2.data, "Cached data should match original"

    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        """Cache should not be used when disabled."""
        # Arrange
        agent = CoreOrchestrationAgent(cache_enabled=False, max_retries=1)
        task = Task(
            task_id="cache_disabled_test",
            task_type=TaskType.VALIDATION,
            payload={"test": "data"},
        )

        # Act
        result1 = await agent.orchestrate(task)
        result2 = await agent.orchestrate(task)

        # Assert
        assert not result1.from_cache
        assert not result2.from_cache, "Should not use cache when disabled"

    @pytest.mark.asyncio
    async def test_cache_key_uniqueness(self):
        """Different payloads should have different cache keys."""
        # Arrange
        agent = CoreOrchestrationAgent(cache_enabled=True)
        task1 = Task(
            task_id="t1",
            task_type=TaskType.VALIDATION,
            payload={"key": "value1"},
        )
        task2 = Task(
            task_id="t2",
            task_type=TaskType.VALIDATION,
            payload={"key": "value2"},
        )

        # Assert
        assert task1.cache_key() != task2.cache_key(), (
            "Different payloads should have different cache keys"
        )


class TestRecoveryExhaustion:
    """Test 2: Verify the agent attempts exactly max_retries before raising
    a final orchestration error."""

    @pytest.mark.asyncio
    async def test_recovery_exhaustion(self):
        """REQUIRED: Agent attempts exactly max_retries before failing."""
        # Arrange
        max_retries = 3
        agent = CoreOrchestrationAgent(
            cache_enabled=False,
            max_retries=max_retries,
            retry_backoff_base=0.01,  # Fast backoff for testing
        )

        # Create a strategy that always fails
        class FailingStrategy(OrchestrationStrategy):
            def __init__(self):
                self.attempt_count = 0

            async def execute(self, task: Task, context: dict[str, Any]) -> Result:
                self.attempt_count += 1
                raise Exception(f"Intentional failure #{self.attempt_count}")

            def can_handle(self, task: Task) -> bool:
                return task.task_type == TaskType.GENERIC

        failing_strategy = FailingStrategy()
        agent._strategies = [failing_strategy]  # Replace strategies

        task = Task(
            task_id="retry_test",
            task_type=TaskType.GENERIC,
            payload={},
            max_retries=max_retries,
        )

        # Act
        result = await agent.orchestrate(task)

        # Assert
        assert not result.success, "Should fail after exhausting retries"
        assert failing_strategy.attempt_count == max_retries, (
            f"Should attempt exactly {max_retries} times, got {failing_strategy.attempt_count}"
        )
        assert result.retries_used == max_retries, (
            f"retries_used should be {max_retries}, got {result.retries_used}"
        )
        assert "Intentional failure" in result.error, "Error message should be preserved"

    @pytest.mark.asyncio
    async def test_success_on_retry(self):
        """Agent should succeed if retry succeeds."""
        # Arrange
        agent = CoreOrchestrationAgent(
            cache_enabled=False,
            max_retries=3,
            retry_backoff_base=0.01,
        )

        # Create a strategy that fails twice then succeeds
        class EventualSuccessStrategy(OrchestrationStrategy):
            def __init__(self):
                self.attempt_count = 0

            async def execute(self, task: Task, context: dict[str, Any]) -> Result:
                self.attempt_count += 1
                if self.attempt_count < 3:
                    raise Exception(f"Failure #{self.attempt_count}")
                return Result(
                    task_id=task.task_id, success=True, data={"attempt": self.attempt_count}
                )

            def can_handle(self, task: Task) -> bool:
                return True

        strategy = EventualSuccessStrategy()
        agent._strategies = [strategy]

        task = Task(
            task_id="eventual_success",
            task_type=TaskType.GENERIC,
            payload={},
            max_retries=3,
        )

        # Act
        result = await agent.orchestrate(task)

        # Assert
        assert result.success, "Should succeed on third attempt"
        assert strategy.attempt_count == 3, "Should take 3 attempts"
        assert result.retries_used == 2, "Should have used 2 retries"


class TestWorkflowDependencyGate:
    """Test 3: Verify that AppWorkflowOrchestratorAgent prevents execution
    of Phase 6 if Phase 5 data is missing or invalid."""

    @pytest.mark.asyncio
    async def test_workflow_dependency_gate(self):
        """REQUIRED: Phase 6 blocked if Phase 5 data missing."""
        # Arrange
        agent = AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC)

        # Create a state that has completed phases 1-4 but NOT phase 5
        state = WorkflowState(
            workflow_id="test_gate",
            workflow_type=WorkflowType.LIC,
            current_phase=WorkflowPhase.LIC_PHASE_6_VALIDATION,
            completed_phases={
                WorkflowPhase.LIC_PHASE_1_PROFILE,
                WorkflowPhase.LIC_PHASE_2_RESEARCH,
                WorkflowPhase.LIC_PHASE_3_GROUNDING,
                WorkflowPhase.LIC_PHASE_4_ROUTING,
                # Phase 5 NOT completed
            },
            context={
                "profile_data": {},
                "archetype": "executive",
                "research_data": {},
                "talking_points": [],
                "grounding_context": {},
                "selected_route": "inmail",
                "route_config": {},
                # draft_message NOT present (Phase 5 output)
            },
        )

        # Act
        is_valid, error = agent.validate_phase_dependencies(
            WorkflowPhase.LIC_PHASE_6_VALIDATION,
            state,
        )

        # Assert
        assert not is_valid, "Phase 6 should be blocked"
        assert error is not None, "Error message should be provided"
        assert "LIC_PHASE_5_GENERATION" in error or "dependency" in error.lower(), (
            f"Error should mention Phase 5 dependency: {error}"
        )

    @pytest.mark.asyncio
    async def test_workflow_dependency_satisfied(self):
        """Phase should execute when dependencies are satisfied."""
        # Arrange
        agent = AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC)

        state = WorkflowState(
            workflow_id="test_satisfied",
            workflow_type=WorkflowType.LIC,
            current_phase=WorkflowPhase.LIC_PHASE_2_RESEARCH,
            completed_phases={WorkflowPhase.LIC_PHASE_1_PROFILE},
            phase_results={
                WorkflowPhase.LIC_PHASE_1_PROFILE: PhaseResult(
                    phase=WorkflowPhase.LIC_PHASE_1_PROFILE,
                    success=True,
                    data={"profile_data": {}, "archetype": "executive"},
                ),
            },
            context={"profile_data": {}, "archetype": "executive"},
        )

        # Act
        is_valid, error = agent.validate_phase_dependencies(
            WorkflowPhase.LIC_PHASE_2_RESEARCH,
            state,
        )

        # Assert
        assert is_valid, f"Phase 2 should be allowed: {error}"
        assert error is None

    @pytest.mark.asyncio
    async def test_missing_required_input(self):
        """Phase should be blocked if required input is missing."""
        # Arrange
        agent = AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC)

        state = WorkflowState(
            workflow_id="test_missing_input",
            workflow_type=WorkflowType.LIC,
            current_phase=WorkflowPhase.LIC_PHASE_1_PROFILE,
            context={},  # Missing recipient_id
        )

        # Act
        is_valid, error = agent.validate_phase_dependencies(
            WorkflowPhase.LIC_PHASE_1_PROFILE,
            state,
        )

        # Assert
        assert not is_valid, "Should be blocked due to missing input"
        assert "recipient_id" in error, f"Error should mention missing input: {error}"


class TestLegacyFactoryMapping:
    """Test 4: Ensure calling the deprecated CachedOrchestratorAgent factory
    returns a functional CoreOrchestrationAgent instance."""

    def test_legacy_factory_mapping(self):
        """REQUIRED: Legacy factory returns functional unified agent."""
        # Act - Should raise deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = create_legacy_cached_orchestrator()

            # Assert warning was raised
            assert len(w) == 1, "Should raise exactly one warning"
            assert issubclass(w[0].category, DeprecationWarning)
            assert "CachedOrchestratorAgent" in str(w[0].message)
            assert "deprecated" in str(w[0].message).lower()

        # Assert agent is functional
        assert isinstance(agent, CoreOrchestrationAgent)
        assert agent.cache_enabled, "Cache should be enabled for cached orchestrator"

    def test_legacy_self_recovering_factory(self):
        """SelfRecoveringOrchestratorAgent factory returns unified agent."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = create_legacy_self_recovering_orchestrator()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "SelfRecoveringOrchestratorAgent" in str(w[0].message)

        assert isinstance(agent, CoreOrchestrationAgent)
        assert agent.max_retries == 3, "Should have default retry count"

    def test_legacy_intelligent_factory(self):
        """IntelligentOrchestratorAgent factory returns unified agent."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            agent = create_legacy_intelligent_orchestrator()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "IntelligentOrchestratorAgent" in str(w[0].message)

        assert isinstance(agent, CoreOrchestrationAgent)

    @pytest.mark.asyncio
    async def test_legacy_agent_executes_tasks(self):
        """Legacy factory agent should execute tasks successfully."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            agent = create_legacy_cached_orchestrator()

        task = Task(
            task_id="legacy_test",
            task_type=TaskType.VALIDATION,
            payload={"test": True},
        )

        result = await agent.orchestrate(task)

        assert result.success, "Legacy agent should execute tasks"
        assert result.task_id == "legacy_test"


class TestIntelligentRouting:
    """Test 5: Verify strategy pattern routing."""

    @pytest.mark.asyncio
    async def test_validation_task_routing(self):
        """Validation tasks should route to ValidationStrategy."""
        agent = CoreOrchestrationAgent()
        task = Task(
            task_id="validation_routing",
            task_type=TaskType.VALIDATION,
            payload={},
        )

        strategy = agent._select_strategy(task)

        assert strategy.__class__.__name__ == "ValidationStrategy"

    @pytest.mark.asyncio
    async def test_healing_task_routing(self):
        """Healing tasks should route to HealingStrategy."""
        agent = CoreOrchestrationAgent()
        task = Task(
            task_id="healing_routing",
            task_type=TaskType.HEALING,
            payload={},
        )

        strategy = agent._select_strategy(task)

        assert strategy.__class__.__name__ == "HealingStrategy"

    @pytest.mark.asyncio
    async def test_generic_fallback_routing(self):
        """Unknown tasks should route to GenericStrategy."""
        agent = CoreOrchestrationAgent()
        task = Task(
            task_id="generic_routing",
            task_type=TaskType.FISSION,  # No specific strategy
            payload={},
        )

        strategy = agent._select_strategy(task)

        assert strategy.__class__.__name__ == "GenericStrategy"


class TestWorkflowStateMachine:
    """Test 6: Verify phase transitions."""

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self):
        """Workflow should complete all phases in order."""
        agent = AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC)

        initial_context = {"recipient_id": "test_123"}

        state = await agent.execute_workflow(initial_context)

        assert state.current_phase == WorkflowPhase.COMPLETE
        assert not state.is_error
        assert len(state.completed_phases) == len(agent.get_workflow_phases())

    @pytest.mark.asyncio
    async def test_workflow_phase_order(self):
        """Phases should execute in dependency order."""
        agent = AppWorkflowOrchestratorAgent(workflow_type=WorkflowType.LIC)

        phases = agent.get_workflow_phases()

        # Verify Phase 1 comes before Phase 2, etc.
        phase_indices = {p: i for i, p in enumerate(phases)}

        assert (
            phase_indices[WorkflowPhase.LIC_PHASE_1_PROFILE]
            < phase_indices[WorkflowPhase.LIC_PHASE_2_RESEARCH]
        )
        assert (
            phase_indices[WorkflowPhase.LIC_PHASE_5_GENERATION]
            < phase_indices[WorkflowPhase.LIC_PHASE_6_VALIDATION]
        )


class TestExecutionStats:
    """Test 8: Verify statistics tracking."""

    @pytest.mark.asyncio
    async def test_execution_stats_tracking(self):
        """Agent should track execution statistics."""
        agent = CoreOrchestrationAgent(cache_enabled=True)

        # Execute some tasks
        for i in range(5):
            task = Task(
                task_id=f"stats_test_{i}",
                task_type=TaskType.VALIDATION,
                payload={"index": i},
            )
            await agent.orchestrate(task)

        # Get stats
        stats = agent.get_execution_stats()

        assert stats["total"] == 5
        assert stats["successful"] == 5
        assert stats["failed"] == 0
        assert stats["success_rate"] == 1.0
        assert "avg_execution_time" in stats


# =============================================================================
# TEST RUNNER
# =============================================================================


def run_tests():
    """Run all tests and report results."""

    print("=" * 70)
    print("Phase 1 Orchestrator Consolidation Test Suite")
    print("=" * 70)

    # Run pytest
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure for required tests
        ]
    )

    if exit_code == 0:
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - 100% pass rate achieved")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ TESTS FAILED - Review failures above")
        print("=" * 70)

    return exit_code


if __name__ == "__main__":
    exit(run_tests())
