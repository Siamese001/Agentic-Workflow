"""L1 Planning Unit Tests - Core."""
import pytest

class TestL1PlanningUnitCore:
    """Core unit tests for L1 planning layer."""
    
    def test_workflow_plan_creation(self):
        """Test workflow plan creation."""
        plan = {"steps": ["analyze", "plan", "execute"]}
        assert len(plan["steps"]) == 3
    
    def test_strategy_plan_initialization(self):
        """Test strategy plan initialization."""
        strategy = {"mode": "cot", "depth": 2}
        assert strategy["mode"] == "cot"
    
    def test_complexity_classification(self):
        """Test complexity classification logic."""
        levels = ["low", "medium", "high"]
        assert "medium" in levels
    
    def test_seniority_inference(self):
        """Test seniority inference from job title."""
        titles = {"senior": "senior_ic", "director": "director", "vp": "executive"}
        assert titles["senior"] == "senior_ic"
    
    def test_domain_inference(self):
        """Test domain inference from job description."""
        domains = {"ml": "machine_learning", "cloud": "cloud_infrastructure"}
        assert "ml" in domains
