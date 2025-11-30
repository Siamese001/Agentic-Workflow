"""
Contract-level tests for Safety Planner (L1)
Tests pure planning behavior for safety validation strategy
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import the actual planner when available
try:
    from agentic_core.l1_planning.planners.safety_planner import SafetyPlanner
except ImportError:
    SafetyPlanner = Mock


class TestSafetyPlannerContracts:
    """Test safety planner contracts at L1 boundary"""
    
    def test_safety_planner_initialization_contract(self):
        """Test planner initializes with required configuration"""
        if SafetyPlanner is Mock:
            pytest.skip("SafetyPlanner not implemented")
        
        config = {"strict_mode": True, "policy_level": "high"}
        planner = SafetyPlanner(config)
        
        assert hasattr(planner, 'plan')
        assert hasattr(planner, 'validate_input')
        assert hasattr(planner, 'get_schema')
    
    def test_safety_planner_input_validation_contract(self):
        """Test planner validates input according to schema"""
        if SafetyPlanner is Mock:
            pytest.skip("SafetyPlanner not implemented")
        
        planner = SafetyPlanner({})
        
        # Valid input should pass
        valid_input = {
            "content": "resume optimization plan",
            "context": {"user_data": "personal_info"},
            "risk_level": "medium"
        }
        assert planner.validate_input(valid_input) is True
        
        # Invalid input should fail
        invalid_input = {"invalid": "data"}
        assert planner.validate_input(invalid_input) is False
    
    def test_safety_planner_output_schema_contract(self):
        """Test planner output matches expected schema"""
        if SafetyPlanner is Mock:
            pytest.skip("SafetyPlanner not implemented")
        
        planner = SafetyPlanner({})
        input_data = {
            "content": "resume optimization plan",
            "context": {"user_data": "personal_info"},
            "risk_level": "medium"
        }
        
        result = planner.plan(input_data)
        
        # Contract: output must have safety structure
        assert "safety_plan" in result
        assert "validations" in result
        assert "risk_assessment" in result
        assert isinstance(result["validations"], list)
    
    def test_safety_planner_purity_contract(self):
        """Test planner is pure - same input produces same output"""
        if SafetyPlanner is Mock:
            pytest.skip("SafetyPlanner not implemented")
        
        planner = SafetyPlanner({})
        input_data = {
            "content": "resume optimization plan",
            "context": {"user_data": "personal_info"},
            "risk_level": "medium"
        }
        
        result1 = planner.plan(input_data)
        result2 = planner.plan(input_data)
        
        assert result1 == result2
    
    def test_safety_planner_invalid_input_negative_case(self):
        """Test negative case: invalid input raises appropriate error"""
        if SafetyPlanner is Mock:
            pytest.skip("SafetyPlanner not implemented")
        
        planner = SafetyPlanner({})
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan(None)
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan({})
