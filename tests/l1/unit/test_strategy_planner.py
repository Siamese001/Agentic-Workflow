"""
Contract-level tests for Strategy Planner (L1)
Tests pure planning behavior without execution dependencies
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import the actual planner when available
try:
    from agentic_core.l1_planning.planners.strategy_planner import StrategyPlanner
except ImportError:
    StrategyPlanner = Mock


class TestStrategyPlannerContracts:
    """Test strategy planner contracts at L1 boundary"""
    
    def test_strategy_planner_initialization_contract(self):
        """Test planner initializes with required configuration"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        config = {"max_depth": 5, "timeout": 30}
        planner = StrategyPlanner(config)
        
        assert hasattr(planner, 'plan')
        assert hasattr(planner, 'validate_input')
        assert hasattr(planner, 'get_schema')
    
    def test_strategy_planner_input_validation_contract(self):
        """Test planner validates input according to schema"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        # Valid input should pass
        valid_input = {
            "goal": "optimize_resume",
            "context": {"user_profile": {}},
            "constraints": []
        }
        assert planner.validate_input(valid_input) is True
        
        # Invalid input should fail
        invalid_input = {"invalid": "data"}
        assert planner.validate_input(invalid_input) is False
    
    def test_strategy_planner_output_schema_contract(self):
        """Test planner output matches expected schema"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        input_data = {
            "goal": "optimize_resume",
            "context": {"user_profile": {}},
            "constraints": []
        }
        
        result = planner.plan(input_data)
        
        # Contract: output must have strategy field
        assert "strategy" in result
        assert "steps" in result
        assert isinstance(result["steps"], list)
    
    def test_strategy_planner_purity_contract(self):
        """Test planner is pure - same input produces same output"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        input_data = {
            "goal": "optimize_resume",
            "context": {"user_profile": {"name": "test"}},
            "constraints": []
        }
        
        result1 = planner.plan(input_data)
        result2 = planner.plan(input_data)
        
        assert result1 == result2
    
    def test_strategy_planner_invalid_input_negative_case(self):
        """Test negative case: invalid input raises appropriate error"""
        if StrategyPlanner is Mock:
            pytest.skip("StrategyPlanner not implemented")
        
        planner = StrategyPlanner({})
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan(None)
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan({})
