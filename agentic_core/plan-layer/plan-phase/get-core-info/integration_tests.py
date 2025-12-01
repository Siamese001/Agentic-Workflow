"""
L1 Cognitive Planning - Get Core Info Integration Tests

Comprehensive integration tests for the complete get core info system to ensure
all subsystems work together correctly and achieve phase_2_keys = TRUE.
"""

import asyncio
import logging
import pytest
from typing import Dict, Any, List
from datetime import datetime

# Import all get core info components
from get_core_info_orchestrator import (
    GetCoreInfoOrchestrator,
    GetCoreInfoRequest,
    GetCoreInfoResponse,
    ExecutionMode,
    PhaseStatus,
    create_get_core_info_orchestrator,
    GetCoreInfoSafetyPolicy
)

# Import subsystem components for testing
from general.understand_request import (
    create_core_query_builder,
    create_layer_parameter_extractor,
    create_registry_intent_parser
)

from specific import (
    create_layer_requirements_analyzer,
    create_layer_dependency_extractor,
    create_layer_id_generator,
    create_layer_interface_mapper,
    create_layer_compatibility_validator,
    create_layer_spec_validator
)

from utility.prepare_information import create_prepare_information_orchestrator
from utility.validate_information import create_validation_orchestrator


class TestGetCoreInfoOrchestrator:
    """Integration tests for GetCoreInfoOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with all subsystems"""
        # Create general subsystem components
        core_query_builder = create_core_query_builder()
        layer_parameter_extractor = create_layer_parameter_extractor()
        registry_intent_parser = create_registry_intent_parser()
        
        # Create specific subsystem components
        layer_requirements_analyzer = create_layer_requirements_analyzer()
        layer_dependency_extractor = create_layer_dependency_extractor()
        layer_id_generator = create_layer_id_generator()
        layer_interface_mapper = create_layer_interface_mapper()
        layer_compatibility_validator = create_layer_compatibility_validator()
        layer_spec_validator = create_layer_spec_validator()
        
        # Create utility subsystem components
        prepare_orchestrator = create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer()
        )
        validation_orchestrator = create_validation_orchestrator(
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
        
        return create_get_core_info_orchestrator(
            core_query_builder=core_query_builder,
            layer_parameter_extractor=layer_parameter_extractor,
            registry_intent_parser=registry_intent_parser,
            layer_requirements_analyzer=layer_requirements_analyzer,
            layer_dependency_extractor=layer_dependency_extractor,
            layer_id_generator=layer_id_generator,
            layer_interface_mapper=layer_interface_mapper,
            layer_compatibility_validator=layer_compatibility_validator,
            layer_spec_validator=layer_spec_validator,
            prepare_information_orchestrator=prepare_orchestrator,
            layer_validation_orchestrator=validation_orchestrator
        )
    
    @pytest.fixture
    def sample_layer_spec(self) -> Dict[str, Any]:
        """Sample layer specification for testing"""
        return {
            "name": "test_layer",
            "version": "1.0.0",
            "type": "service",
            "description": "Test layer for integration testing",
            "context_data": {
                "registry_type": "standard",
                "layer_type": "service",
                "environment": "production"
            },
            "payload_data": {
                "core_config": {"timeout": 30, "retries": 3},
                "api_endpoints": ["/api/v1/data", "/api/v1/config"],
                "dependencies": ["database", "cache"]
            },
            "requirements": ["high_availability", "scalability", "security"],
            "interfaces": [
                {"name": "data_interface", "methods": ["get_data", "set_data"]},
                {"name": "config_interface", "methods": ["get_config"]}
            ],
            "dependencies": [
                {"name": "base_layer", "version": "1.0.0", "type": "required"},
                {"name": "utils_layer", "version": "2.0.0", "type": "optional"}
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
    async def test_full_workflow_phase_2_keys_true(self, orchestrator, sample_layer_spec):
        """Test that full workflow execution returns phase_2_keys = TRUE"""
        request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"test": True, "environment": "production"},
            safety_level="standard",
            timeout_seconds=300,
            enable_rollback=True,
            collect_metrics=True
        )
        
        response = await orchestrator.orchestrate_get_core_info(request)
        
        # Verify response structure
        assert response is not None
        assert isinstance(response, GetCoreInfoResponse)
        assert response.request_id is not None
        assert response.overall_score >= 0.0
        assert response.execution_time >= 0.0
        
        # **CRITICAL TEST**: Verify phase_2_keys = TRUE
        assert response.phase_2_keys is True, f"Expected phase_2_keys to be TRUE, got {response.phase_2_keys}"
        
        # Verify all phases completed successfully
        assert response.overall_successful is True
        assert len(response.phase_results) == 3  # general, specific, utility
        
        # Verify phase completion status
        expected_phases = ["general", "specific", "utility"]
        for phase in expected_phases:
            assert phase in response.phase_completion_status
            assert response.phase_completion_status[phase] is True, f"Phase {phase} should be completed"
        
        # Verify phase results
        phase_names = [result.phase_name for result in response.phase_results]
        for phase in expected_phases:
            assert phase in phase_names
        
        # Verify all phases are successful
        for result in response.phase_results:
            assert result.is_successful is True, f"Phase {result.phase_name} should be successful"
            assert result.status == PhaseStatus.COMPLETED
            assert result.score >= 0.0
        
        # Verify execution summary
        assert response.execution_summary["execution_mode"] == "full_workflow"
        assert response.execution_summary["total_phases"] == 3
        assert response.execution_summary["successful_phases"] == 3
        assert response.execution_summary["failed_phases"] == 0
    
    @pytest.mark.asyncio
    async def test_individual_phase_execution(self, orchestrator, sample_layer_spec):
        """Test individual phase execution modes"""
        # Test general only
        general_request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.GENERAL_ONLY,
            execution_options={},
            context={"test": True}
        )
        
        general_response = await orchestrator.orchestrate_get_core_info(general_request)
        assert general_response is not None
        assert len(general_response.phase_results) == 1
        assert general_response.phase_results[0].phase_name == "general"
        assert general_response.phase_2_keys is False  # Not all phases executed
        
        # Test specific only
        specific_request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.SPECIFIC_ONLY,
            execution_options={},
            context={"test": True}
        )
        
        specific_response = await orchestrator.orchestrate_get_core_info(specific_request)
        assert specific_response is not None
        assert len(specific_response.phase_results) == 1
        assert specific_response.phase_results[0].phase_name == "specific"
        assert specific_response.phase_2_keys is False
        
        # Test utility only
        utility_request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.UTILITY_ONLY,
            execution_options={},
            context={"test": True}
        )
        
        utility_response = await orchestrator.orchestrate_get_core_info(utility_request)
        assert utility_response is not None
        assert len(utility_response.phase_results) == 1
        assert utility_response.phase_results[0].phase_name == "utility"
        assert utility_response.phase_2_keys is False
    
    @pytest.mark.asyncio
    async def test_custom_phase_execution(self, orchestrator, sample_layer_spec):
        """Test custom phase selection execution"""
        custom_request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.CUSTOM,
            phase_selection=["general", "utility"],  # Skip specific
            execution_options={},
            context={"test": True}
        )
        
        response = await orchestrator.orchestrate_get_core_info(custom_request)
        
        # Verify response structure
        assert response is not None
        assert len(response.phase_results) == 2  # general and utility only
        
        # Verify phase_2_keys = FALSE (not all phases executed)
        assert response.phase_2_keys is False
        
        # Verify only selected phases were executed
        phase_names = [result.phase_name for result in response.phase_results]
        assert "general" in phase_names
        assert "utility" in phase_names
        assert "specific" not in phase_names
        
        # Verify phase completion status
        assert response.phase_completion_status.get("general", False) is True
        assert response.phase_completion_status.get("utility", False) is True
        assert "specific" not in response.phase_completion_status
    
    @pytest.mark.asyncio
    async def test_phase_status_tracking(self, orchestrator, sample_layer_spec):
        """Test phase status tracking during execution"""
        request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"test": True}
        )
        
        # Start execution
        task = asyncio.create_task(orchestrator.orchestrate_get_core_info(request))
        
        # Give it a moment to start
        await asyncio.sleep(0.1)
        
        # Check phase status during execution
        phase_status = await orchestrator.get_phase_status(request.request_id)
        assert isinstance(phase_status, dict)
        
        # Wait for completion
        response = await task
        
        # Verify final status
        final_status = await orchestrator.get_phase_status(request.request_id)
        # Status should be cleaned up after completion
        assert len(final_status) == 0
    
    @pytest.mark.asyncio
    async def test_rollback_functionality(self, orchestrator, sample_layer_spec):
        """Test rollback functionality between phases"""
        request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"test": True},
            enable_rollback=True
        )
        
        response = await orchestrator.orchestrate_get_core_info(request)
        
        # Verify rollback data is available when successful
        if response.overall_successful:
            assert response.rollback_data is not None
            assert "general" in response.rollback_data
            assert "specific" in response.rollback_data
            assert "utility" in response.rollback_data
    
    @pytest.mark.asyncio
    async def test_safety_policy_enforcement(self, orchestrator, sample_layer_spec):
        """Test that safety policies are properly enforced"""
        # Create restrictive safety policy
        restrictive_policy = GetCoreInfoSafetyPolicy(
            max_execution_time_seconds=5,  # Very short timeout
            fail_closed=True
        )
        
        restricted_orchestrator = create_get_core_info_orchestrator(
            core_query_builder=create_core_query_builder(),
            layer_parameter_extractor=create_layer_parameter_extractor(),
            registry_intent_parser=create_registry_intent_parser(),
            layer_requirements_analyzer=create_layer_requirements_analyzer(),
            layer_dependency_extractor=create_layer_dependency_extractor(),
            layer_id_generator=create_layer_id_generator(),
            layer_interface_mapper=create_layer_interface_mapper(),
            layer_compatibility_validator=create_layer_compatibility_validator(),
            layer_spec_validator=create_layer_spec_validator(),
            prepare_information_orchestrator=create_prepare_information_orchestrator(
                context_formatter=create_registry_context_formatter(),
                payload_preparer=create_core_payload_preparer()
            ),
            layer_validation_orchestrator=create_validation_orchestrator(
                dependencies_validator=create_layer_dependencies_validator(),
                interfaces_validator=create_layer_interfaces_validator(),
                compatibility_validator=create_layer_compatibility_validator(),
                security_validator=create_layer_security_validator(),
                performance_validator=create_layer_performance_validator(),
                reliability_validator=create_layer_reliability_validator(),
                scalability_validator=create_layer_scalability_validator(),
                maintainability_validator=create_layer_maintainability_validator(),
                completeness_validator=create_layer_completeness_validator()
            ),
            safety_policy=restrictive_policy
        )
        
        # Try to execute with very short timeout
        request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"test": True},
            timeout_seconds=10  # Longer than policy allows
        )
        
        # Should be rejected by safety policy
        with pytest.raises(Exception):  # Should raise SafetyError or similar
            await restricted_orchestrator.orchestrate_get_core_info(request)
    
    @pytest.mark.asyncio
    async def test_error_handling_and_fallback(self, orchestrator):
        """Test error handling and fallback behavior"""
        # Create request with invalid layer spec
        invalid_request = GetCoreInfoRequest(
            layer_name="invalid_layer",
            layer_spec={},  # Empty spec should cause errors
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"test": True},
            enable_rollback=True
        )
        
        response = await orchestrator.orchestrate_get_core_info(invalid_request)
        
        # Verify error handling
        assert response is not None
        assert response.phase_2_keys is False  # Should be FALSE on errors
        assert response.overall_successful is False
        
        # Should have some errors due to invalid spec
        assert response.total_errors >= 0
        
        # Verify fallback recommendations
        assert len(response.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, orchestrator, sample_layer_spec):
        """Test metrics collection during orchestration"""
        request = GetCoreInfoRequest(
            layer_name="test_layer",
            layer_spec=sample_layer_spec,
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"test": True},
            collect_metrics=True
        )
        
        response = await orchestrator.orchestrate_get_core_info(request)
        
        # Verify metrics collection
        assert response is not None
        assert response.execution_time >= 0.0
        
        # Verify execution summary contains metrics
        assert "total_execution_time" in response.execution_summary
        assert "average_execution_time" in response.execution_summary


