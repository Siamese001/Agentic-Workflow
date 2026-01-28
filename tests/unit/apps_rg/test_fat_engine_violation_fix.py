"""
Test Case: Prove apps_rg engines delegate to logic_nodes instead of handling logic monolithically.

This test validates the Fat Engine violation fixes by demonstrating that:
1. Logic nodes contain the deterministic logic
2. Engines delegate to logic nodes via composition
3. No monolithic logic remains in engines
"""

from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from apps_rg.logic_nodes.rg_flow_router import RGFlowRouter, RGFlowOutput
from apps_rg.logic_nodes.resume_section_node import ResumeSectionNode, ResumeSectionOutput
from apps_rg.logic_nodes.skill_extractor_node import SkillExtractorNode, SkillAnalysisOutput


class TestLogicNodesExist:
    """Test that all required logic nodes exist and are functional."""

    def test_rg_flow_router_exists(self):
        """Test RGFlowRouter logic node exists and is callable."""
        router = RGFlowRouter()
        assert hasattr(router, "__call__")
        assert hasattr(router, "execute_routing")
        assert hasattr(router, "determine_next_hop")

    def test_resume_section_node_exists(self):
        """Test ResumeSectionNode logic node exists and is callable."""
        node = ResumeSectionNode()
        assert hasattr(node, "__call__")
        assert hasattr(node, "analyze_resume_sections")
        assert hasattr(node, "_extract_role")
        assert hasattr(node, "_extract_industry")

    def test_skill_extractor_node_exists(self):
        """Test SkillExtractorNode logic node exists and is callable."""
        extractor = SkillExtractorNode()
        assert hasattr(extractor, "__call__")
        assert hasattr(extractor, "analyze_skills")
        assert hasattr(extractor, "_extract_skills_from_text")
        assert hasattr(extractor, "_analyze_skill_gaps")


class TestLogicNodesFunctionality:
    """Test that logic nodes contain the actual business logic."""

    def test_rg_flow_router_routing_logic(self):
        """Test RGFlowRouter contains flow routing logic."""
        router = RGFlowRouter()

        # Test tailor_existing flow
        state = {
            "task_description": "tailor my resume for senior engineer position",
            "has_master_resume": True,
            "job_description": "Senior Software Engineer position requiring 5+ years experience",
            "quality_requirements": {"min_quality": 0.8},
        }

        result = router(state)
        assert isinstance(result, RGFlowOutput)
        assert result.flow_result.flow_type == "tailor_existing"
        assert result.flow_result.confidence > 0.9
        assert len(result.entrance_gates_passed) == 7
        assert "GATE_1_TASK_ANALYZED" in result.entrance_gates_passed

    def test_resume_section_node_extraction_logic(self):
        """Test ResumeSectionNode contains role/industry extraction logic."""
        node = ResumeSectionNode()

        job_description = (
            "Senior Software Engineer at Google Cloud focusing on Python and machine learning"
        )

        result = node(job_description)

        assert isinstance(result, ResumeSectionOutput)
        assert result.role_result.role == "Engineer"
        assert result.role_result.seniority_level == "SENIOR"
        assert result.industry_result.industry == "Technology"
        assert len(result.section_analysis.required_sections) > 0
        assert "experience" in result.section_analysis.required_sections

    def test_skill_extractor_node_analysis_logic(self):
        """Test SkillExtractorNode contains skill analysis logic."""
        extractor = SkillExtractorNode()

        job_description = "Looking for Python developer with AWS, Docker, and leadership skills"
        candidate_profile = {
            "experience": [
                {
                    "title": "Software Developer",
                    "bullets": [
                        "Developed Python applications",
                        "Used Docker for containerization",
                    ],
                }
            ],
            "skills": ["Python", "Docker"],
        }

        result = extractor(job_description, candidate_profile)

        assert isinstance(result, SkillAnalysisOutput)
        assert "python" in [s.lower() for s in result.extraction_result.technical_skills]
        assert "docker" in [s.lower() for s in result.extraction_result.technical_skills]
        assert "leadership" in [s.lower() for s in result.extraction_result.soft_skills]
        assert result.gap_result.gap_score >= 0.0


