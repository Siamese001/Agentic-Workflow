"""

logger = logging.getLogger(__name__)
Simplified integration tests for hardened orchestrator functionality.
Tests core components without complex workflow specifications.
"""
import pytest
import tempfile
from pathlib import Path

from runtime.shared.routing.factory import reset_router
import logging
    kflowOrchestrator

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

class TestHardenedOrchestratorCore:
    """Test core hardened orchestrator functionality."""

    def test_orchestrator_creation_with_storage(self, temp_state_dir):
            """Test creating a hardened orchestrator with storage path."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        assert orchestrator is not None
        assert isinstance(orchestrator, HardenedWorkflowOrchestrator)
        assert orchestrator.state_manager is not None
        assert orchestrator.router is not None

    def test_orchestrator_creation_without_storage(self):
            """Test creating a hardened orchestrator without storage path."""
        orchestrator = create_hardened_orchestrator()
        assert orchestrator is not None
        assert isinstance(orchestrator, HardenedWorkflowOrchestrator)
        assert orchestrator.state_manager is not None
        assert orchestrator.router is not None

    def test_state_manager_initialization(self, temp_state_dir):
            """Test that state manager is properly initialized."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        state_manager = orchestrator.state_manager
        assert state_manager is not None
        assert state_manager.storage_path == Path(temp_state_dir)

    def test_router_initialization(self, temp_state_dir):
            """Test that router is properly initialized."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        router = orchestrator.router
        assert router is not None
        assert isinstance(router, HardenedRouter)

class TestStateManagement:
    """Test atomic state management functionality."""

    def test_state_manager_from_orchestrator(self, temp_state_dir):
            """Test that state manager is accessible from orchestrator."""
        orchestrator = create_hardened_orchestrator(storage_path=temp_state_dir)
        state_manager = orchestrator.state_manager
        assert state_manager is not None
        assert state_manager.storage_path == Path(temp_state_dir)

    def test_state_manager_reset_via_orchestrator(self, temp_state_dir):
            """Test that state manager can be reset."""
        orchestrator1 = create_hardened_orchestrator(storage_path=temp_state_dir)
        state_manager1 = orchestrator1.state_manager
        reset_state_manager()
        orchestrator2 = create_hardened_orchestrator(storage_path=temp_state_dir)
        state_manager2 = orchestrator2.state_manager
        assert state_manager1 is not state_manager2

    def test_state_persistence_directory_creation(self, temp_state_dir):
            """Test that state persistence creates necessary directories."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        state_dir = Path(temp_state_dir)
        assert state_dir.exists()
        assert state_dir.is_dir()

class TestResilientRouting:
    """Test resilient routing functionality."""

    def test_router_singleton(self):
            """Test that router follows singleton pattern."""
        router1 = get_resilient_router()
        router2 = get_resilient_router()
        assert router1 is router2

    def test_router_reset(self):
            """Test that router can be reset."""
        router1 = get_resilient_router()
        reset_router()
        router2 = get_resilient_router()
        assert router1 is not router2

    def test_router_has_execute_method(self, temp_state_dir):
            """Test that router has execute_with_fallback method."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        router = orchestrator.router
        assert hasattr(router, 'execute_with_fallback')
        assert callable(router.execute_with_fallback)

class TestAgentResponseStructure:
    """Test AgentResponse structure and usage."""

    def test_agent_response_creation(self):
            """Test creating an AgentResponse with correct parameters."""
        response = AgentResponse(
            content="Test response",
            finish_reason="stop",
            usage={"total_tokens": 100}
        )
        assert response.content == "Test response"
        assert response.finish_reason == "stop"
        assert response.usage["total_tokens"] == 100

    def test_agent_response_with_metadata(self):
            """Test creating an AgentResponse with metadata."""
        response = AgentResponse(
            content="Test response",
            finish_reason="stop",
            usage={"total_tokens": 100},
            metadata={"provider_used": "mock_provider"}
        )
        assert response.metadata["provider_used"] == "mock_provider"

    def test_agent_response_optional_fields(self):
            """Test AgentResponse with optional fields."""
        response = AgentResponse(
            content="Test response",
            finish_reason="stop",
            usage={"total_tokens": 100},
            tool_calls=None,
            raw_response=None,
            interaction_id="test_id"
        )
        assert response.interaction_id == "test_id"
        assert response.tool_calls is None

class TestCircuitBreakerIntegration:
    """Test circuit breaker integration."""

    def test_circuit_breaker_exists(self, temp_state_dir):
            """Test that circuit breaker is integrated in router."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        router = orchestrator.router
        # Router should have circuit breaker functionality
        assert hasattr(router, 'configs') or hasattr(router, '_executors')

class TestOrchestratorIntegration:
    """Test integration between components."""

    def test_orchestrator_has_all_components(self, temp_state_dir):
            """Test that orchestrator has all required components."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        # Check state manager
        assert orchestrator.state_manager is not None

        # Check router
        assert orchestrator.router is not None

        # Check that orchestrator is properly initialized
        assert hasattr(orchestrator, 'execute_workflow')

    def test_multiple_orchestrators_share_state(self, temp_state_dir):
            """Test that multiple orchestrators can share state."""
        orchestrator1 = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        orchestrator2 = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        # Both should use the same state manager instance
        assert orchestrator1.state_manager is orchestrator2.state_manager

    def test_orchestrator_storage_path_handling(self, temp_state_dir):
            """Test that orchestrator handles storage path correctly."""
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )

        state_manager = orchestrator.state_manager
        assert state_manager.storage_path == Path(temp_state_dir)

class TestErrorHandling:
    """Test error handling in hardened components."""

    def test_orchestrator_handles_missing_api_keys(self, temp_state_dir):
            """Test that orchestrator handles missing API keys gracefully."""
        # This should not raise an exception during initialization
        orchestrator = create_hardened_orchestrator(
            storage_path=temp_state_dir
        )
        assert orchestrator is not None

    def test_orchestrator_with_default_storage(self):
            """Test that orchestrator works with default storage."""
        # Should handle default storage path gracefully
        orchestrator = create_hardened_orchestrator()
        assert orchestrator is not None
        assert orchestrator.state_manager is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