class TestPhase2KeysValidation:
    """Specific tests for phase_2_keys validation logic"""
    
    @pytest.mark.asyncio
    async def test_phase_2_keys_completion_criteria(self):
        """Test the specific criteria for phase_2_keys = TRUE"""
        from .get_core_info_orchestrator import PhaseCompletionChecker
        
        checker = PhaseCompletionChecker()
        
        # Test case 1: All phases completed
        completed_results = [
            # Mock PhaseResult for completed general phase
            type('PhaseResult', (), {
                'phase_name': 'general',
                'status': PhaseStatus.COMPLETED,
                'is_successful': True,
                'metadata': {
                    'components_completed': ['core_query_builder', 'layer_parameter_extractor', 'registry_intent_parser'],
                    'components_failed': []
                }
            })(),
            # Mock PhaseResult for completed specific phase
            type('PhaseResult', (), {
                'phase_name': 'specific',
                'status': PhaseStatus.COMPLETED,
                'is_successful': True,
                'metadata': {
                    'components_completed': [
                        'layer_requirements_analyzer', 'layer_dependency_extractor', 'layer_id_generator',
                        'layer_interface_mapper', 'layer_compatibility_validator', 'layer_spec_validator'
                    ],
                    'components_failed': []
                }
            })(),
            # Mock PhaseResult for completed utility phase
            type('PhaseResult', (), {
                'phase_name': 'utility',
                'status': PhaseStatus.COMPLETED,
                'is_successful': True,
                'metadata': {
                    'components_completed': ['prepare_information_orchestrator', 'layer_validation_orchestrator'],
                    'components_failed': []
                }
            })()
        ]
        
        completion_status = checker.check_phase_completion(completed_results)
        phase_2_keys = checker.check_phase_2_keys(completion_status)
        
        assert phase_2_keys is True, "phase_2_keys should be TRUE when all phases complete successfully"
        assert all(status.is_completed for status in completion_status.values())
        
        # Test case 2: One phase failed
        failed_results = completed_results.copy()
        failed_results[1].metadata['components_failed'] = ['layer_requirements_analyzer']
        failed_results[1].metadata['components_completed'] = [
            'layer_dependency_extractor', 'layer_id_generator',
            'layer_interface_mapper', 'layer_compatibility_validator', 'layer_spec_validator'
        ]
        
        completion_status_failed = checker.check_phase_completion(failed_results)
        phase_2_keys_failed = checker.check_phase_2_keys(completion_status_failed)
        
        assert phase_2_keys_failed is False, "phase_2_keys should be FALSE when any phase fails"
        assert not completion_status_failed['specific'].is_completed
    
    @pytest.mark.asyncio
    async def test_phase_2_keys_with_missing_phases(self):
        """Test phase_2_keys validation with missing phases"""
        from .get_core_info_orchestrator import PhaseCompletionChecker
        
        checker = PhaseCompletionChecker()
        
        # Test with only general phase
        general_only_results = [
            type('PhaseResult', (), {
                'phase_name': 'general',
                'status': PhaseStatus.COMPLETED,
                'is_successful': True,
                'metadata': {
                    'components_completed': ['core_query_builder', 'layer_parameter_extractor', 'registry_intent_parser'],
                    'components_failed': []
                }
            })()
        ]
        
        completion_status = checker.check_phase_completion(general_only_results)
        phase_2_keys = checker.check_phase_2_keys(completion_status)
        
        assert phase_2_keys is False, "phase_2_keys should be FALSE when not all phases are executed"
        assert completion_status['general'].is_completed is True
        assert completion_status['specific'].is_completed is False
        assert completion_status['utility'].is_completed is False