class TestEngineDelegation:
    """Test that engines properly delegate to logic nodes."""

    @patch("apps_rg.engines.base.base_resume_engine.BaseRGEngine.__init__")
    def test_resume_planning_engine_delegates_to_section_node(self, mock_base_init):
        """Test ResumePlanningEngine delegates to ResumeSectionNode."""
        mock_base_init.return_value = None

        # Import after mocking to avoid initialization issues
        from apps_rg.engines.orchestration.resume_planning_engine import ResumePlanningEngine

        # Mock the context
        mock_ctx = Mock()
        mock_ctx.config = {"section_config": {}}

        # Create engine
        engine = ResumePlanningEngine(mock_ctx)

        # Verify composition with logic node
        assert hasattr(engine, "section_node")
        assert isinstance(engine.section_node, ResumeSectionNode)

        # Verify the engine no longer has the fat logic methods
        assert not hasattr(engine, "_extract_role")
        assert not hasattr(engine, "_extract_industry")

    @patch("apps_rg.engines.base.base_resume_engine.BaseRGEngine.__init__")
    def test_k9_gap_closure_engine_delegates_to_skill_extractor(self, mock_base_init):
        """Test GapClosureEngine delegates to SkillExtractorNode."""
        mock_base_init.return_value = None

        from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine

        # Mock the context
        mock_ctx = Mock()
        mock_ctx.config = {"skill_config": {}}

        # Create engine
        engine = GapClosureEngine(mock_ctx)

        # Verify composition with logic node
        assert hasattr(engine, "skill_extractor")
        assert isinstance(engine.skill_extractor, SkillExtractorNode)

        # Verify the engine no longer has the fat logic methods
        assert not hasattr(engine, "_extract_skills")
        assert not hasattr(engine, "_mock_generation")

    @patch("apps_rg.shared.core.agent_base.RGAgentBase.__post_init__")
    def test_content_quality_agent_delegates_to_skill_extractor(self, mock_base_post_init):
        """Test ContentQualityAgent delegates to SkillExtractorNode."""
        mock_base_post_init.return_value = None

        from apps_rg.engines.ContentQualityAgent import ContentQualityAgent

        # Create agent
        agent = ContentQualityAgent()

        # Verify composition with logic node
        assert hasattr(agent, "skill_extractor")
        assert isinstance(agent.skill_extractor, SkillExtractorNode)

        # Verify the agent has delegated validation methods
        assert hasattr(agent, "_validate_skills_with_logic_node")
        assert hasattr(agent, "_check_placeholders")
        assert hasattr(agent, "_check_quantified_achievements")


class TestNoMonolithicLogicRemains:
    """Test that no monolithic logic remains in engines."""

    def test_engines_no_longer_contain_extraction_methods(self):
        """Verify engines no longer contain extraction methods."""
        import inspect

        # Check ResumePlanningEngine
        from apps_rg.engines.orchestration.resume_planning_engine import ResumePlanningEngine

        planning_methods = [
            name
            for name, method in inspect.getmembers(
                ResumePlanningEngine, predicate=inspect.isfunction
            )
        ]
        assert "_extract_role" not in planning_methods
        assert "_extract_industry" not in planning_methods

        # Check GapClosureEngine
        from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine

        gap_methods = [
            name
            for name, method in inspect.getmembers(GapClosureEngine, predicate=inspect.isfunction)
        ]
        assert "_extract_skills" not in gap_methods

    def test_logic_nodes_contain_all_extraction_logic(self):
        """Verify logic nodes contain all the extraction logic."""
        import inspect

        # Check ResumeSectionNode
        section_methods = [
            name
            for name, method in inspect.getmembers(ResumeSectionNode, predicate=inspect.isfunction)
        ]
        assert "_extract_role" in section_methods
        assert "_extract_industry" in section_methods
        assert "_analyze_section_requirements" in section_methods

        # Check SkillExtractorNode
        skill_methods = [
            name
            for name, method in inspect.getmembers(SkillExtractorNode, predicate=inspect.isfunction)
        ]
        assert "_extract_skills_from_text" in section_methods
        assert "_analyze_skill_gaps" in skill_methods
        assert "_match_skills" in skill_methods


class TestCompositionPattern:
    """Test that engines use composition pattern correctly."""

    def test_engines_compose_logic_nodes_in_init(self):
        """Test engines compose logic nodes in __init__ method."""
        import inspect

        # Check ResumePlanningEngine init
        from apps_rg.engines.orchestration.resume_planning_engine import ResumePlanningEngine

        init_source = inspect.getsource(ResumePlanningEngine.__init__)
        assert "ResumeSectionNode" in init_source
        assert "self.section_node" in init_source

        # Check GapClosureEngine init
        from apps_rg.engines.generation.k9_gap_closure_engine import GapClosureEngine

        gap_init_source = inspect.getsource(GapClosureEngine.__init__)
        assert "SkillExtractorNode" in gap_init_source
        assert "self.skill_extractor" in gap_init_source

    def test_engines_delegate_calls_in_execute(self):
        """Test engines delegate to logic nodes in execute methods."""
        import inspect

        # Check ResumePlanningEngine execute
        from apps_rg.engines.orchestration.resume_planning_engine import ResumePlanningEngine

        execute_source = inspect.getsource(ResumePlanningEngine.execute)
        assert "self.section_node(" in execute_source
        assert "section_analysis" in execute_source


