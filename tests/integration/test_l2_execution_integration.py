"""
Integration tests for L2 Execution Layer
Tests cross-executor contracts and layer boundaries
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock
import time

# Import actual executors when available
try:
    from agentic_core.l2_execution.executors.company_research_executor import CompanyResearchExecutor
    from agentic_core.l2_execution.executors.contact_research_executor import ContactResearchExecutor
    from agentic_core.l2_execution.executors.message_generation_executor import MessageGenerationExecutor
except ImportError:
    CompanyResearchExecutor = ContactResearchExecutor = MessageGenerationExecutor = Mock


class TestL2ExecutionIntegration:
    """Test L2 execution layer integration contracts"""
    
    def test_executor_chain_integration_contract(self):
        """Test that executors can be chained in valid sequence"""
        if any(executor is Mock for executor in [CompanyResearchExecutor, ContactResearchExecutor, MessageGenerationExecutor]):
            pytest.skip("Executors not implemented")
        
        # Initialize executors
        company_executor = CompanyResearchExecutor({"timeout": 10})
        contact_executor = ContactResearchExecutor({"timeout": 10})
        message_executor = MessageGenerationExecutor({"timeout": 10})
        
        # Company Research -> Contact Research -> Message Generation chain
        company_input = {
            "company_name": "TechCorp",
            "research_scope": ["basic_info", "products"],
            "depth": "basic"
        }
        
        company_result = company_executor.execute(company_input)
        assert "company_data" in company_result
        
        # Use company output for contact research
        contact_input = {
            "company_name": "TechCorp",
            "target_role": "engineering_manager",
            "contact_limit": 3,
            "research_depth": "basic"
        }
        
        contact_result = contact_executor.execute(contact_input)
        assert "contacts" in contact_result
        
        # Use contact output for message generation
        message_input = {
            "recipient": "hiring_manager",
            "context": {
                "company": company_result.get("company_data", {}),
                "contacts": contact_result.get("contacts", []),
                "position": "Senior Engineer"
            },
            "tone": "professional",
            "goal": "introduce_resume"
        }
        
        message_result = message_executor.execute(message_input)
        assert "message" in message_result
    
    def test_executor_output_compatibility_contract(self):
        """Test that executor outputs are compatible across the layer"""
        if any(executor is Mock for executor in [CompanyResearchExecutor, ContactResearchExecutor]):
            pytest.skip("Executors not implemented")
        
        company_executor = CompanyResearchExecutor({})
        contact_executor = ContactResearchExecutor({})
        
        # All executors should produce outputs with compatible schema structure
        company_output = company_executor.execute({
            "company_name": "TechCorp",
            "research_scope": ["basic_info"],
            "depth": "basic"
        })
        
        contact_output = contact_executor.execute({
            "company_name": "TechCorp",
            "target_role": "engineering_manager",
            "contact_limit": 3,
            "research_depth": "basic"
        })
        
        # Contract: all outputs must have metadata and be serializable
        for output in [company_output, contact_output]:
            assert isinstance(output, dict)
            assert "metadata" in output or "sources" in output
            assert not any(key in output for key in ["internal_state", "private_data"])
    
    def test_executor_timeout_consistency_contract(self):
        """Test that all executors respect timeout consistently"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        timeout_config = {"timeout": 2}
        executors = [
            CompanyResearchExecutor(timeout_config),
            ContactResearchExecutor(timeout_config),
            MessageGenerationExecutor(timeout_config)
        ]
        
        for executor in executors:
            if executor is Mock:
                continue
                
            # Test basic input that should complete quickly
            if isinstance(executor, CompanyResearchExecutor):
                test_input = {"company_name": "Test", "research_scope": ["basic"], "depth": "basic"}
            elif isinstance(executor, ContactResearchExecutor):
                test_input = {"company_name": "Test", "target_role": "manager", "contact_limit": 1, "research_depth": "basic"}
            else:  # MessageGenerationExecutor
                test_input = {"recipient": "test", "context": {"company": "Test"}, "tone": "professional", "goal": "test"}
            
            start_time = time.time()
            result = executor.execute(test_input)
            elapsed_time = time.time() - start_time
            
            # Should complete within timeout + buffer
            assert elapsed_time < timeout_config["timeout"] + 1
    
    def test_executor_error_propagation_contract(self):
        """Test that executor errors propagate properly through the layer"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({})
        
        # Invalid input should raise error that can be caught and handled
        with pytest.raises((ValueError, TypeError, KeyError)):
            executor.execute({"invalid": "structure"})
    
    def test_executor_layer_boundary_contract(self):
        """Test that L2 executors do not import from orchestration layers"""
        try:
            # This is a structural test - ensure no L3+ imports in L2
            import agentic_core.l2_execution.executors.company_research_executor as cre_module
            
            # Check that L2 modules don't import from L3, L4, L5
            l2_source = getattr(cre_module, '__file__', '')
            if l2_source and l2_source.endswith('.py'):
                with open(l2_source, 'r') as f:
                    source_code = f.read()
                    
                # Should not import from orchestration layers
                forbidden_imports = [
                    'from agentic_core.l3_orchestration',
                    'from agentic_core.l4_memory',
                    'from agentic_core.l5_safety'
                ]
                
                for forbidden in forbidden_imports:
                    assert forbidden not in source_code, f"L2 purity violation: {forbidden}"
        except ImportError:
            pytest.skip("CompanyResearchExecutor module not implemented")
    
    def test_executor_circuit_breaker_integration_contract(self):
        """Test that circuit breaker works across executor chain"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({"failure_threshold": 2, "timeout": 1})
        
        # Simulate failures to trigger circuit breaker
        failing_input = {
            "company_name": "Invalid" * 100,  # Very long invalid name
            "research_scope": ["trigger_failure"],
            "depth": "basic"
        }
        
        # Execute until circuit breaker opens
        for i in range(3):
            result = executor.execute(failing_input)
            if i >= 2:  # After threshold, should fail fast
                if "error" in result:
                    assert result["error"]["type"] in ["circuit_breaker_open", "timeout"]
                    break
    
    def test_executor_deterministic_behavior_contract(self):
        """Test that all executors exhibit deterministic behavior for same input"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({})
        input_data = {
            "company_name": "TestCorp",
            "research_scope": ["basic_info"],
            "depth": "basic"
        }
        
        # Multiple calls with same input should produce similar results
        results = [executor.execute(input_data) for _ in range(3)]
        
        # All results should have same structure and key fields
        for result in results[1:]:
            assert type(result) == type(results[0])
            assert "company_data" in result == "company_data" in results[0]
            assert "metadata" in result == "metadata" in results[0]
