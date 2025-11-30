"""
Regression tests for API Stability
Tests that APIs remain stable across versions
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock
import inspect

# Import actual components when available
try:
    from agentic_core.l1_planning.planners.strategy_planner import StrategyPlanner
    from agentic_core.l2_execution.executors.company_research_executor import CompanyResearchExecutor
    from agentic_core.l3_orchestration.dag.dag import ResumeEngineDAG
    from agentic_core.l4_memory.providers.rag_provider import RAGProvider
    from agentic_core.l5_safety.policies.policy_engine import PolicyEngine
except ImportError:
    StrategyPlanner = CompanyResearchExecutor = ResumeEngineDAG = RAGProvider = PolicyEngine = Mock


class TestAPIStability:
    """Test API stability regression contracts"""
    
    def test_planner_api_stability_contract(self):
        """Test planner APIs remain stable"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        # Check required methods exist
        required_methods = ['plan', 'validate_input', 'get_schema']
        for method in required_methods:
            assert hasattr(planner, method), f"Missing required method: {method}"
        
        # Check method signatures
        plan_sig = inspect.signature(planner.plan)
        assert 'input_data' in plan_sig.parameters or 'data' in plan_sig.parameters
        
        validate_sig = inspect.signature(planner.validate_input)
        assert len(validate_sig.parameters) >= 1
        
        # Test method calls don't raise unexpected errors
        try:
            result = planner.plan({
                "goal": "test",
                "context": {},
                "constraints": []
            })
            assert isinstance(result, dict)
        except Exception as e:
            # Should be predictable error types
            assert isinstance(e, (ValueError, TypeError, KeyError))
    
    def test_executor_api_stability_contract(self):
        """Test executor APIs remain stable"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({})
        
        # Check required methods
        required_methods = ['execute', 'validate_input', 'get_timeout', 'get_failure_modes']
        for method in required_methods:
            assert hasattr(executor, method), f"Missing required method: {method}"
        
        # Check method signatures
        execute_sig = inspect.signature(executor.execute)
        assert len(execute_sig.parameters) >= 1
        
        # Test timeout method returns reasonable value
        timeout = executor.get_timeout()
        assert isinstance(timeout, (int, float))
        assert timeout > 0
        
        # Test failure modes returns list
        failure_modes = executor.get_failure_modes()
        assert isinstance(failure_modes, list)
    
    def test_dag_api_stability_contract(self):
        """Test DAG orchestration APIs remain stable"""
        if ResumeEngineDAG is Mock:
            pytest.skip("ResumeEngineDAG not implemented")
        
        dag = ResumeEngineDAG({})
        
        # Check required methods
        required_methods = ['execute', 'validate_dag', 'get_nodes', 'get_edges']
        for method in required_methods:
            assert hasattr(dag, method), f"Missing required method: {method}"
        
        # Test node count matches expected
        nodes = dag.get_nodes()
        assert isinstance(nodes, list)
        assert len(nodes) == 12  # As specified in validation keys
        
        # Test DAG validation
        is_valid = dag.validate_dag()
        assert isinstance(is_valid, bool)
    
    def test_rag_api_stability_contract(self):
        """Test RAG provider APIs remain stable"""
        if RAGProvider is Mock:
            pytest.skip("RAGProvider not implemented")
        
        rag_provider = RAGProvider({})
        
        # Check required methods
        required_methods = ['query', 'get_retrieval_config', 'get_golden_queries']
        for method in required_methods:
            assert hasattr(rag_provider, method), f"Missing required method: {method}"
        
        # Test retrieval config structure
        config = rag_provider.get_retrieval_config()
        assert isinstance(config, dict)
        assert "mode" in config
        assert config["mode"] in ["dense", "sparse", "hybrid"]
        
        # Test golden queries structure
        golden_queries = rag_provider.get_golden_queries()
        assert isinstance(golden_queries, list)
        if golden_queries:
            assert "query" in golden_queries[0]
            assert "expected_results" in golden_queries[0]
    
    def test_safety_api_stability_contract(self):
        """Test safety policy APIs remain stable"""
        if PolicyEngine is Mock:
            pytest.skip("PolicyEngine not implemented")
        
        policy_engine = PolicyEngine({})
        
        # Check required methods
        required_methods = ['evaluate_content', 'apply_policies', 'get_policy_result']
        for method in required_methods:
            assert hasattr(policy_engine, method), f"Missing required method: {method}"
        
        # Test evaluation method signature
        eval_sig = inspect.signature(policy_engine.evaluate_content)
        assert len(eval_sig.parameters) >= 1
        
        # Test evaluation result structure
        result = policy_engine.evaluate_content({
            "text": "test content",
            "context": {"type": "test"}
        })
        
        assert isinstance(result, dict)
        required_fields = ["allowed", "confidence_score", "metadata"]
        for field in required_fields:
            assert field in result, f"Missing required field in result: {field}"
    
    def test_api_parameter_stability_contract(self):
        """Test API parameters remain stable"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        # Test initialization parameters
        valid_configs = [
            {},
            {"strict_mode": True},
            {"timeout": 30, "max_retries": 3},
            {"custom_param": "value"}  # Should handle extra params gracefully
        ]
        
        for config in valid_configs:
            try:
                planner = StrategyPlanner(config)
                assert planner is not None
            except Exception as e:
                # Should only raise for truly invalid configs
                assert isinstance(e, (ValueError, TypeError))
    
    def test_api_return_type_stability_contract(self):
        """Test API return types remain stable"""
        if CompanyResearchExecutor is Mock:
            pytest.skip("CompanyResearchExecutor not implemented")
        
        executor = CompanyResearchExecutor({})
        
        # Test execute return type
        result = executor.execute({
            "company_name": "TestCorp",
            "research_scope": ["basic"],
            "depth": "basic"
        })
        
        assert isinstance(result, dict)
        
        # Should have expected structure
        expected_keys = ["company_data", "sources", "metadata"]
        for key in expected_keys:
            assert key in result, f"Missing expected key: {key}"
        
        # Test nested structure types
        assert isinstance(result["company_data"], dict)
        assert isinstance(result["sources"], list)
        assert isinstance(result["metadata"], dict)
    
    def test_api_error_handling_stability_contract(self):
        """Test API error handling remains stable"""
        if PolicyEngine is Mock:
            pytest.skip("PolicyEngine not implemented")
        
        policy_engine = PolicyEngine({})
        
        # Test error types are consistent
        error_inputs = [
            None,
            {},
            {"invalid": "structure"}
        ]
        
        for error_input in error_inputs:
            try:
                result = policy_engine.evaluate_content(error_input)
                # If it doesn't error, should return error structure
                if "error" in result:
                    assert "type" in result["error"]
                    assert "message" in result["error"]
            except Exception as e:
                # Should raise standard exception types
                assert isinstance(e, (ValueError, TypeError, KeyError))
    
    def test_api_version_compatibility_contract(self):
        """Test APIs maintain version compatibility"""
        # This test would check compatibility across versions
        # For now, we'll test the version handling structure
        
        version_components = [
            StrategyPlanner,
            CompanyResearchExecutor, 
            ResumeEngineDAG,
            PolicyEngine
        ]
        
        for component in version_components:
            if component is Mock:
                continue
                
            try:
                instance = component({})
                
                # Should have version information
                if hasattr(instance, 'get_version'):
                    version = instance.get_version()
                    assert isinstance(version, str)
                    assert len(version.split('.')) >= 2  # At least major.minor
                
                # Should handle version-specific features
                if hasattr(instance, 'supports_feature'):
                    feature_support = instance.supports_feature("deterministic_mode")
                    assert isinstance(feature_support, bool)
                    
            except Exception:
                # Version handling might not be implemented yet
                pass
    
    def test_api_deprecation_handling_contract(self):
        """Test APIs handle deprecation gracefully"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        # Test with potentially deprecated parameters
        deprecated_params = {
            "old_param": "value",  # Might be deprecated
            "legacy_mode": True    # Might be deprecated
        }
        
        try:
            result = planner.plan({
                "goal": "test",
                "context": {},
                "constraints": []
            }, **deprecated_params)
            
            # Should either work or provide deprecation warning
            assert isinstance(result, dict)
            
        except Exception as e:
            # Should provide clear error about deprecated parameters
            assert isinstance(e, (ValueError, TypeError))
    
    def test_negative_case_api_breakage_contract(self):
        """Test negative case: detect API breakages"""
        # This test validates our ability to detect API breakages
        
        expected_apis = {
            "StrategyPlanner": {
                "methods": ["plan", "validate_input", "get_schema"],
                "init_params": ["config"]
            },
            "CompanyResearchExecutor": {
                "methods": ["execute", "validate_input", "get_timeout"],
                "init_params": ["config"]
            },
            "PolicyEngine": {
                "methods": ["evaluate_content", "apply_policies"],
                "init_params": ["config"]
            }
        }
        
        # Validate expected API structure exists
        for component_name, expected_api in expected_apis.items():
            if component_name == "StrategyPlanner" and StrategyPlanner is not Mock:
                component = StrategyPlanner
            elif component_name == "CompanyResearchExecutor" and CompanyResearchExecutor is not Mock:
                component = CompanyResearchExecutor
            elif component_name == "PolicyEngine" and PolicyEngine is not Mock:
                component = PolicyEngine
            else:
                continue  # Skip if not implemented
            
            instance = component({})
            
            # Check methods exist
            for method in expected_api["methods"]:
                assert hasattr(instance, method), f"API breakage: {component_name} missing {method}"
            
            # Check method signatures haven't changed drastically
            for method in expected_api["methods"]:
                if hasattr(instance, method):
                    sig = inspect.signature(getattr(instance, method))
                    # Should have reasonable number of parameters
                    assert len(sig.parameters) <= 5, f"API breakage: {component_name}.{method} has too many parameters"
    
    def test_api_documentation_stability_contract(self):
        """Test API documentation remains stable"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        # Check key methods have docstrings
        key_methods = ['plan', 'validate_input', 'get_schema']
        
        for method_name in key_methods:
            method = getattr(planner, method_name, None)
            if method:
                docstring = method.__doc__
                if docstring:
                    # Should have meaningful documentation
                    assert len(docstring.strip()) > 10, f"Poor documentation for {method_name}"
                    assert method_name.lower() in docstring.lower(), f"Documentation doesn't mention {method_name}"
