"""
Contract-level tests for Refinement Planner (L1)
Tests pure planning behavior for strategy refinement
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import the actual planner when available
try:
    from agentic_core.l1_planning.planners.refinement_planner import RefinementPlanner
except ImportError:
    RefinementPlanner = Mock


class TestRefinementPlannerContracts:
    """Test refinement planner contracts at L1 boundary"""
    
    def test_refinement_planner_initialization_contract(self):
        """Test planner initializes with required configuration"""
        if RefinementPlanner is Mock:
            pytest.skip("RefinementPlanner not implemented")
        
        config = {"max_iterations": 3, "improvement_threshold": 0.1}
        planner = RefinementPlanner(config)
        
        assert hasattr(planner, 'plan')
        assert hasattr(planner, 'validate_input')
        assert hasattr(planner, 'get_schema')
    
    def test_refinement_planner_input_validation_contract(self):
        """Test planner validates input according to schema"""
        if RefinementPlanner is Mock:
            pytest.skip("RefinementPlanner not implemented")
        
        planner = RefinementPlanner({})
        
        # Valid input should pass
        valid_input = {
            "current_strategy": {"steps": [], "confidence": 0.5},
            "feedback": {"issues": ["missing_research"], "suggestions": []},
            "context": {"goal": "optimize_resume"}
        }
        assert planner.validate_input(valid_input) is True
        
        # Invalid input should fail
        invalid_input = {"invalid": "data"}
        assert planner.validate_input(invalid_input) is False
    
    def test_refinement_planner_output_schema_contract(self):
        """Test planner output matches expected schema"""
        if RefinementPlanner is Mock:
            pytest.skip("RefinementPlanner not implemented")
        
        planner = RefinementPlanner({})
        input_data = {
            "current_strategy": {"steps": [], "confidence": 0.5},
            "feedback": {"issues": ["missing_research"], "suggestions": []},
            "context": {"goal": "optimize_resume"}
        }
        
        result = planner.plan(input_data)
        
        # Contract: output must have refinement structure
        assert "refined_strategy" in result
        assert "improvements" in result
        assert "confidence_score" in result
        assert isinstance(result["improvements"], list)
    
    def test_refinement_planner_purity_contract(self):
        """Test planner is pure - same input produces same output"""
        if RefinementPlanner is Mock:
            pytest.skip("RefinementPlanner not implemented")
        
        planner = RefinementPlanner({})
        input_data = {
            "current_strategy": {"steps": ["research"], "confidence": 0.5},
            "feedback": {"issues": [], "suggestions": ["add_validation"]},
            "context": {"goal": "optimize_resume"}
        }
        
        result1 = planner.plan(input_data)
        result2 = planner.plan(input_data)
        
        assert result1 == result2
    
    def test_refinement_planner_invalid_input_negative_case(self):
        """Test negative case: invalid input raises appropriate error"""
        if RefinementPlanner is Mock:
            pytest.skip("RefinementPlanner not implemented")
        
        planner = RefinementPlanner({})
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan(None)
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan({})
