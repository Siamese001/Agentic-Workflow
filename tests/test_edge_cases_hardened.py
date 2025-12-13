"""
Test Suite: Hardened Infrastructure Edge Cases

This module tests catastrophic failure scenarios and edge cases
in the hardened infrastructure components including:
- Atomic state corruption & recovery
- Router total provider failure
- Circuit breaker flapping behavior
"""

import pytest
import asyncio
import json
from typing import Dict, Any

# Import the modules we're testing
# Note: These imports may need adjustment based on actual module structure
try:
    from runtime.shared.state import AtomicStateManager, WorkflowState, BackendType, StatePersistenceError
    from runtime.shared.routing import HardenedRouter, Provider, RoutingTier, AllProvidersDownError
    from runtime.shared.resilience import CircuitBreaker, CircuitState, CircuitOpenError
except ImportError as e:
    # Fallback imports for testing
    pytest.skip(f"Skipping hardened infrastructure tests: {e}", allow_module_level=True)

@pytest.mark.asyncio
async def test_atomic_state_shadow_write_failure(tmp_path):
    """
    Test that if the "Shadow Write" fails, the original checkpoint is preserved.

    This verifies atomic state management ensures no corruption during write failures.
    """
    # Setup: Create a valid initial state file
    manager = AtomicStateManager(BackendType.FILE)
    initial_state = WorkflowState(workflow_id="test_01", current_k_node=1)

    # Write initial state manually to simulate existing progress
    state_path = tmp_path / "test_01.json"
    state_path.write_text(initial_state.json())

    # Action: Try to checkpoint NEW state, but Mock the file write to fail
    new_state = WorkflowState(workflow_id="test_01", current_k_node=2)

    with patch("builtins.open", side_effect=IOError("Disk Full")):
        with pytest.raises(StatePersistenceError):
            await manager.checkpoint("test_01", new_state)

    # Verification:
    # 1. The original file must still exist and contain 'current_k_node=1'
    reloaded = manager.resume_workflow("test_01")
    assert reloaded.current_k_node == 1

    # 2. No corrupted shadow files should remain (cleanup check)
    assert not (tmp_path / "test_01_shadow.json").exists()

@pytest.mark.asyncio
async def test_router_total_provider_failure():
    """
    Test system behavior when OpenAI, Anthropic, and Gemini ALL fail.

    Verifies the router properly handles total provider outage scenarios.
    """
    # Setup: Mock Router with 3 providers
    router = HardenedRouter()

    # Mock all executors to raise CircuitOpenError
    mock_executor = AsyncMock(side_effect=CircuitOpenError("Service Down"))
    router.executors = {
        Provider.OPENAI: mock_executor,
        Provider.ANTHROPIC: mock_executor,
        Provider.GEMINI: mock_executor
    }

    # Action & Verification:
    with pytest.raises(AllProvidersDownError) as exc_info:
        await router.execute_with_fallback(RoutingTier.REASONING, "Test Prompt")

    assert "All available providers for tier REASONING failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_circuit_breaker_flapping_recovery():
    """
    Test the transition from OPEN -> HALF_OPEN -> CLOSED/OPEN based on success/fail signals.

    Verifies circuit breaker properly handles flapping services and recovery attempts.
    """
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    # Phase 1: Fail twice to OPEN the circuit
    await cb.record_failure()
    await cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Phase 2: Wait for recovery timeout
    await asyncio.sleep(0.15)

    # Phase 3: Next call should be permitted (HALF_OPEN)
    assert cb.allow_request() is True
    assert cb.state == CircuitState.HALF_OPEN

    # Phase 4: Success closes it
    await cb.record_success()
    assert cb.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_circuit_breaker_permanent_failure():
    """
    Test that circuit breaker remains OPEN after repeated failures in HALF_OPEN state.
    """
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    # Trigger OPEN state
    await cb.record_failure()
    await cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Wait for timeout and enter HALF_OPEN
    await asyncio.sleep(0.15)
    cb.allow_request()  # This should set to HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN

    # Fail again in HALF_OPEN - should go back to OPEN
    await cb.record_failure()
    assert cb.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_atomic_state_concurrent_writes(tmp_path):
    """
    Test that concurrent state writes don't corrupt the state file.
    """
    manager = AtomicStateManager(BackendType.FILE)

    # Simulate concurrent writes
    async def write_state(workflow_id: str, node_id: int):
        """TODO: Add docstring."""

        state = WorkflowState(workflow_id=workflow_id, current_k_node=node_id)
        await manager.checkpoint(workflow_id, state)

    # Launch multiple concurrent writes for the same workflow
    tasks = [
        write_state("concurrent_test", i) for i in range(1, 6)
    ]

    await asyncio.gather(*tasks)

    # Verify final state is consistent (should be one of the written states)
    final_state = manager.resume_workflow("concurrent_test")
    assert final_state.current_k_node in range(1, 6)

    # Verify state file is valid JSON
    state_file = tmp_path / "concurrent_test.json"
    assert state_file.exists()
    json.loads(state_file.read_text())  # Should not raise

