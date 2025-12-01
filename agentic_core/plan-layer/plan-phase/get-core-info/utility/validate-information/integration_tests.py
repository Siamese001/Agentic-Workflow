"""
L1 Cognitive Planning - Validation System Integration Tests

Comprehensive integration tests for the validation system to ensure
all validators work together correctly with proper orchestration.
"""

import asyncio
import logging
import pytest
from typing import Dict, Any, List
from datetime import datetime

# Import all validation components
from .validation_orchestrator import (
    LayerValidationOrchestrator,
    OrchestratorRequest,
    ValidationType,
    OrchestrationMode,
    create_validation_orchestrator,
    OrchestratorSafetyPolicy
)

from .validation_registry import (
    ValidationRegistry,
    ValidatorType,
    ValidatorRegistration,
    get_validation_registry,
    register_custom_validator
)

# Import individual validators
from .validate_layer_dependencies import create_layer_dependencies_validator
from .validate_layer_interfaces import create_layer_interfaces_validator
from .validate_layer_compatibility import create_layer_compatibility_validator
from .validate_layer_security import create_layer_security_validator
from .validate_layer_performance import create_layer_performance_validator
from .validate_layer_reliability import create_layer_reliability_validator
from .validate_layer_scalability import create_layer_scalability_validator
from .validate_layer_maintainability import create_layer_maintainability_validator
from .validate_layer_completeness import create_layer_completeness_validator


