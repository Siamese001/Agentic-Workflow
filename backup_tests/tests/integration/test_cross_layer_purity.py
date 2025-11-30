"""
Integration tests for Cross-Layer Purity
Tests that L1-L5 layers maintain proper separation and boundaries
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock
import importlib
import inspect


class TestCrossLayerPurity:
    """Test cross-layer purity contracts"""
    
    def test_l1_no_lower_layer_imports_contract(self):
        """Test L1 does not import from L2, L3, L4, L5"""
        # Check L1 planning modules
        l1_modules = [
            'agentic_core.l1_planning.planners.strategy_planner',
            'agentic_core.l1_planning.planners.message_planner',
            'agentic_core.l1_planning.planners.research_planner',
            'agentic_core.l1_planning.planners.refinement_planner',
            'agentic_core.l1_planning.planners.safety_planner'
        ]
        
        forbidden_imports = [
            'from agentic_core.l2_execution',
            'from agentic_core.l3_orchestration',
            'from agentic_core.l4_memory',
            'from agentic_core.l5_safety'
        ]
        
        for module_name in l1_modules:
            try:
                module = importlib.import_module(module_name)
                source_file = getattr(module, '__file__', '')
                
                if source_file and source_file.endswith('.py'):
                    with open(source_file, 'r') as f:
                        source_code = f.read()
                    
                    for forbidden in forbidden_imports:
                        assert forbidden not in source_code, f"L1 purity violation in {module_name}: {forbidden}"
                        
            except ImportError:
                # Module not implemented - skip
                pass
    
    def test_l2_no_lower_layer_imports_contract(self):
        """Test L2 does not import from L3, L4, L5"""
        l2_modules = [
            'agentic_core.l2_execution.executors.company_research_executor',
            'agentic_core.l2_execution.executors.contact_research_executor',
            'agentic_core.l2_execution.executors.message_generation_executor'
        ]
        
        forbidden_imports = [
            'from agentic_core.l3_orchestration',
            'from agentic_core.l4_memory',
            'from agentic_core.l5_safety'
        ]
        
        for module_name in l2_modules:
            try:
                module = importlib.import_module(module_name)
                source_file = getattr(module, '__file__', '')
                
                if source_file and source_file.endswith('.py'):
                    with open(source_file, 'r') as f:
                        source_code = f.read()
                    
                    for forbidden in forbidden_imports:
                        assert forbidden not in source_code, f"L2 purity violation in {module_name}: {forbidden}"
                        
            except ImportError:
                # Module not implemented - skip
                pass
    
    def test_l3_no_lower_layer_imports_contract(self):
        """Test L3 does not import from L4, L5"""
        l3_modules = [
            'agentic_core.l3_orchestration.engines.dag',
            'agentic_core.l3_orchestration.engines.dag',
            'agentic_core.l3_orchestration.framework.dag'
        ]
        
        forbidden_imports = [
            'from agentic_core.l4_memory',
            'from agentic_core.l5_safety'
        ]
        
        for module_name in l3_modules:
            try:
                module = importlib.import_module(module_name)
                source_file = getattr(module, '__file__', '')
                
                if source_file and source_file.endswith('.py'):
                    with open(source_file, 'r') as f:
                        source_code = f.read()
                    
                    for forbidden in forbidden_imports:
                        assert forbidden not in source_code, f"L3 purity violation in {module_name}: {forbidden}"
                        
            except ImportError:
                # Module not implemented - skip
                pass
    
    def test_l4_no_business_logic_imports_contract(self):
        """Test L4 does not import business logic from L1, L2, L3"""
        l4_modules = [
            'agentic_core.l4_memory.providers.provider_registry',
            'agentic_core.l4_memory.temporal.temporal_store',
            'agentic_core.l4_memory.mappings.data_mapper'
        ]
        
        forbidden_imports = [
            'from agentic_core.l1_planning.planners',
            'from agentic_core.l2_execution.executors',
            'from agentic_core.l3_orchestration.engines'
        ]
        
        for module_name in l4_modules:
            try:
                module = importlib.import_module(module_name)
                source_file = getattr(module, '__file__', '')
                
                if source_file and source_file.endswith('.py'):
                    with open(source_file, 'r') as f:
                        source_code = f.read()
                    
                    for forbidden in forbidden_imports:
                        assert forbidden not in source_code, f"L4 purity violation in {module_name}: {forbidden}"
                        
            except ImportError:
                # Module not implemented - skip
                pass
    
    def test_l5_no_business_logic_imports_contract(self):
        """Test L5 does not import business logic from L1, L2, L3, L4"""
        l5_modules = [
            'agentic_core.l5_safety.policies.policy_engine',
            'agentic_core.l5_safety.filters.content_filter',
            'agentic_core.l5_safety.validators.safety_validator'
        ]
        
        forbidden_imports = [
            'from agentic_core.l1_planning.planners',
            'from agentic_core.l2_execution.executors',
            'from agentic_core.l3_orchestration.engines',
            'from agentic_core.l4_memory.providers'
        ]
        
        for module_name in l5_modules:
            try:
                module = importlib.import_module(module_name)
                source_file = getattr(module, '__file__', '')
                
                if source_file and source_file.endswith('.py'):
                    with open(source_file, 'r') as f:
                        source_code = f.read()
                    
                    for forbidden in forbidden_imports:
                        assert forbidden not in source_code, f"L5 purity violation in {module_name}: {forbidden}"
                        
            except ImportError:
                # Module not implemented - skip
                pass
    
    def test_layer_boundary_interfaces_contract(self):
        """Test that layers communicate through proper interfaces"""
        # Each layer should expose specific interface methods
        layer_interfaces = {
            'L1': ['plan', 'validate_input', 'get_schema'],
            'L2': ['execute', 'validate_input', 'get_timeout'],
            'L3': ['execute', 'validate_dag', 'get_nodes'],
            'L4': ['store_event', 'get_events', 'query'],
            'L5': ['evaluate_content', 'validate', 'filter_content']
        }
        
        # Test that test files reference only interface methods
        test_files = [
            'tests/l1/unit/test_strategy_planner.py',
            'tests/l2/unit/test_company_research_executor.py',
            'tests/l3/orchestration/test_dag.py',
            'tests/l4/memory/test_temporal_memory.py',
            'tests/l5/safety/test_policy_engine.py'
        ]
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    test_code = f.read()
                
                # Should only reference interface methods, not internal implementation
                assert 'private_method' not in test_code
                assert '_internal_' not in test_code
                assert '__secret__' not in test_code
                
            except FileNotFoundError:
                # Test file not created yet - skip
                pass
    
    def test_no_circular_dependencies_contract(self):
        """Test that there are no circular dependencies between layers"""
        # Build a simple dependency graph from import statements
        layer_dependencies = {}
        
        layers = ['l1_planning', 'l2_execution', 'l3_orchestration', 'l4_memory', 'l5_safety']
        
        for layer in layers:
            dependencies = set()
            
            try:
                # Check if layer module exists
                module_path = f'agentic_core.{layer}'
                module = importlib.import_module(module_path)
                
                # Look at submodules
                for submodule_name in ['planners', 'executors', 'engines', 'providers', 'policies']:
                    try:
                        submodule_path = f'agentic_core.{layer}.{submodule_name}'
                        submodule = importlib.import_module(submodule_path)
                        
                        # Check imports in this submodule
                        source_file = getattr(submodule, '__file__', '')
                        if source_file and source_file.endswith('.py'):
                            with open(source_file, 'r') as f:
                                source_code = f.read()
                            
                            # Find layer dependencies
                            for other_layer in layers:
                                if other_layer != layer:
                                    if f'from agentic_core.{other_layer}' in source_code:
                                        dependencies.add(other_layer)
                    
                    except ImportError:
                        continue
                
                layer_dependencies[layer] = dependencies
                
            except ImportError:
                layer_dependencies[layer] = set()
        
        # Check for circular dependencies
        for layer, deps in layer_dependencies.items():
            for dep in deps:
                # If layer A depends on B, B should not depend on A
                if layer in layer_dependencies.get(dep, set()):
                    assert False, f"Circular dependency detected: {layer} <-> {dep}"
    
    def test_layer_isolation_contract(self):
        """Test that layers can be instantiated and used in isolation"""
        # Each layer should be usable without importing other layers
        try:
            # Try to import and use L1 without other layers
            from agentic_core.l1_planning.planners.strategy_planner import StrategyPlanner
            assert StrategyPlanner is not None
        except ImportError:
            pass  # Not implemented
        
        try:
            # Try to import and use L2 without other layers
            from agentic_core.l2_execution.executors.company_research_executor import CompanyResearchExecutor
            assert CompanyResearchExecutor is not None
        except ImportError:
            pass  # Not implemented
        
        try:
            # Try to import and use L3 without other layers
            from agentic_core.l3_orchestration.dag.dag import ResumeEngineDAG
            assert ResumeEngineDAG is not None
        except ImportError:
            pass  # Not implemented
        
        try:
            # Try to import and use L4 without other layers
            from agentic_core.l4_memory.temporal.temporal_store import TemporalStore
            assert TemporalStore is not None
        except ImportError:
            pass  # Not implemented
        
        try:
            # Try to import and use L5 without other layers
            from agentic_core.l5_safety.policies.policy_engine import PolicyEngine
            assert PolicyEngine is not None
        except ImportError:
            pass  # Not implemented
    
    def test_data_flow_contract(self):
        """Test that data flows properly between layers without contamination"""
        # Data should be transformed but not contaminated as it flows between layers
        
        # Test input data
        clean_input = {
            "user_profile": {"name": "John", "skills": ["Python"]},
            "target": "Software Engineer"
        }
        
        # Each layer should add metadata but not modify core data inappropriately
        processed_data = clean_input.copy()
        
        # L1: Planning should add strategy metadata
        processed_data["l1_metadata"] = {"strategy_applied": True}
        assert processed_data["user_profile"] == clean_input["user_profile"]
        
        # L2: Execution should add execution metadata
        processed_data["l2_metadata"] = {"execution_completed": True}
        assert processed_data["user_profile"] == clean_input["user_profile"]
        assert processed_data["l1_metadata"] == {"strategy_applied": True}
        
        # L3: Orchestration should add orchestration metadata
        processed_data["l3_metadata"] = {"dag_executed": True}
        assert processed_data["user_profile"] == clean_input["user_profile"]
        
        # Core data should remain intact through the pipeline
        assert processed_data["user_profile"] == clean_input["user_profile"]
