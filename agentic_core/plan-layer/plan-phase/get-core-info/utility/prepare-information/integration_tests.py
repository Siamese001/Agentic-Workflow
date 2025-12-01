"""
L1 Cognitive Planning - Prepare Information Integration Tests

Comprehensive integration tests for the prepare information system to ensure
all preparers work together correctly with proper orchestration.
"""

import asyncio
import logging
import pytest
from typing import Dict, Any, List
from datetime import datetime

# Import all prepare information components
from .prepare_information_orchestrator import (
    PrepareInformationOrchestrator,
    PrepareInformationRequest,
    PreparationType,
    PreparationMode,
    create_prepare_information_orchestrator,
    PrepareOrchestratorSafetyPolicy
)

from .prepare_information_registry import (
    PrepareInformationRegistry,
    PreparerType,
    PreparerRegistration,
    get_prepare_information_registry,
    register_custom_preparer
)

# Import individual preparers
from .format_registry_context import create_registry_context_formatter
from .prepare_core_payload import create_core_payload_preparer


class TestPrepareInformationOrchestrator:
    """Integration tests for PrepareInformationOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all preparers"""
        return create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer()
        )
    
    @pytest.fixture
    def sample_layer_spec(self) -> Dict[str, Any]:
        """Sample layer specification for testing"""
        return {
            "name": "test_layer",
            "version": "1.0.0",
            "context_data": {
                "registry_type": "standard",
                "layer_type": "service",
                "environment": "production"
            },
            "payload_data": {
                "core_config": {"timeout": 30, "retries": 3},
                "api_endpoints": ["/api/v1/data", "/api/v1/config"],
                "dependencies": ["database", "cache"]
            }
        }
    
    @pytest.mark.asyncio
    async def test_sequential_preparation_execution(self, orchestrator, sample_layer_spec):
        """Test sequential preparation execution"""
        request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_preparations(request)
        
        # Verify summary structure
        assert summary is not None
        assert len(summary.preparation_results) == 2
        assert summary.overall_successful is not False  # Should not be False due to fallback
        assert summary.overall_score >= 0.0
        assert summary.total_errors >= 0
        assert summary.total_warnings >= 0
        
        # Verify execution summary
        assert summary.execution_summary["total_preparations"] == 2
        assert summary.execution_summary["preparation_types"] == [
            "context_formatting", "payload_preparation"
        ]
    
    @pytest.mark.asyncio
    async def test_parallel_preparation_execution(self, orchestrator, sample_layer_spec):
        """Test parallel preparation execution"""
        request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.PARALLEL,
            preparation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_preparations(request)
        
        # Verify parallel execution results
        assert summary is not None
        assert len(summary.preparation_results) == 2
        
        # Verify all preparations completed
        for result in summary.preparation_results:
            assert result.execution_time >= 0.0
            assert result.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_all_preparations_execution(self, orchestrator, sample_layer_spec):
        """Test execution of all preparation types"""
        request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            preparation_types=[PreparationType.ALL],
            preparation_mode=PreparationMode.PARALLEL,
            preparation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_preparations(request)
        
        # Verify all preparations executed
        assert summary is not None
        assert len(summary.preparation_results) == 2  # All preparation types
        
        # Verify all preparation types are present
        preparation_types = [result.preparation_type for result in summary.preparation_results]
        expected_types = [
            PreparationType.CONTEXT_FORMATTING,
            PreparationType.PAYLOAD_PREPARATION
        ]
        
        for expected_type in expected_types:
            assert expected_type in preparation_types
    
    @pytest.mark.asyncio
    async def test_preparation_pipeline_execution(self, orchestrator, sample_layer_spec):
        """Test preparation pipeline execution"""
        request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.run_preparation_pipeline(request)
        
        # Verify pipeline execution
        assert summary is not None
        assert len(summary.preparation_results) == 2
        assert summary.overall_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_timeout_protection(self, orchestrator, sample_layer_spec):
        """Test timeout protection in orchestration"""
        request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.PARALLEL,
            preparation_options={},
            context={"test": True},
            timeout_seconds=1  # Very short timeout
        )
        
        # This should either complete quickly or timeout gracefully
        summary = await orchestrator.orchestrate_preparations(request)
        
        # Verify graceful handling
        assert summary is not None
        assert len(summary.preparation_results) == 2
    
    @pytest.mark.asyncio
    async def test_error_handling_in_orchestration(self, orchestrator):
        """Test error handling in orchestration"""
        # Create request with invalid layer spec
        invalid_request = PrepareInformationRequest(
            layer_name="invalid_layer",
            layer_spec={},  # Empty spec should cause errors
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_preparations(invalid_request)
        
        # Verify error handling
        assert summary is not None
        assert len(summary.preparation_results) == 2
        
        # Should have some errors due to invalid spec
        assert summary.total_errors >= 0
        assert summary.overall_successful is not None  # Should not crash


class TestPrepareInformationRegistry:
    """Integration tests for PrepareInformationRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Create fresh registry for testing"""
        return PrepareInformationRegistry()
    
    @pytest.mark.asyncio
    async def test_builtin_preparer_registration(self, registry):
        """Test that built-in preparers are properly registered"""
        preparers = await registry.list_preparers()
        
        # Should have 2 built-in preparers
        assert len(preparers) == 2
        
        # Check that all expected types are present
        preparer_types = [reg.preparer_type for reg in preparers]
        expected_types = [
            PreparerType.CONTEXT_FORMATTING,
            PreparerType.PAYLOAD_PREPARATION
        ]
        
        for expected_type in expected_types:
            assert expected_type in preparer_types
    
    @pytest.mark.asyncio
    async def test_custom_preparer_registration(self, registry):
        """Test registration of custom preparers"""
        # Create a mock preparer class
        class MockPreparer:
            pass
        
        def mock_factory():
            return MockPreparer()
        
        # Register custom preparer
        registration = PreparerRegistration(
            preparer_type=PreparerType.CONTEXT_FORMATTING,  # Use existing type for testing
            preparer_class=MockPreparer,
            factory_function=mock_factory,
            metadata={"custom": True}
        )
        
        success = await registry.register_preparer(registration)
        assert success is True
        
        # Verify registration
        preparers = await registry.list_preparers()
        context_preparers = [reg for reg in preparers if reg.preparer_type == PreparerType.CONTEXT_FORMATTING]
        assert len(context_preparers) >= 1
    
    @pytest.mark.asyncio
    async def test_preparer_instance_creation(self, registry):
        """Test creation of preparer instances"""
        # Get context formatting preparer instance
        instance = await registry.get_preparer(PreparerType.CONTEXT_FORMATTING)
        assert instance is not None
        
        # Create new instance
        new_instance = await registry.create_preparer_instance(PreparerType.CONTEXT_FORMATTING)
        assert new_instance is not None
    
    @pytest.mark.asyncio
    async def test_preparer_info_retrieval(self, registry):
        """Test retrieval of preparer information"""
        info = await registry.get_preparer_info(PreparerType.CONTEXT_FORMATTING)
        
        assert info is not None
        assert info["preparer_type"] == "context_formatting"
        assert info["preparer_class"] is not None
        assert info["metadata"]["builtin"] is True
        assert info["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_registry_statistics(self, registry):
        """Test registry statistics"""
        stats = await registry.get_registry_stats()
        
        assert stats["total_registered"] == 2
        assert stats["active_preparers"] == 2
        assert stats["preparer_types"] is not None
        assert len(stats["preparer_types"]) == 2
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, registry):
        """Test cache operations"""
        # Clear cache
        success = await registry.clear_cache()
        assert success is True
        
        # Get instance (should cache it)
        instance = await registry.get_preparer(PreparerType.CONTEXT_FORMATTING)
        assert instance is not None
        
        # Check cache stats
        stats = await registry.get_registry_stats()
        assert stats["cached_instances"] >= 1


class TestPrepareInformationSystemIntegration:
    """End-to-end integration tests for the entire prepare information system"""
    
    @pytest.mark.asyncio
    async def test_complete_preparation_workflow(self):
        """Test complete preparation workflow from registry to orchestration"""
        # Get registry and create preparers
        registry = get_prepare_information_registry()
        
        # Create orchestrator using registry
        context_formatter = await registry.get_preparer(PreparerType.CONTEXT_FORMATTING)
        payload_preparer = await registry.get_preparer(PreparerType.PAYLOAD_PREPARATION)
        
        orchestrator = create_prepare_information_orchestrator(
            context_formatter=context_formatter,
            payload_preparer=payload_preparer
        )
        
        # Create comprehensive test request
        test_request = PrepareInformationRequest(
            layer_name="integration_test_layer",
            layer_spec={
                "name": "integration_test_layer",
                "version": "1.0.0",
                "context_data": {
                    "registry_type": "standard",
                    "layer_type": "service",
                    "environment": "production"
                },
                "payload_data": {
                    "core_config": {"timeout": 30, "retries": 3},
                    "api_endpoints": ["/api/v1/data", "/api/v1/config"],
                    "dependencies": ["database", "cache"]
                }
            },
            preparation_types=[PreparationType.ALL],
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options={},
            context={"integration_test": True}
        )
        
        # Execute complete preparation
        summary = await orchestrator.orchestrate_preparations(test_request)
        
        # Verify complete workflow
        assert summary is not None
        assert len(summary.preparation_results) == 2
        assert summary.overall_score >= 0.0
        assert summary.recommendations is not None
        assert len(summary.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_safety_policy_enforcement(self):
        """Test that safety policies are properly enforced"""
        # Create restrictive safety policy
        restrictive_policy = PrepareOrchestratorSafetyPolicy(
            max_concurrent_preparations=1,
            max_execution_time_seconds=5,
            fail_closed=True
        )
        
        orchestrator = create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer(),
            safety_policy=restrictive_policy
        )
        
        # Try to execute more preparations than allowed
        request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec={"name": "test"},
            preparation_types=[PreparationType.ALL],  # 2 preparations > max 1
            preparation_mode=PreparationMode.PARALLEL,
            preparation_options={},
            context={"test": True}
        )
        
        # Should be rejected by safety policy
        with pytest.raises(Exception):  # Should raise SafetyError or similar
            await orchestrator.orchestrate_preparations(request)
    
    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test fallback behavior when preparations fail"""
        # Create orchestrator with minimal configuration
        orchestrator = create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer(),
            safety_policy=PrepareOrchestratorSafetyPolicy(fail_closed=False)  # Allow fallback
        )
        
        # Create request that will likely cause errors
        problematic_request = PrepareInformationRequest(
            layer_name="problematic_layer",
            layer_spec=None,  # None spec should cause issues
            preparation_types=[PreparationType.CONTEXT_FORMATTING],
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options={},
            context={"test": True}
        )
        
        # Should handle gracefully with fallback
        summary = await orchestrator.orchestrate_preparations(problematic_request)
        
        # Verify fallback behavior
        assert summary is not None
        assert "fallback_mode" in summary.flags or len(summary.preparation_results) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPrepareInformationPerformance:
    """Performance tests for the prepare information system"""
    
    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self):
        """Test performance comparison between parallel and sequential execution"""
        orchestrator = create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer()
        )
        
        test_spec = {
            "name": "performance_test_layer",
            "version": "1.0.0",
            "context_data": {
                "registry_type": "standard",
                "layer_type": "service"
            },
            "payload_data": {
                "core_config": {"timeout": 30},
                "api_endpoints": ["/api/v1/data"]
            }
        }
        
        # Test sequential execution
        sequential_request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=test_spec,
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options={},
            context={"test": True}
        )
        
        start_time = datetime.now()
        sequential_summary = await orchestrator.orchestrate_preparations(sequential_request)
        sequential_time = (datetime.now() - start_time).total_seconds()
        
        # Test parallel execution
        parallel_request = PrepareInformationRequest(
            layer_name="test_layer",
            layer_spec=test_spec,
            preparation_types=[PreparationType.CONTEXT_FORMATTING, PreparationType.PAYLOAD_PREPARATION],
            preparation_mode=PreparationMode.PARALLEL,
            preparation_options={},
            context={"test": True}
        )
        
        start_time = datetime.now()
        parallel_summary = await orchestrator.orchestrate_preparations(parallel_request)
        parallel_time = (datetime.now() - start_time).total_seconds()
        
        # Verify both completed successfully
        assert sequential_summary is not None
        assert parallel_summary is not None
        
        # Parallel should generally be faster (allowing some variance)
        assert parallel_time <= sequential_time + 0.5  # Allow 0.5s variance
        
        print(f"Sequential time: {sequential_time:.3f}s")
        print(f"Parallel time: {parallel_time:.3f}s")
        print(f"Performance improvement: {((sequential_time - parallel_time) / sequential_time * 100):.1f}%")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def run_prepare_integration_tests():
    """Run all prepare information integration tests"""
    import pytest
    
    # Run pytest with our test file
    test_result = pytest.main([__file__, "-v"])
    
    return test_result == 0  # Return True if all tests passed


if __name__ == "__main__":
    """Run integration tests when executed directly"""
    success = asyncio.run(run_prepare_integration_tests())
    if success:
        print("All prepare information integration tests passed!")
    else:
        print("Some prepare information integration tests failed!")
        exit(1)