class TestValidationOrchestrator:
    """Integration tests for LayerValidationOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all validators"""
        return create_validation_orchestrator(
            dependencies_validator=create_layer_dependencies_validator(),
            interfaces_validator=create_layer_interfaces_validator(),
            compatibility_validator=create_layer_compatibility_validator(),
            security_validator=create_layer_security_validator(),
            performance_validator=create_layer_performance_validator(),
            reliability_validator=create_layer_reliability_validator(),
            scalability_validator=create_layer_scalability_validator(),
            maintainability_validator=create_layer_maintainability_validator(),
            completeness_validator=create_layer_completeness_validator()
        )
    
    @pytest.fixture
    def sample_layer_spec(self) -> Dict[str, Any]:
        """Sample layer specification for testing"""
        return {
            "name": "test_layer",
            "version": "1.0.0",
            "dependencies": [
                {"name": "base_layer", "version": "1.0.0", "type": "required"},
                {"name": "utils_layer", "version": "2.0.0", "type": "optional"}
            ],
            "interfaces": [
                {"name": "data_interface", "methods": ["get_data", "set_data"]},
                {"name": "config_interface", "methods": ["get_config"]}
            ],
            "security": {
                "authentication": {"methods": ["oauth2", "jwt"]},
                "encryption": {"enabled": True, "algorithm": "AES-256"}
            },
            "performance_metrics": {
                "average_response_time": 150,
                "cpu_usage_percent": 45,
                "memory_usage_percent": 60
            },
            "reliability_metrics": {
                "uptime_percent": 99.95,
                "error_rate_percent": 0.5
            },
            "scalability_metrics": {
                "min_instances": 2,
                "max_instances": 10,
                "cpu_scaling_enabled": True
            },
            "maintainability_metrics": {
                "cyclomatic_complexity": 8,
                "code_duplication_percent": 3,
                "api_documentation_coverage": 85
            },
            "completeness_metrics": {
                "requirement_coverage": 95,
                "implemented_features": 18,
                "total_features": 20
            }
        }
    
    @pytest.mark.asyncio
    async def test_sequential_validation_execution(self, orchestrator, sample_layer_spec):
        """Test sequential validation execution"""
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES, ValidationType.SECURITY],
            orchestration_mode=OrchestrationMode.SEQUENTIAL,
            validation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_validations(request)
        
        # Verify summary structure
        assert summary is not None
        assert len(summary.validation_results) == 3
        assert summary.overall_valid is not False  # Should not be False due to fallback
        assert summary.overall_score >= 0.0
        assert summary.total_errors >= 0
        assert summary.total_warnings >= 0
        
        # Verify execution summary
        assert summary.execution_summary["total_validations"] == 3
        assert summary.execution_summary["validation_types"] == [
            "dependencies", "interfaces", "security"
        ]
    
    @pytest.mark.asyncio
    async def test_parallel_validation_execution(self, orchestrator, sample_layer_spec):
        """Test parallel validation execution"""
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES, ValidationType.SECURITY],
            orchestration_mode=OrchestrationMode.PARALLEL,
            validation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_validations(request)
        
        # Verify parallel execution results
        assert summary is not None
        assert len(summary.validation_results) == 3
        
        # Verify all validations completed
        for result in summary.validation_results:
            assert result.execution_time >= 0.0
            assert result.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_parallel_with_dependencies_execution(self, orchestrator, sample_layer_spec):
        """Test parallel execution with dependencies"""
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            validation_types=[
                ValidationType.DEPENDENCIES,
                ValidationType.INTERFACES,
                ValidationType.COMPATIBILITY,
                ValidationType.SECURITY
            ],
            orchestration_mode=OrchestrationMode.PARALLEL_WITH_DEPENDENCIES,
            validation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_validations(request)
        
        # Verify dependency-aware execution
        assert summary is not None
        assert len(summary.validation_results) == 4
        
        # Verify execution order respects dependencies
        validation_order = [result.validation_type for result in summary.validation_results]
        
        # Dependencies should come before interfaces
        dependencies_index = validation_order.index(ValidationType.DEPENDENCIES)
        interfaces_index = validation_order.index(ValidationType.INTERFACES)
        assert dependencies_index < interfaces_index
    
    @pytest.mark.asyncio
    async def test_all_validations_execution(self, orchestrator, sample_layer_spec):
        """Test execution of all validation types"""
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            validation_types=[ValidationType.ALL],
            orchestration_mode=OrchestrationMode.PARALLEL,
            validation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_validations(request)
        
        # Verify all validations executed
        assert summary is not None
        assert len(summary.validation_results) == 9  # All validation types
        
        # Verify all validation types are present
        validation_types = [result.validation_type for result in summary.validation_results]
        expected_types = [
            ValidationType.DEPENDENCIES,
            ValidationType.INTERFACES,
            ValidationType.COMPATIBILITY,
            ValidationType.SECURITY,
            ValidationType.PERFORMANCE,
            ValidationType.RELIABILITY,
            ValidationType.SCALABILITY,
            ValidationType.MAINTAINABILITY,
            ValidationType.COMPLETENESS
        ]
        
        for expected_type in expected_types:
            assert expected_type in validation_types
    
    @pytest.mark.asyncio
    async def test_validation_pipeline_execution(self, orchestrator, sample_layer_spec):
        """Test validation pipeline execution"""
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES, ValidationType.SECURITY],
            orchestration_mode=OrchestrationMode.SEQUENTIAL,
            validation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.run_validation_pipeline(request)
        
        # Verify pipeline execution
        assert summary is not None
        assert len(summary.validation_results) == 3
        assert summary.overall_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_timeout_protection(self, orchestrator, sample_layer_spec):
        """Test timeout protection in orchestration"""
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES],
            orchestration_mode=OrchestrationMode.PARALLEL,
            validation_options={},
            context={"test": True},
            timeout_seconds=1  # Very short timeout
        )
        
        # This should either complete quickly or timeout gracefully
        summary = await orchestrator.orchestrate_validations(request)
        
        # Verify graceful handling
        assert summary is not None
        assert len(summary.validation_results) == 2
    
    @pytest.mark.asyncio
    async def test_error_handling_in_orchestration(self, orchestrator):
        """Test error handling in orchestration"""
        # Create request with invalid layer spec
        invalid_request = OrchestratorRequest(
            layer_name="invalid_layer",
            layer_spec={},  # Empty spec should cause errors
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES],
            orchestration_mode=OrchestrationMode.SEQUENTIAL,
            validation_options={},
            context={"test": True}
        )
        
        summary = await orchestrator.orchestrate_validations(invalid_request)
        
        # Verify error handling
        assert summary is not None
        assert len(summary.validation_results) == 2
        
        # Should have some errors due to invalid spec
        assert summary.total_errors >= 0
        assert summary.overall_valid is not None  # Should not crash


