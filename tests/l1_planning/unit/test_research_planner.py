"""
Contract-level tests for Research Planner (L1)
Tests pure planning behavior for research strategy
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock

# Import the actual planner when available
try:
    from agentic_core.l1_planning.planners.research_planner import ResearchPlanner
except ImportError:
    ResearchPlanner = Mock


class TestResearchPlannerContracts:
    """Test research planner contracts at L1 boundary"""
    
    def test_research_planner_initialization_contract(self):
        """Test planner initializes with required configuration"""
        if ResearchPlanner is Mock:
            pytest.skip("ResearchPlanner not implemented")
        
        config = {"max_sources": 10, "depth": 3}
        planner = ResearchPlanner(config)
        
        assert hasattr(planner, 'plan')
        assert hasattr(planner, 'validate_input')
        assert hasattr(planner, 'get_schema')
    
    def test_research_planner_input_validation_contract(self):
        """Test planner validates input according to schema"""
        if ResearchPlanner is Mock:
            pytest.skip("ResearchPlanner not implemented")
        
        planner = ResearchPlanner({})
        
        # Valid input should pass
        valid_input = {
            "research_target": "company_analysis",
            "entity": "TechCorp",
            "scope": ["funding", "products", "team"]
        }
        assert planner.validate_input(valid_input) is True
        
        # Invalid input should fail
        invalid_input = {"invalid": "data"}
        assert planner.validate_input(invalid_input) is False
    
    def test_research_planner_output_schema_contract(self):
        """Test planner output matches expected schema"""
        if ResearchPlanner is Mock:
            pytest.skip("ResearchPlanner not implemented")
        
        planner = ResearchPlanner({})
        input_data = {
            "research_target": "company_analysis",
            "entity": "TechCorp",
            "scope": ["funding", "products", "team"]
        }
        
        result = planner.plan(input_data)
        
        # Contract: output must have research structure
        assert "research_plan" in result
        assert "data_sources" in result
        assert "query_strategy" in result
        assert isinstance(result["data_sources"], list)
    
    def test_research_planner_purity_contract(self):
        """Test planner is pure - same input produces same output"""
        if ResearchPlanner is Mock:
            pytest.skip("ResearchPlanner not implemented")
        
        planner = ResearchPlanner({})
        input_data = {
            "research_target": "company_analysis",
            "entity": "TechCorp",
            "scope": ["funding", "products"]
        }
        
        result1 = planner.plan(input_data)
        result2 = planner.plan(input_data)
        
        assert result1 == result2
    
    def test_research_planner_invalid_input_negative_case(self):
        """Test negative case: invalid input raises appropriate error"""
        if ResearchPlanner is Mock:
            pytest.skip("ResearchPlanner not implemented")
        
        planner = ResearchPlanner({})
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan(None)
        
        with pytest.raises((ValueError, TypeError)):
            planner.plan({})