@pytest.mark.asyncio
async def test_router_fallback_with_degraded_providers():
    """
    Test router behavior when some providers are degraded but not completely failed.
    """
    router = HardenedRouter()

    # Mock executors with different behaviors
        """TODO: Add docstring."""

    async def failing_executor(prompt):
        raise CircuitOpenError("Service Unavailable")
        """TODO: Add docstring."""


    async def slow_executor(prompt):
        await asyncio.sleep(0.1)  # Simulate slowness
        """TODO: Add docstring."""

        return "Slow response"

    async def working_executor(prompt):
        return "Quick response"

    router.executors = {
        Provider.OPENAI: AsyncMock(side_effect=failing_executor),
        Provider.ANTHROPIC: AsyncMock(side_effect=slow_executor),
        Provider.GEMINI: AsyncMock(side_effect=working_executor)
    }

    # Should fallback to working provider
    result = await router.execute_with_fallback(RoutingTier.REASONING, "Test")

    assert result == "Quick response"
    # Verify the failing provider was attempted first
    router.executors[Provider.OPENAI].assert_called_once()

@pytest.mark.asyncio
async def test_state_recovery_from_backup(tmp_path):
    """
    Test state recovery when primary file is corrupted but backup exists.
    """
    manager = AtomicStateManager(BackendType.FILE)

    # Create a valid state and backup
    original_state = WorkflowState(workflow_id="backup_test", current_k_node=42)
    state_path = tmp_path / "backup_test.json"
    backup_path = tmp_path / "backup_test.bak"

    # Write original state
    state_path.write_text(original_state.json())
    backup_path.write_text(original_state.json())

    # Corrupt the primary file
    state_path.write_text("corrupted json {")

    # Should recover from backup
    recovered_state = manager.resume_workflow("backup_test")
    assert recovered_state.current_k_node == 42

@pytest.mark.asyncio
async def test_circuit_breaker_metrics_collection():
    """
    Test that circuit breaker properly collects and reports metrics.
    """
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

    # Record some activity
    await cb.record_success()
    await cb.record_failure()
    await cb.record_failure()

    metrics = cb.get_metrics()

    assert metrics['total_requests'] == 3
    assert metrics['successes'] == 1
    assert metrics['failures'] == 2
    assert metrics['current_state'] == 'OPEN'  # 2 failures should meet threshold

# Additional helper classes for testing (if not already defined)
class AgentResponse:
    """Simple container for agent responses."""
    def __init__(self, content: str, metadata: Dict[str, Any]):
        self.content = content
        self.metadata = metadata

class MaxValidationRetriesError(Exception):
    """Raised when maximum validation retries are exceeded."""
    pass

class ContextOverflowError(Exception):
    """Raised when context exceeds token limits."""
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
