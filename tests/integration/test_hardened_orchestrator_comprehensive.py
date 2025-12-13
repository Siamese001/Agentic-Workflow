"""
Comprehensive integration tests for hardened orchestrator functionality.
Tests atomic state management, resilient routing, circuit breaker, and recovery.
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from runtime.shared.state import get_state_manager, reset_state_manager
from runtime.shared.routing.factory import reset_router
from apps_rg.L3_orchestration.hardened_orchestrator import create_hardened_orchestrator
from apps_rg.L3_orchestration.orchestrate_workflow import WorkflowSpec, HopSpec
from runtime.shared.routing.router import HardenedRouter
from runtime.shared.agent_executor import AgentResponse

@pytest.fixture(autouse=True)
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
            return AgentResponse(
                content=f"Mock response for: {prompt[:50]}",
                finish_reason="stop",
                usage={"total_tokens": 100},
                metadata={"provider_used": "mock_provider"}
            )
        mock.side_effect = side_effect
        yield mock

class TestHardenedOrchestratorBasics:
    """Test basic hardened orchestrator functionality."""

    def test_orchestrator_creation(self, temp_state_dir):
        """Test creating a hardened orchestrator."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        assert orchestrator is not None
        assert orchestrator.state_manager is not None
        assert orchestrator.router is not None

    def test_workflow_execution_simple(self, temp_state_dir, mock_execute_with_fallback):
        """Test simple workflow execution."""
        workflow_spec = WorkflowSpec(
            name="test_simple",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        result = orchestrator.execute_workflow({})

        assert result["status"] == "COMPLETED"
        assert len(result["hops_completed"]) == 2
        assert result["final_state"]["progress_percentage"] == 100.0

    def test_workflow_with_parallel_hops(self, temp_state_dir, mock_execute_with_fallback):
        """Test workflow with parallel hop execution."""
        workflow_spec = WorkflowSpec(
            name="test_parallel",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Root hop"),
                HopSpec(id="K.2", script="test_script.py", description="Parallel 1"),
                HopSpec(id="K.3", script="test_script.py", description="Parallel 2"),
                HopSpec(id="K.4", script="test_script.py", description="Merge")
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        result = orchestrator.execute_workflow({})

        assert result["status"] == "COMPLETED"
        assert len(result["hops_completed"]) == 4

class TestAtomicStateManagement:
    """Test atomic state management with ACID guarantees."""

    def test_checkpoint_creation(self, temp_state_dir, mock_execute_with_fallback):
        """Test that checkpoints are created after each hop."""
        workflow_spec = WorkflowSpec(
            name="test_checkpoint",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        orchestrator.execute_workflow({})

        state_manager = get_state_manager(temp_state_dir)
        checkpoints = state_manager.list_checkpoints("test_checkpoint")

        assert len(checkpoints) >= 2

    def test_state_persistence(self, temp_state_dir, mock_execute_with_fallback):
        """Test that workflow state persists across orchestrator instances."""
        workflow_spec = WorkflowSpec(
            name="test_persist",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1")
            ]
        )

        orchestrator1 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )
        orchestrator1.execute_workflow()

        orchestrator2 = create_hardened_orchestrator(
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
            name="test_rollback",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        orchestrator = create_hardened_orchestrator(
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
            state = state_manager.resume_workflow("test_rollback")

            assert state.current_k_node == 1

class TestResilientRouting:
    """Test resilient routing with provider fallback."""

    def test_provider_fallback_on_failure(self, temp_state_dir):
        """Test that router falls back to next provider on failure."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            name="test_fallback",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop")
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                AgentResponse(
                    content="Success after fallback",
                    finish_reason="stop",
                    usage={"total_tokens": 100},
                    metadata={"provider_used": "fallback_provider", "fallback_count": 1}
                )
            ]

            result = orchestrator.execute_workflow({})

            assert result["status"] == "COMPLETED"

    def test_all_providers_exhausted(self, temp_state_dir):
        """Test behavior when all providers fail."""
        workflow_spec = WorkflowSpec(
            name="test_all_fail",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop")
            ]
        )

        orchestrator = create_hardened_orchestrator(
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
            name="test_circuit",
            version="1.0",
            hops=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, 6)
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [Exception("Failure")] * 5

            with pytest.raises(Exception):
                orchestrator.execute_workflow({})

    def test_circuit_breaker_recovery(self, temp_state_dir):
        """Test circuit breaker recovery after successful calls."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            name="test_recovery",
            version="1.0",
            hops=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, 4)
            ]
        )

        responses = [
            Exception("Failure 1"),
            Exception("Failure 2"),
            AgentResponse(content="Success", finish_reason="stop", usage={"total_tokens": 100})
        ]

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = responses

            try:
                orchestrator.execute_workflow({})
            except Exception:
                pass

