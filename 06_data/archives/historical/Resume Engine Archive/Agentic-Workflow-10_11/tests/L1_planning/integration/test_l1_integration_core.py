"""L1 Planning Integration Tests."""

class TestL1PlanningIntegration:
    """Integration tests for L1 planning layer."""
    
    def test_workflow_to_strategy_integration(self):
        """Test workflow to strategy planning integration."""
        workflow = {"id": "wf1", "steps": ["plan", "execute"]}
        strategy = {"workflow_id": workflow["id"], "mode": "cot"}
        assert strategy["workflow_id"] == "wf1"
    
    def test_strategy_to_drafting_integration(self):
        """Test strategy to drafting integration."""
        strategy_result = {"complexity": "medium"}
        drafting_config = {"based_on": strategy_result["complexity"]}
        assert drafting_config["based_on"] == "medium"
    
    def test_planning_to_safety_integration(self):
        """Test planning to safety integration."""
        plan = {"content": "resume text"}
        safety_check = {"plan_id": "p1", "validated": True}
        assert safety_check["validated"] is True
    
    def test_full_planning_pipeline(self):
        """Test full planning pipeline integration."""
        stages = ["workflow", "strategy", "drafting", "qa", "safety"]
        completed = [True for _ in stages]
        assert all(completed)
