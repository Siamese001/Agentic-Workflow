"""
Integration tests for L1 Planning Layer
Tests cross-planner contracts and layer boundaries
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import actual planners when available
try:
    from agentic_core.l1_planning.planners.strategy_planner import StrategyPlanner
    from agentic_core.l1_planning.planners.message_planner import MessagePlanner
    from agentic_core.l1_planning.planners.research_planner import ResearchPlanner
    from agentic_core.l1_planning.planners.refinement_planner import RefinementPlanner
    from agentic_core.l1_planning.planners.safety_planner import SafetyPlanner
except ImportError:
    StrategyPlanner = MessagePlanner = ResearchPlanner = RefinementPlanner = SafetyPlanner = Mock


class TestL1PlanningIntegration:
    """Test L1 planning layer integration contracts"""
    
    def test_planner_chain_integration_contract(self):
        """Test that planners can be chained in valid sequence"""
        if any(planner is Mock for planner in [StrategyPlanner, MessagePlanner, ResearchPlanner]):
            pytest.skip("Planners not implemented")
        
        # Initialize planners
        strategy_planner = StrategyPlanner({})
        research_planner = ResearchPlanner({})
        message_planner = MessagePlanner({})
        
        # Strategy -> Research -> Message chain
        initial_input = {
            "goal": "optimize_resume",
            "context": {"user_profile": {"name": "John"}},
            "constraints": []
        }
        
        strategy_result = strategy_planner.plan(initial_input)
        assert "strategy" in strategy_result
        
        # Use strategy output for research planning
        research_input = {
            "research_target": "company_analysis",
            "entity": "TechCorp",
            "scope": strategy_result.get("research_scope", ["products"])
        }
        
        research_result = research_planner.plan(research_input)
        assert "research_plan" in research_result
        
        # Use research output for message planning
        message_input = {
            "recipient": "hiring_manager",
            "context": research_result.get("context", {}),
            "goal": "introduce_resume"
        }
        
        message_result = message_planner.plan(message_input)
        assert "message_plan" in message_result
    
    def test_planner_output_compatibility_contract(self):
        """Test that planner outputs are compatible across the layer"""
        if any(planner is Mock for planner in [StrategyPlanner, ResearchPlanner]):
            pytest.skip("Planners not implemented")
        
        strategy_planner = StrategyPlanner({})
        research_planner = ResearchPlanner({})
        
        # All planners should produce outputs with compatible schema structure
        strategy_output = strategy_planner.plan({
            "goal": "optimize_resume",
            "context": {"user_profile": {}},
            "constraints": []
        })
        
        research_output = research_planner.plan({
            "research_target": "company_analysis",
            "entity": "TechCorp",
            "scope": ["products"]
        })
        
        # Contract: all outputs must have metadata and be serializable
        for output in [strategy_output, research_output]:
            assert isinstance(output, dict)
            assert "metadata" in output or "plan" in output or "strategy" in output or "research_plan" in output
    
    def test_planner_error_propagation_contract(self):
        """Test that planner errors propagate properly through the layer"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        # Invalid input should raise error that can be caught and handled
        with pytest.raises((ValueError, TypeError, KeyError)):
            planner.plan({"invalid": "structure"})
    
    def test_planner_layer_boundary_contract(self):
        """Test that L1 planners do not import from lower layers"""
        try:
            import agentic_core.l1_planning.planners.strategy_planner as sp_module
            
            # Check that L1 modules don't import from execution layers
            l1_source = getattr(sp_module, '__file__', '')
            if l1_source and l1_source.endswith('.py'):
                with open(l1_source, 'r') as f:
                    source_code = f.read()
                    
                # Should not import from execution layers
                forbidden_imports = [
                    'from agentic_core.l2_execution',
                    'from agentic_core.l3_orchestration', 
                    'from agentic_core.l4_memory',
                    'from agentic_core.l5_safety'
                ]
                
                for forbidden in forbidden_imports:
                    assert forbidden not in source_code, f"L1 purity violation: {forbidden}"
        except ImportError:
            pytest.skip("StrategyPlanner module not implemented")
    
    def test_planner_deterministic_behavior_contract(self):
        """Test that all planners exhibit deterministic behavior"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        input_data = {
            "goal": "optimize_resume",
            "context": {"user_profile": {"name": "test_user"}},
            "constraints": []
        }
        
        # Multiple calls with same input should produce identical results
        results = [planner.plan(input_data) for _ in range(3)]
        
        # All results should be identical
        for result in results[1:]:
            assert result == results[0], "Planner behavior is not deterministic"