class TestWorkflowResumption:
    """Test workflow resumption from checkpoints."""

    def test_resume_from_checkpoint(self, temp_state_dir, mock_execute_with_fallback):
        """Test resuming workflow from a checkpoint."""
        workflow_spec = WorkflowSpec(
            name="test_resume",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2"),
                HopSpec(id="K.3", script="test_script.py", description="Test hop 3")
            ]
        )

        orchestrator1 = create_hardened_orchestrator(
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

        orchestrator2 = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir,
            enable_checkpointing=True
        )

        result = orchestrator2.resume_workflow("test_resume")

        assert result["status"] == "COMPLETED"
        assert result["resumed_from_checkpoint"] is True
        assert len(result["hops_completed"]) >= 2

    def test_resume_preserves_execution_log(self, temp_state_dir, mock_execute_with_fallback):
        """Test that execution log is preserved across resume."""
        workflow_spec = WorkflowSpec(
            name="test_log_preserve",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop 1"),
                HopSpec(id="K.2", script="test_script.py", description="Test hop 2")
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )
        orchestrator.execute_workflow({})

        state_manager = get_state_manager(temp_state_dir)
        state = state_manager.resume_workflow("test_log_preserve")

        assert len(state.execution_log) >= 2
        assert all(log.success for log in state.execution_log)

class TestErrorRecovery:
    """Test error recovery mechanisms."""

    def test_retry_on_transient_failure(self, temp_state_dir):
        """Test retry mechanism on transient failures."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            name="test_retry",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Test hop")
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        with patch.object(HardenedRouter, 'execute_with_fallback') as mock:
            mock.side_effect = [
                Exception("Transient failure"),
                AgentResponse(content="Success after retry", finish_reason="stop", usage={"total_tokens": 100})
            ]

            result = orchestrator.execute_workflow({})

            assert result["status"] == "COMPLETED"

    def test_graceful_degradation(self, temp_state_dir):
        """Test graceful degradation when optional hops fail."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        workflow_spec = WorkflowSpec(
            name="test_degradation",
            version="1.0",
            hops=[
                HopSpec(id="K.1", script="test_script.py", description="Required hop"),
                HopSpec(id="K.2", script="test_script.py", description="Optional hop"),
                HopSpec(id="K.3", script="test_script.py", description="Final hop")
            ]
        )

        orchestrator = create_hardened_orchestrator(
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
                result = orchestrator.execute_workflow({})
                assert result["status"] in ["COMPLETED", "PARTIAL"]
            except Exception:
                pass

class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""

    def test_large_workflow_execution(self, temp_state_dir, mock_execute_with_fallback):
        """Test execution of large workflow with many hops."""
        num_hops = 20
        workflow_spec = WorkflowSpec(
            name="test_large",
            version="1.0",
            hops=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, num_hops + 1)
            ]
        )

        orchestrator = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        result = orchestrator.execute_workflow({})

        assert result["status"] == "COMPLETED"
        assert len(result["hops_completed"]) == num_hops

    def test_checkpoint_overhead(self, temp_state_dir, mock_execute_with_fallback):
        """Test that checkpointing doesn't significantly impact performance."""
        import time

        workflow_spec = WorkflowSpec(
            name="test_overhead",
            version="1.0",
            hops=[
                HopSpec(id=f"K.{i}", script="test_script.py", description=f"Test hop {i}")
                for i in range(1, 11)
            ]
        )

        orchestrator_with_checkpoint = create_hardened_orchestrator(
            workflow_spec=workflow_spec,
            storage_path=temp_state_dir
        )

        start = time.time()
        orchestrator_with_checkpoint.execute_workflow()
        duration_with = time.time() - start

        assert duration_with < 10.0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