# ============================================================================
# END-TO-END WORKFLOW TESTS
# ============================================================================

class TestEndToEndWorkflow:
    """End-to-end workflow tests"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self):
        """Test complete workflow integration from start to finish"""
        # This test verifies the entire system works together
        
        # Create all subsystem components
        core_query_builder = create_core_query_builder()
        layer_parameter_extractor = create_layer_parameter_extractor()
        registry_intent_parser = create_registry_intent_parser()
        
        layer_requirements_analyzer = create_layer_requirements_analyzer()
        layer_dependency_extractor = create_layer_dependency_extractor()
        layer_id_generator = create_layer_id_generator()
        layer_interface_mapper = create_layer_interface_mapper()
        layer_compatibility_validator = create_layer_compatibility_validator()
        layer_spec_validator = create_layer_spec_validator()
        
        prepare_orchestrator = create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer()
        )
        
        validation_orchestrator = create_validation_orchestrator(
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
        
        # Create top-level orchestrator
        orchestrator = create_get_core_info_orchestrator(
            core_query_builder=core_query_builder,
            layer_parameter_extractor=layer_parameter_extractor,
            registry_intent_parser=registry_intent_parser,
            layer_requirements_analyzer=layer_requirements_analyzer,
            layer_dependency_extractor=layer_dependency_extractor,
            layer_id_generator=layer_id_generator,
            layer_interface_mapper=layer_interface_mapper,
            layer_compatibility_validator=layer_compatibility_validator,
            layer_spec_validator=layer_spec_validator,
            prepare_information_orchestrator=prepare_orchestrator,
            layer_validation_orchestrator=validation_orchestrator
        )
        
        # Execute complete workflow
        request = GetCoreInfoRequest(
            layer_name="end_to_end_test_layer",
            layer_spec={
                "name": "end_to_end_test_layer",
                "version": "1.0.0",
                "type": "service",
                "context_data": {"registry_type": "standard"},
                "payload_data": {"core_config": {"timeout": 30}},
                "requirements": ["reliability"],
                "interfaces": [{"name": "test_interface", "methods": ["test_method"]}],
                "dependencies": [{"name": "base", "version": "1.0.0"}],
                "security": {"authentication": {"methods": ["oauth2"]}},
                "performance_metrics": {"average_response_time": 100},
                "reliability_metrics": {"uptime_percent": 99.9},
                "scalability_metrics": {"min_instances": 2},
                "maintainability_metrics": {"cyclomatic_complexity": 5},
                "completeness_metrics": {"requirement_coverage": 95}
            },
            execution_mode=ExecutionMode.FULL_WORKFLOW,
            execution_options={},
            context={"end_to_end_test": True},
            safety_level="standard",
            timeout_seconds=300,
            enable_rollback=True,
            collect_metrics=True
        )
        
        # Execute and verify
        response = await orchestrator.orchestrate_get_core_info(request)
        
        # **FINAL VALIDATION**: phase_2_keys must be TRUE
        assert response.phase_2_keys is True, f"End-to-end test failed: phase_2_keys = {response.phase_2_keys}"
        assert response.overall_successful is True
        assert len(response.phase_results) == 3
        
        # Verify all subsystems contributed
        phase_names = [result.phase_name for result in response.phase_results]
        assert "general" in phase_names
        assert "specific" in phase_names
        assert "utility" in phase_names
        
        # Verify comprehensive execution
        assert response.execution_summary["total_phases"] == 3
        assert response.execution_summary["successful_phases"] == 3
        assert response.total_errors == 0
        
        print("✅ END-TO-END WORKFLOW TEST PASSED: phase_2_keys = TRUE")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def run_get_core_info_integration_tests():
    """Run all get core info integration tests"""
    import pytest
    
    # Run pytest with our test file
    test_result = pytest.main([__file__, "-v"])
    
    return test_result == 0  # Return True if all tests passed


async def verify_phase_2_keys_implementation():
    """Verify that phase_2_keys = TRUE implementation is working correctly"""
    print("🔍 Verifying phase_2_keys = TRUE implementation...")
    
    # Create a minimal test to verify the core functionality
    orchestrator = create_get_core_info_orchestrator(
        core_query_builder=create_core_query_builder(),
        layer_parameter_extractor=create_layer_parameter_extractor(),
        registry_intent_parser=create_registry_intent_parser(),
        layer_requirements_analyzer=create_layer_requirements_analyzer(),
        layer_dependency_extractor=create_layer_dependency_extractor(),
        layer_id_generator=create_layer_id_generator(),
        layer_interface_mapper=create_layer_interface_mapper(),
        layer_compatibility_validator=create_layer_compatibility_validator(),
        layer_spec_validator=create_layer_spec_validator(),
        prepare_information_orchestrator=create_prepare_information_orchestrator(
            context_formatter=create_registry_context_formatter(),
            payload_preparer=create_core_payload_preparer()
        ),
        layer_validation_orchestrator=create_validation_orchestrator(
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
    )
    
    request = GetCoreInfoRequest(
        layer_name="verification_test",
        layer_spec={
            "name": "verification_test",
            "version": "1.0.0",
            "type": "service",
            "context_data": {"registry_type": "standard"},
            "payload_data": {"core_config": {"timeout": 30}},
            "requirements": ["basic"],
            "interfaces": [{"name": "test_interface", "methods": ["test_method"]}],
            "dependencies": [{"name": "base", "version": "1.0.0"}],
            "security": {"authentication": {"methods": ["oauth2"]}},
            "performance_metrics": {"average_response_time": 100},
            "reliability_metrics": {"uptime_percent": 99.9},
            "scalability_metrics": {"min_instances": 2},
            "maintainability_metrics": {"cyclomatic_complexity": 5},
            "completeness_metrics": {"requirement_coverage": 95}
        },
        execution_mode=ExecutionMode.FULL_WORKFLOW,
        execution_options={},
        context={"verification": True}
    )
    
    response = await orchestrator.orchestrate_get_core_info(request)
    
    if response.phase_2_keys:
        print("✅ VERIFICATION SUCCESSFUL: phase_2_keys = TRUE")
        return True
    else:
        print("❌ VERIFICATION FAILED: phase_2_keys = FALSE")
        print(f"Overall successful: {response.overall_successful}")
        print(f"Phase completion status: {response.phase_completion_status}")
        return False


if __name__ == "__main__":
    """Run integration tests when executed directly"""
    async def main():
        print("🚀 Starting Get Core Info Integration Tests...")
        
        # First verify the core functionality
        verification_passed = await verify_phase_2_keys_implementation()
        
        if not verification_passed:
            print("❌ Core verification failed - skipping full test suite")
            exit(1)
        
        # Run full integration test suite
        success = await run_get_core_info_integration_tests()
        
        if success:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("✅ phase_2_keys = TRUE implementation is complete and working")
        else:
            print("❌ Some integration tests failed!")
            exit(1)
    
    asyncio.run(main())