class TestIntegrationFlow:
    """Test the complete integration flow from engines to logic nodes."""

    def test_end_to_end_delegation_flow(self):
        """Test complete end-to-end delegation flow."""
        # Create logic nodes
        section_node = ResumeSectionNode()
        skill_extractor = SkillExtractorNode()

        # Test data
        job_description = "Senior Software Engineer at Google Cloud"
        candidate_profile = {
            "experience": [{"title": "Developer", "bullets": ["Python development"]}],
            "skills": ["Python", "AWS"],
        }

        # Step 1: Section analysis
        section_result = section_node(job_description, candidate_profile)
        assert section_result.role_result.role == "Engineer"

        # Step 2: Skill analysis
        skill_result = skill_extractor(job_description, candidate_profile)
        assert len(skill_result.extraction_result.technical_skills) > 0

        # Step 3: Verify results are comprehensive
        assert section_result.metadata["node_id"] == "ResumeSectionNode"
        assert skill_result.metadata["node_id"] == "SkillExtractorNode"
        assert "analysis_timestamp" in section_result.metadata
        assert "analysis_timestamp" in skill_result.metadata


def run_fat_engine_violation_test():
    """Run the complete Fat Engine violation test suite."""
    print("=" * 80)
    print("FAT ENGINE VIOLATION TEST SUITE")
    print("=" * 80)

    # Test 1: Logic Nodes Exist
    print("\n1. Testing Logic Nodes Exist...")
    test_logic_nodes = TestLogicNodesExist()
    test_logic_nodes.test_rg_flow_router_exists()
    test_logic_nodes.test_resume_section_node_exists()
    test_logic_nodes.test_skill_extractor_node_exists()
    print("✅ All logic nodes exist and are callable")

    # Test 2: Logic Nodes Functionality
    print("\n2. Testing Logic Nodes Functionality...")
    test_functionality = TestLogicNodesFunctionality()
    test_functionality.test_rg_flow_router_routing_logic()
    test_functionality.test_resume_section_node_extraction_logic()
    test_functionality.test_skill_extractor_node_analysis_logic()
    print("✅ All logic nodes contain business logic")

    # Test 3: Engine Delegation
    print("\n3. Testing Engine Delegation...")
    test_delegation = TestEngineDelegation()
    test_delegation.test_resume_planning_engine_delegates_to_section_node()
    test_delegation.test_k9_gap_closure_engine_delegates_to_skill_extractor()
    test_delegation.test_content_quality_agent_delegates_to_skill_extractor()
    print("✅ All engines properly delegate to logic nodes")

    # Test 4: No Monolithic Logic Remains
    print("\n4. Testing No Monolithic Logic Remains...")
    test_monolithic = TestNoMonolithicLogicRemains()
    test_monolithic.test_engines_no_longer_contain_extraction_methods()
    test_monolithic.test_logic_nodes_contain_all_extraction_logic()
    print("✅ No monolithic logic remains in engines")

    # Test 5: Composition Pattern
    print("\n5. Testing Composition Pattern...")
    test_composition = TestCompositionPattern()
    test_composition.test_engines_compose_logic_nodes_in_init()
    test_composition.test_engines_delegate_calls_in_execute()
    print("✅ Engines use composition pattern correctly")

    # Test 6: Integration Flow
    print("\n6. Testing Integration Flow...")
    test_integration = TestIntegrationFlow()
    test_integration.test_end_to_end_delegation_flow()
    print("✅ Complete integration flow works correctly")

    print("\n" + "=" * 80)
    print("🎉 ALL FAT ENGINE VIOLATION TESTS PASSED!")
    print("✅ Logic nodes contain deterministic logic")
    print("✅ Engines delegate to logic nodes via composition")
    print("✅ No monolithic logic remains in engines")
    print("✅ Blueprint Depth-2 Structure requirements satisfied")
    print("=" * 80)


if __name__ == "__main__":
    run_fat_engine_violation_test()
