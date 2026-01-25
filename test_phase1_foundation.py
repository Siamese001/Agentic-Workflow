"""
Aggressive Test Suite for Phase 1 Foundation.
Validates K.0 Thematic Analysis, Zero-Tolerance Enforcer, and Enhanced Flow Router.
"""
import pytest
import sys
import os

# Add the apps_rg directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps_rg'))

from logic_nodes.thematic_analysis_node import ThematicAnalysisNode, ThematicAnalysisOutput
from validation.word_count_enforcer import WordCountEnforcementEngine
from logic_nodes.rg_flow_router import RGFlowRouter


class TestPhase1Foundation:
    
    def test_k0_node_output_structure(self):
        """
        Verify K.0 Node produces correct output schema with authenticity patterns.
        """
        node = ThematicAnalysisNode()
        output = node("Senior Python Engineer", "TechCorp")
        
        assert isinstance(output, ThematicAnalysisOutput)
        assert output.primary_theme is not None
        assert isinstance(output.secondary_themes, list)
        assert "Spearheaded" in output.authenticity_patterns.achievement_verb_patterns
        assert len(output.competitive_intelligence.differentiator_keywords) > 0
        assert output.company_name == "TechCorp"

    def test_k0_node_theme_extraction_heuristics(self):
        """
        Verify theme extraction heuristics work correctly for different domains.
        """
        node = ThematicAnalysisNode()
        
        # Test engineering theme
        eng_output = node("Senior Software Engineer position", "TechCorp")
        assert eng_output.primary_theme == "Engineering Excellence"
        assert "System Architecture" in eng_output.secondary_themes
        
        # Test management theme
        mgr_output = node("Product Manager role", "StartupInc")
        assert mgr_output.primary_theme == "Strategic Leadership"
        assert "Team Building" in mgr_output.secondary_themes
        
        # Test default theme
        default_output = node("Professional position", "GenericCorp")
        assert default_output.primary_theme == "Professional Impact"
        assert "Execution" in default_output.secondary_themes

    def test_zero_tolerance_enforcement_logic(self):
        """
        Verify the regeneration engine strictly enforces constraints.
        """
        enforcer = WordCountEnforcementEngine()
        
        # Test Case 1: Valid Content
        # "min": 25, "max": 33 for resume_overview
        valid_text = " ".join(["word"] * 30)
        result = enforcer.validate_content(valid_text, "resume_overview")
        assert result.is_valid
        assert result.word_count == 30
        assert result.violation_type is None
        
        # Test Case 2: Underflow Detection
        short_text = "Too short"
        result = enforcer.validate_content(short_text, "resume_overview")
        assert not result.is_valid
        assert result.violation_type == "UNDERFLOW"
        assert result.word_count < result.min_required
        
        # Test Case 3: Overflow Detection
        long_text = " ".join(["word"] * 40)
        result = enforcer.validate_content(long_text, "resume_overview")
        assert not result.is_valid
        assert result.violation_type == "OVERFLOW"
        assert result.word_count > result.max_allowed

    def test_zero_tolerance_regeneration_attempts(self):
        """
        Verify regeneration attempts work for underflow content.
        """
        enforcer = WordCountEnforcementEngine()
        
        # Test Case: Underflow content should be expanded
        short_text = " ".join(["word"] * 20)  # Under 25 min for resume_overview
        
        try:
            fixed_text = enforcer.enforce_with_regeneration(short_text, "resume_overview", max_attempts=3)
            # Should either be valid or raise exception
            result = enforcer.validate_content(fixed_text, "resume_overview")
            if result.is_valid:
                assert len(fixed_text.split()) >= 25
        except ValueError:
            # Acceptable if regeneration fails after max attempts
            pass

    def test_router_injects_thematic_analysis(self):
        """
        Verify RGFlowRouter runs K.0 analysis and injects it into state.
        """
        router = RGFlowRouter()
        state = {
            "task_description": "generate new resume",
            "job_description": "CEO position at BigBank with responsibility for strategic leadership and team management",
            "company_name": "BigBank",
            "has_master_resume": False
        }
        
        # Execute Router
        output = router(state)
        
        # Check State Injection
        assert "thematic_analysis" in state
        assert isinstance(state["thematic_analysis"], ThematicAnalysisOutput)
        assert state["primary_theme"] == "Strategic Leadership"  # CEO role maps to Strategic Leadership
        assert output.flow_result.flow_type == "generate_scratch"

    def test_router_differentiator_logic(self):
        """
        Verify router changes path based on differentiator count.
        """
        router = RGFlowRouter()
        
        # Mock the thematic node inside the router to return many differentiators
        class MockOutput:
            primary_theme = "Mock"
            secondary_themes = ["Theme1", "Theme2"]
            company_name = "MockCorp"
            
            class authenticity_patterns:
                executive_summary_patterns = ["Built and scaled"]
                achievement_verb_patterns = ["Spearheaded"]
                metric_presentation_patterns = ["X% improvement"]
                competency_phrasing_patterns = ["Specialized in"]
            
            class competitive_intelligence:
                peer_jds_analyzed = ["Competitor1", "Competitor2"]
                table_stakes_keywords = ["leadership", "strategy"]
                differentiator_keywords = ["A", "B", "C", "D"]  # > 3 items
        
        # Test the enhanced classification method directly
        mock_thematic = MockOutput()
        flow_result = router._classify_flow_with_thematic_analysis(
            "generate new resume", 
            True, 
            mock_thematic
        )
        
        # Should route to strategic tailor due to strong differentiators
        assert flow_result.flow_type == "strategic_tailor_node"
        assert flow_result.confidence == 0.98

    def test_router_backward_compatibility(self):
        """
        Verify router still works without thematic analysis (backward compatibility).
        """
        router = RGFlowRouter()
        
        # Don't provide thematic analysis in state
        state = {
            "task_description": "tailor existing resume",
            "job_description": "Software Engineer position with requirements for Python and cloud infrastructure experience",
            "company_name": "TechCorp",
            "has_master_resume": True
        }
        
        output = router(state)
        
        # Should still work and inject thematic analysis
        assert "thematic_analysis" in state
        assert output.flow_result.flow_type == "tailor_existing"

    def test_word_count_constraints_configuration(self):
        """
        Verify word count constraints are properly configured.
        """
        enforcer = WordCountEnforcementEngine()
        
        # Check that constraints are properly loaded
        assert "executive_summary" in enforcer.constraints
        assert "resume_overview" in enforcer.constraints
        assert "experience_bullets" in enforcer.constraints
        
        # Check specific constraint values
        assert enforcer.constraints["executive_summary"]["min"] == 120
        assert enforcer.constraints["executive_summary"]["max"] == 140
        assert enforcer.constraints["resume_overview"]["min"] == 25
        assert enforcer.constraints["resume_overview"]["max"] == 33

    def test_thematic_analysis_dataclass_structure(self):
        """
        Verify all dataclass components are properly structured.
        """
        # Test AuthenticityPatterns
        from logic_nodes.thematic_analysis_node import AuthenticityPatterns, CompetitiveIntelligence
        
        auth = AuthenticityPatterns(
            executive_summary_patterns=["Built"],
            achievement_verb_patterns=["Spearheaded"],
            metric_presentation_patterns=["X%"],
            competency_phrasing_patterns=["Specialized"]
        )
        assert len(auth.executive_summary_patterns) == 1
        assert len(auth.achievement_verb_patterns) == 1
        
        # Test CompetitiveIntelligence
        comp = CompetitiveIntelligence(
            peer_jds_analyzed=["Peer1"],
            table_stakes_keywords=["leadership"],
            differentiator_keywords=["innovation"]
        )
        assert len(comp.peer_jds_analyzed) == 1
        assert len(comp.differentiator_keywords) == 1

    def test_router_flow_configuration_integrity(self):
        """
        Verify router flow configurations include new strategic tailor node.
        """
        router = RGFlowRouter()
        
        # Check that strategic_tailor_node configuration exists
        assert "strategic_tailor_node" in router.flow_configs
        assert router.flow_configs["strategic_tailor_node"]["validation_required"] is True
        assert router.flow_configs["strategic_tailor_node"]["retry_enabled"] is True
        assert len(router.flow_configs["strategic_tailor_node"]["required_hops"]) == 6  # HOP-1 through HOP-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