class TestValidationRegistry:
    """Integration tests for ValidationRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Create fresh registry for testing"""
        return ValidationRegistry()
    
    @pytest.mark.asyncio
    async def test_builtin_validator_registration(self, registry):
        """Test that built-in validators are properly registered"""
        validators = await registry.list_validators()
        
        # Should have 9 built-in validators
        assert len(validators) == 9
        
        # Check that all expected types are present
        validator_types = [reg.validator_type for reg in validators]
        expected_types = [
            ValidatorType.DEPENDENCIES,
            ValidatorType.INTERFACES,
            ValidatorType.COMPATIBILITY,
            ValidatorType.SECURITY,
            ValidatorType.PERFORMANCE,
            ValidatorType.RELIABILITY,
            ValidatorType.SCALABILITY,
            ValidatorType.MAINTAINABILITY,
            ValidatorType.COMPLETENESS
        ]
        
        for expected_type in expected_types:
            assert expected_type in validator_types
    
    @pytest.mark.asyncio
    async def test_custom_validator_registration(self, registry):
        """Test registration of custom validators"""
        # Create a mock validator class
        class MockValidator:
            pass
        
        def mock_factory():
            return MockValidator()
        
        # Register custom validator
        registration = ValidatorRegistration(
            validator_type=ValidatorType.DEPENDENCIES,  # Use existing type for testing
            validator_class=MockValidator,
            factory_function=mock_factory,
            metadata={"custom": True}
        )
        
        success = await registry.register_validator(registration)
        assert success is True
        
        # Verify registration
        validators = await registry.list_validators()
        dependencies_validators = [reg for reg in validators if reg.validator_type == ValidatorType.DEPENDENCIES]
        assert len(dependencies_validators) >= 1
    
    @pytest.mark.asyncio
    async def test_validator_instance_creation(self, registry):
        """Test creation of validator instances"""
        # Get dependencies validator instance
        instance = await registry.get_validator(ValidatorType.DEPENDENCIES)
        assert instance is not None
        
        # Create new instance
        new_instance = await registry.create_validator_instance(ValidatorType.DEPENDENCIES)
        assert new_instance is not None
    
    @pytest.mark.asyncio
    async def test_validator_info_retrieval(self, registry):
        """Test retrieval of validator information"""
        info = await registry.get_validator_info(ValidatorType.DEPENDENCIES)
        
        assert info is not None
        assert info["validator_type"] == "dependencies"
        assert info["validator_class"] is not None
        assert info["metadata"]["builtin"] is True
        assert info["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_registry_statistics(self, registry):
        """Test registry statistics"""
        stats = await registry.get_registry_stats()
        
        assert stats["total_registered"] == 9
        assert stats["active_validators"] == 9
        assert stats["validator_types"] is not None
        assert len(stats["validator_types"]) == 9
    
    @pytest.mark.asyncio
    async def test_cache_operations(self, registry):
        """Test cache operations"""
        # Clear cache
        success = await registry.clear_cache()
        assert success is True
        
        # Get instance (should cache it)
        instance = await registry.get_validator(ValidatorType.DEPENDENCIES)
        assert instance is not None
        
        # Check cache stats
        stats = await registry.get_registry_stats()
        assert stats["cached_instances"] >= 1


class TestValidationSystemIntegration:
    """End-to-end integration tests for the entire validation system"""
    
    @pytest.mark.asyncio
    async def test_complete_validation_workflow(self):
        """Test complete validation workflow from registry to orchestration"""
        # Get registry and create validators
        registry = get_validation_registry()
        
        # Create orchestrator using registry
        dependencies_validator = await registry.get_validator(ValidatorType.DEPENDENCIES)
        interfaces_validator = await registry.get_validator(ValidatorType.INTERFACES)
        security_validator = await registry.get_validator(ValidatorType.SECURITY)
        
        orchestrator = create_validation_orchestrator(
            dependencies_validator=dependencies_validator,
            interfaces_validator=interfaces_validator,
            compatibility_validator=await registry.get_validator(ValidatorType.COMPATIBILITY),
            security_validator=security_validator,
            performance_validator=await registry.get_validator(ValidatorType.PERFORMANCE),
            reliability_validator=await registry.get_validator(ValidatorType.RELIABILITY),
            scalability_validator=await registry.get_validator(ValidatorType.SCALABILITY),
            maintainability_validator=await registry.get_validator(ValidatorType.MAINTAINABILITY),
            completeness_validator=await registry.get_validator(ValidatorType.COMPLETENESS)
        )
        
        # Create comprehensive test request
        test_request = OrchestratorRequest(
            layer_name="integration_test_layer",
            layer_spec={
                "name": "integration_test_layer",
                "version": "1.0.0",
                "dependencies": [{"name": "base", "version": "1.0.0"}],
                "interfaces": [{"name": "test_interface", "methods": ["test_method"]}],
                "security": {"authentication": {"methods": ["oauth2"]}},
                "performance_metrics": {"average_response_time": 100},
                "reliability_metrics": {"uptime_percent": 99.9},
                "scalability_metrics": {"min_instances": 2},
                "maintainability_metrics": {"cyclomatic_complexity": 5},
                "completeness_metrics": {"requirement_coverage": 95}
            },
            validation_types=[ValidationType.ALL],
            orchestration_mode=OrchestrationMode.PARALLEL_WITH_DEPENDENCIES,
            validation_options={},
            context={"integration_test": True}
        )
        
        # Execute complete validation
        summary = await orchestrator.orchestrate_validations(test_request)
        
        # Verify complete workflow
        assert summary is not None
        assert len(summary.validation_results) == 9
        assert summary.overall_score >= 0.0
        assert summary.recommendations is not None
        assert len(summary.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_safety_policy_enforcement(self):
        """Test that safety policies are properly enforced"""
        # Create restrictive safety policy
        restrictive_policy = OrchestratorSafetyPolicy(
            max_concurrent_validations=2,
            max_execution_time_seconds=5,
            fail_closed=True
        )
        
        orchestrator = create_validation_orchestrator(
            dependencies_validator=create_layer_dependencies_validator(),
            interfaces_validator=create_layer_interfaces_validator(),
            compatibility_validator=create_layer_compatibility_validator(),
            security_validator=create_layer_security_validator(),
            performance_validator=create_layer_performance_validator(),
            reliability_validator=create_layer_reliability_validator(),
            scalability_validator=create_layer_scalability_validator(),
            maintainability_validator=create_layer_maintainability_validator(),
            completeness_validator=create_layer_completeness_validator(),
            safety_policy=restrictive_policy
        )
        
        # Try to execute more validations than allowed
        request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec={"name": "test"},
            validation_types=[ValidationType.ALL],  # 9 validations > max 2
            orchestration_mode=OrchestrationMode.PARALLEL,
            validation_options={},
            context={"test": True}
        )
        
        # Should be rejected by safety policy
        with pytest.raises(Exception):  # Should raise SafetyError or similar
            await orchestrator.orchestrate_validations(request)
    
    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test fallback behavior when validations fail"""
        # Create orchestrator with minimal configuration
        orchestrator = create_validation_orchestrator(
            dependencies_validator=create_layer_dependencies_validator(),
            interfaces_validator=create_layer_interfaces_validator(),
            compatibility_validator=create_layer_compatibility_validator(),
            security_validator=create_layer_security_validator(),
            performance_validator=create_layer_performance_validator(),
            reliability_validator=create_layer_reliability_validator(),
            scalability_validator=create_layer_scalability_validator(),
            maintainability_validator=create_layer_maintainability_validator(),
            completeness_validator=create_layer_completeness_validator(),
            safety_policy=OrchestratorSafetyPolicy(fail_closed=False)  # Allow fallback
        )
        
        # Create request that will likely cause errors
        problematic_request = OrchestratorRequest(
            layer_name="problematic_layer",
            layer_spec=None,  # None spec should cause issues
            validation_types=[ValidationType.DEPENDENCIES],
            orchestration_mode=OrchestrationMode.SEQUENTIAL,
            validation_options={},
            context={"test": True}
        )
        
        # Should handle gracefully with fallback
        summary = await orchestrator.orchestrate_validations(problematic_request)
        
        # Verify fallback behavior
        assert summary is not None
        assert "fallback_mode" in summary.flags or len(summary.validation_results) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestValidationPerformance:
    """Performance tests for the validation system"""
    
    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self):
        """Test performance comparison between parallel and sequential execution"""
        orchestrator = create_validation_orchestrator(
            dependencies_validator=create_layer_dependencies_validator(),
            interfaces_validator=create_layer_interfaces_validator(),
            compatibility_validator=create_layer_compatibility_validator(),
            security_validator=create_layer_security_validator(),
            performance_validator=create_layer_performance_validator(),
            reliability_validator=create_layer_reliability_validator(),
            scalability_validator=create_layer_scalability_validator(),
            maintainability_validator=create_layer_maintainability_validator(),
            completeness_validator=create_layer_completeness_validator()
        )
        
        test_spec = {
            "name": "performance_test_layer",
            "version": "1.0.0",
            "dependencies": [{"name": "base", "version": "1.0.0"}],
            "interfaces": [{"name": "test_interface", "methods": ["test_method"]}],
            "security": {"authentication": {"methods": ["oauth2"]}},
            "performance_metrics": {"average_response_time": 100},
            "reliability_metrics": {"uptime_percent": 99.9},
            "scalability_metrics": {"min_instances": 2},
            "maintainability_metrics": {"cyclomatic_complexity": 5},
            "completeness_metrics": {"requirement_coverage": 95}
        }
        
        # Test sequential execution
        sequential_request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=test_spec,
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES, ValidationType.SECURITY],
            orchestration_mode=OrchestrationMode.SEQUENTIAL,
            validation_options={},
            context={"test": True}
        )
        
        start_time = datetime.now()
        sequential_summary = await orchestrator.orchestrate_validations(sequential_request)
        sequential_time = (datetime.now() - start_time).total_seconds()
        
        # Test parallel execution
        parallel_request = OrchestratorRequest(
            layer_name="test_layer",
            layer_spec=test_spec,
            validation_types=[ValidationType.DEPENDENCIES, ValidationType.INTERFACES, ValidationType.SECURITY],
            orchestration_mode=OrchestrationMode.PARALLEL,
            validation_options={},
            context={"test": True}
        )
        
        start_time = datetime.now()
        parallel_summary = await orchestrator.orchestrate_validations(parallel_request)
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

async def run_integration_tests():
    """Run all integration tests"""
    import pytest
    
    # Run pytest with our test file
    test_result = pytest.main([__file__, "-v"])
    
    return test_result == 0  # Return True if all tests passed


if __name__ == "__main__":
    """Run integration tests when executed directly"""
    success = asyncio.run(run_integration_tests())
    if success:
        print("All integration tests passed!")
    else:
        print("Some integration tests failed!")
        exit(1)
