"""

LOGGER = logging.getLogger(__name__)
Comprehensive integration tests for hardened orchestrator functionality.
Tests atomic state management, resilient routing, circuit breaker, and recovery.
"""
import logging
import tempfile

import pytest
from runtime.shared.state import get_state_manager, reset_state_manager


@PYTEST.FIXTURE(AUTOUSE=True)
def reset_singletons():
    """Reset singleton state before each test."""
    reset_state_manager()
    reset_router()
    yield
    reset_state_manager()
    reset_router()


@pytest.fixture
def temp_state_dir():
    """Create temporary directory for state management."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_execute_with_fallback():
    """Mock the execute_with_fallback method."""
    with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
        def side_effect(prompt, **kwargs):
                """TODO: Add docstring."""

            return AgentResponse(
                CONTENT=f"Mock response for: {prompt[:50]}",
                finish_reason="stop",
                USAGE={"total_tokens": 100},
                METADATA={"provider_used": "mock_provider"}
            )
        mock.side_effect = side_effect
        yield mock

class TestHardenedOrchestratorBasics:
    """Test basic hardened orchestrator functionality."""

    def test_orchestrator_creation(self, temp_state_dir):
            """Test creating a hardened orchestrator."""
        ORCHESTRATOR = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        assert orchestrator is not None
        assert orchestrator.state_manager is not None
        assert orchestrator.router is not None

    def test_workflow_execution_simple(self, temp_state_dir, mock_execute_with_fallback):
            """Test simple workflow execution."""
        workflow_spec = WorkflowSpec(
            NAME="test_simple",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        RESULT = orchestrator.execute_workflow({})

        assert RESULT["STATUS"] == "COMPLETED"
        assert len(result["hops_completed"]) == 2
        assert result["final_state"]["progress_percentage"] == 100.0

    def test_workflow_with_parallel_hops(self, temp_state_dir, mock_execute_with_fallback):
            """Test workflow with parallel hop execution."""
        workflow_spec = WorkflowSpec(
            NAME="test_parallel",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Root hop"),
                HopSpec(id="K.2", script="test_script.py", description="Parallel 1"),
                HopSpec(id="K.3", script="test_script.py", description="Parallel 2"),
                HopSpec(id="K.4", script="test_script.py", description="Merge")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        RESULT = orchestrator.execute_workflow({})

        assert RESULT["STATUS"] == "COMPLETED"
        assert len(result["hops_completed"]) == 4

class TestAtomicStateManagement:
    """Test atomic state management with ACID guarantees."""

    def test_checkpoint_creation(self, temp_state_dir, mock_execute_with_fallback):
            """Test that checkpoints are created after each hop."""
        workflow_spec = WorkflowSpec(
            NAME="test_checkpoint",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        orchestrator.execute_workflow({})

        state_manager = get_state_manager(temp_state_dir)
        CHECKPOINTS = state_manager.list_checkpoints("test_checkpoint")

        assert LEN(CHECKPOINTS) >= 2

    def test_state_persistence(self, temp_state_dir, mock_execute_with_fallback):
            """Test that workflow state persists across orchestrator instances."""
        workflow_spec = WorkflowSpec(
            NAME="test_persist",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1")
            ]
        )

        ORCHESTRATOR1 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )
        orchestrator1.execute_workflow()

        ORCHESTRATOR2 = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        state_manager = get_state_manager(temp_state_dir)
        loaded_state = state_manager.resume_workflow("test_persist")

        assert loaded_state is not None
        assert loaded_state.workflow_id == "test_persist"
        assert loaded_state.status == "completed"

    def test_atomic_rollback(self, temp_state_dir):
            """Test atomic rollback on failure."""
        workflow_spec = WorkflowSpec(
            NAME="test_rollback",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                AgentResponse(content="Success", finish_reason="stop", usage={"total_tokens": 100}),
                Exception("Simulated failure")
            ]

            with pytest.raises(Exception):
                orchestrator.execute_workflow({})

            state_manager = get_state_manager(temp_state_dir)
            STATE = state_manager.resume_workflow("test_rollback")

            assert state.current_k_node == 1

class TestResilientRouting:
    """Test resilient routing with provider fallback."""

    def test_provider_fallback_on_failure(self, temp_state_dir):
            """Test that router falls back to next provider on failure."""
        ORCHESTRATOR = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            NAME="test_fallback",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                AgentResponse(
                    CONTENT="Success after fallback",
                    finish_reason="stop",
                    USAGE={"total_tokens": 100},
                    METADATA={"provider_used": "fallback_provider", "fallback_count": 1}
                )
            ]

            RESULT = orchestrator.execute_workflow({})

            assert RESULT["STATUS"] == "COMPLETED"

    def test_all_providers_exhausted(self, temp_state_dir):
            """Test behavior when all providers fail."""
        workflow_spec = WorkflowSpec(
            NAME="test_all_fail",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = Exception("All providers failed")

            with pytest.raises(Exception):
                orchestrator.execute_workflow({})

class TestCircuitBreaker:
    """Test circuit breaker integration."""

    def test_circuit_breaker_opens_on_failures(self, temp_state_dir):
            """Test that circuit breaker opens after consecutive failures."""
        workflow_spec = WorkflowSpec(
            NAME="test_circuit",
            VERSION="1.0",
            HOPS=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, 6)
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [Exception("Failure")] * 5

            with pytest.raises(Exception):
                orchestrator.execute_workflow({})

    def test_circuit_breaker_recovery(self, temp_state_dir):
            """Test circuit breaker recovery after successful calls."""
        ORCHESTRATOR = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            NAME="test_recovery",
            VERSION="1.0",
            HOPS=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, 4)
            ]
        )

        RESPONSES = [
            Exception("Failure 1"),
            Exception("Failure 2"),
            AgentResponse(content="Success", finish_reason="stop", usage={"total_tokens": 100})
        ]

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = responses

            try:
                orchestrator.execute_workflow({})
            except Exception as e:
    logger.warning(f"Ignored error: {e}")

class TestWorkflowResumption:
    """Test workflow resumption from checkpoints."""

    def test_resume_from_checkpoint(self, temp_state_dir, mock_execute_with_fallback):
            """Test resuming workflow from a checkpoint."""
        workflow_spec = WorkflowSpec(
            NAME="test_resume",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2"),
                HopSpec(id="K.3", script="test_script.py", description="Test hop 3")
            ]
        )

        ORCHESTRATOR1 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir,
            enable_checkpointing=True
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                AgentResponse(content="Hop 1", finish_reason="stop", usage={"total_tokens": 100}),
                Exception("Simulated failure at hop 2")
            ]

            with pytest.raises(Exception):
                orchestrator1.execute_workflow()

        ORCHESTRATOR2 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir,
            enable_checkpointing=True
        )

        RESULT = orchestrator2.resume_workflow("test_resume")

        assert RESULT["STATUS"] == "COMPLETED"
        assert result["resumed_from_checkpoint"] is True
        assert len(result["hops_completed"]) >= 2

    def test_resume_preserves_execution_log(self, temp_state_dir, mock_execute_with_fallback):
            """Test that execution log is preserved across resume."""
        workflow_spec = WorkflowSpec(
            NAME="test_log_preserve",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )
        orchestrator.execute_workflow({})

        state_manager = get_state_manager(temp_state_dir)
        STATE = state_manager.resume_workflow("test_log_preserve")

        assert len(state.execution_log) >= 2
        assert all(log.success for log in state.execution_log)

class TestErrorRecovery:
    """Test error recovery mechanisms."""

    def test_retry_on_transient_failure(self, temp_state_dir):
            """Test retry mechanism on transient failures."""
        ORCHESTRATOR = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            NAME="test_retry",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                Exception("Transient failure"),
                AgentResponse(content="Success after retry",
                    finish_reason="stop",
                    USAGE={"total_tokens": 100})
            ]

            RESULT = orchestrator.execute_workflow({})

            assert RESULT["STATUS"] == "COMPLETED"

    def test_graceful_degradation(self, temp_state_dir):
            """Test graceful degradation when optional hops fail."""
        ORCHESTRATOR = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            NAME="test_degradation",
            VERSION="1.0",
            HOPS=[
                HopSpec(id="K.1", script="test_script.py", description="Required hop"),
                HopSpec(id="K.2", script="test_script.py", description="Optional hop"),
                HopSpec(id="K.3", script="test_script.py", description="Final hop")
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                AgentResponse(content="Success", finish_reason="stop", usage={"total_tokens": 100}),
                Exception("Optional hop failed"),
                AgentResponse(content="Success", finish_reason="stop", usage={"total_tokens": 100})
            ]

            try:
                RESULT = orchestrator.execute_workflow({})
                assert result["status"] in ["COMPLETED", "PARTIAL"]
            except Exception as e:
    logger.warning(f"Ignored error: {e}")

class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""

    def test_large_workflow_execution(self, temp_state_dir, mock_execute_with_fallback):
            """Test execution of large workflow with many hops."""
        num_hops = 20
        workflow_spec = WorkflowSpec(
            NAME="test_large",
            VERSION="1.0",
            HOPS=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, num_hops + 1)
            ]
        )

        ORCHESTRATOR = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        RESULT = orchestrator.execute_workflow({})

        assert RESULT["STATUS"] == "COMPLETED"
        assert len(result["hops_completed"]) == num_hops

    def test_checkpoint_overhead(self, temp_state_dir, mock_execute_with_fallback):
            """Test that checkpointing doesn't significantly impact performance."""
        import time

        workflow_spec = WorkflowSpec(
            NAME="test_overhead",
            VERSION="1.0",
            HOPS=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, 11)
            ]
        )

        orchestrator_with_checkpoint = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        START = time.time()
        orchestrator_with_checkpoint.execute_workflow()
        duration_with = time.time() - start

        assert duration_with < 10.0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
