"""
Contract-level tests for Message Planner (L1)
Tests pure planning behavior for message generation strategy
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import the actual planner when available
try:
    from agentic_core.l1_planning.planners.message_planner import MessagePlanner
except ImportError:
    MessagePlanner = Mock


class TestMessagePlannerContracts:
    """Test message planner contracts at L1 boundary"""
    
    def test_message_planner_initialization_contract(self):
        """Test planner initializes with required configuration"""
        if MessagePlanner is Mock:
            pytest.skip("MessagePlanner not implemented")
        
        config = {"max_length": 500, "tone": "professional"}
        planner = MessagePlanner(config)
        
        assert hasattr(planner, 'plan')
        assert hasattr(planner, 'validate_input')
        assert hasattr(planner, 'get_schema')
    
    def test_message_planner_input_validation_contract(self):
        """Test planner validates input according to schema"""
        if MessagePlanner is Mock:
            pytest.skip("MessagePlanner not implemented")
        
        planner = MessagePlanner({})
        
        # Valid input should pass
        valid_input = {
            "recipient": "hiring_manager",
            "context": {"company": "TechCorp", "position": "Engineer"},
            "goal": "introduce_resume"
        }
        assert planner.validate_input(valid_input) is True
        
        # Invalid input should fail
        invalid_input = {"invalid": "data"}
        assert planner.validate_input(invalid_input) is False
    
    def test_message_planner_output_schema_contract(self):
        """Test planner output matches expected schema"""
        if MessagePlanner is Mock:
            pytest.skip("MessagePlanner not implemented")
        
        planner = MessagePlanner({})
        input_data = {
            "recipient": "hiring_manager",
            "context": {"company": "TechCorp", "position": "Engineer"},
            "goal": "introduce_resume"
        }
        
        result = planner.plan(input_data)
        
        # Contract: output must have message structure
        assert "message_plan" in result
        assert "key_points" in result
        assert "tone" in result
        assert isinstance(result["key_points"], list)
    
    def test_message_planner_purity_contract(self):
        """Test planner is pure - same input produces same output"""
        if MessagePlanner is Mock:
            pytest.skip("MessagePlanner not implemented")
        
        planner = MessagePlanner({})
        input_data = {
            "recipient": "hiring_manager",
            "context": {"company": "TechCorp", "position": "Engineer"},
            "goal": "introduce_resume"
        }
        
        result1 = planner.plan(input_data)
        result2 = planner.plan(input_data)
        
        assert result1 == result2
    
    def test_message_planner_invalid_input_negative_case(self):
        """Test negative case: invalid input raises appropriate error"""
        if MessagePlanner is Mock:
            pytest.skip("MessagePlanner not implemented")
        
        planner = MessagePlanner({})
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan(None)
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan({})
