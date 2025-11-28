"""Tests for LIC Fusion Planner - L1 pure planning layer."""

import pytest
from unittest.mock import MagicMock

from l1.lic_fusion_planner import (
    LICFusionPlanner,
    LICFusionPlan,
    LICValueProposition,
    LICMessageSectionPlan,
)


@pytest.fixture
def mock_telemetry_bus():
    """Mock telemetry bus."""
    bus = MagicMock()
    bus.record_event = MagicMock()
    return bus


@pytest.fixture
def default_planner():
    """Default LIC fusion planner."""
    return LICFusionPlanner()


@pytest.fixture
def planner_with_telemetry(mock_telemetry_bus):
    """LIC fusion planner with telemetry."""
    return LICFusionPlanner(telemetry_bus=mock_telemetry_bus)


@pytest.fixture
def sample_resume_features():
    """Sample resume features for testing."""
    return {
        "achievements": [
            {
                "id": "achievement_1",
                "text": "Led engineering team to deliver 25% revenue growth through strategic product roadmap",
                "impact_type": "revenue",
                "seniority_signal": "executive",
            },
            {
                "id": "achievement_2", 
                "text": "Reduced infrastructure costs by 40% by implementing cloud-native architecture",
                "impact_type": "cost",
                "seniority_signal": "manager",
            },
            {
                "id": "achievement_3",
                "text": "Scaled engineering team from 10 to 50 engineers while maintaining 95% retention",
                "impact_type": "team",
                "seniority_signal": "ic",
            },
        ],
        "skills": ["leadership", "technical", "strategy"],
        "experience_years": 8,
    }


@pytest.fixture
def sample_research_signals():
    """Sample research signals for testing."""
    return {
        "company_signals": [
            {
                "id": "company_signal_1",
                "text": "TechCorp is expanding their engineering leadership team",
                "description": "Company growth signal",
            },
            {
                "id": "company_signal_2", 
                "text": "Recent $50M Series B funding for product expansion",
                "description": "Funding signal",
            },
        ],
        "role_signals": [
            {
                "id": "role_signal_1",
                "text": "Seeking strategic technical leader for product roadmap",
                "description": "Role requirements signal",
            },
        ],
        "strategic_themes": ["growth", "funding", "product strategy"],
    }


@pytest.fixture
def sample_outreach_context():
    """Sample outreach context for testing."""
    return {
        "mission": "Test mission",
        "recipient_profile": {
            "name": "John Doe",
            "role_title": "Senior Software Engineer",
        },
    }


class TestLICFusionPlanner:
    """Test suite for LIC fusion planner."""
    
    def test_generates_value_props_from_resume_and_signals(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that value propositions are generated from resume and signals."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Should generate value propositions
        assert len(plan.value_propositions) > 0
        
        # Check value proposition structure
        for vp in plan.value_propositions:
            assert isinstance(vp, LICValueProposition)
            assert vp.id.startswith("vp_")
            assert vp.achievement_snippet
            assert vp.signal_snippet
            assert vp.archetype_target in ["EXECUTIVE", "SENIOR_TA", "RECRUITER"]
            assert vp.priority >= 1
            assert vp.angle in ["strategic", "operational", "technical"]
            assert vp.expected_impact
            assert isinstance(vp.metadata, dict)
    
    def test_respects_max_value_props_limit(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that max_value_props limit is respected."""
        planner = LICFusionPlanner(max_value_props=2)
        
        plan = planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        assert len(plan.value_propositions) <= 2
    
    def test_sections_include_opening_body_and_cta_in_order(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that sections include opening, body, and CTA in correct order."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Should have at least opening and CTA sections
        assert len(plan.sections) >= 2
        
        # Check section order
        section_types = [section.section_type for section in plan.sections]
        assert "opening" in section_types
        assert "cta" in section_types
        
        # Opening should come before CTA
        opening_index = section_types.index("opening")
        cta_index = section_types.index("cta")
        assert opening_index < cta_index
    
    def test_archetype_specific_cta_styles_for_executive(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test CTA styles for EXECUTIVE archetype."""
        planner = LICFusionPlanner(enable_exec_strict_cta=True)
        
        plan = planner.plan(
            role_title="VP Engineering",
            company_name="TechCorp",
            archetype="EXECUTIVE",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        assert plan.primary_cta_style == "light_touch"
        assert plan.fallback_cta_style == "exploratory_call"
        
        # Check CTA section guidance
        cta_section = next(s for s in plan.sections if s.section_type == "cta")
        assert "strategic alignment" in cta_section.cta_guidance.lower()
    
    def test_archetype_specific_cta_styles_for_senior_ta(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test CTA styles for SENIOR_TA archetype."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        assert plan.primary_cta_style == "exploratory_call"
        assert plan.fallback_cta_style == "light_touch"
        
        # Check CTA section guidance
        cta_section = next(s for s in plan.sections if s.section_type == "cta")
        assert "technical discussion" in cta_section.cta_guidance.lower()
    
    def test_archetype_specific_cta_styles_for_recruiter(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test CTA styles for RECRUITER archetype."""
        plan = default_planner.plan(
            role_title="Technical Recruiter",
            company_name="TechCorp",
            archetype="RECRUITER",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        assert plan.primary_cta_style == "direct"
        assert plan.fallback_cta_style == "light_touch"
        
        # Check CTA section guidance
        cta_section = next(s for s in plan.sections if s.section_type == "cta")
        assert "role alignment" in cta_section.cta_guidance.lower()
    
    def test_value_props_prioritized_by_strategic_and_numeric_impact(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that value propositions are prioritized correctly."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Sort by priority (lower = higher priority)
        sorted_vps = sorted(plan.value_propositions, key=lambda x: x.priority)
        
        # First VP should have priority 1
        assert sorted_vps[0].priority == 1
        
        # Strategic VPs should get higher priority (lower score)
        strategic_vps = [vp for vp in sorted_vps if vp.angle == "strategic"]
        if strategic_vps:
            # Strategic VPs should appear early in the list
            assert strategic_vps[0].priority <= 3
        
        # VPs with numeric impact should get higher priority
        numeric_vps = [
            vp for vp in sorted_vps 
            if any(char in vp.achievement_snippet.lower() for char in ["%", "$", "m", "k", "x"])
        ]
        if numeric_vps:
            assert numeric_vps[0].priority <= 3
    
    def test_metadata_includes_counts_and_styles(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that plan metadata includes required counts and styles."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Check plan metadata
        assert "archetype" in plan.metadata
        assert "role_title" in plan.metadata
        assert "company_name" in plan.metadata
        assert "value_prop_count" in plan.metadata
        assert "primary_cta_style" in plan.metadata
        assert "fallback_cta_style" in plan.metadata
        
        assert plan.metadata["archetype"] == "SENIOR_TA"
        assert plan.metadata["role_title"] == "Senior Software Engineer"
        assert plan.metadata["company_name"] == "TechCorp"
        assert plan.metadata["value_prop_count"] == len(plan.value_propositions)
        assert plan.metadata["primary_cta_style"] == plan.primary_cta_style
        assert plan.metadata["fallback_cta_style"] == plan.fallback_cta_style
    
    def test_section_metadata_contains_indices_and_terminal_flags(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that section metadata contains indices and terminal flags."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        for i, section in enumerate(plan.sections):
            assert "section_index" in section.metadata
            assert "is_terminal_section" in section.metadata
            
            if section.section_type == "cta":
                assert section.metadata["is_terminal_section"] is True
            else:
                assert section.metadata["is_terminal_section"] is False
    
    def test_fusion_planner_is_pure_and_does_not_call_execution(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that fusion planner is pure with no external execution calls."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Verify plan structure
        assert isinstance(plan, LICFusionPlan)
        assert plan.role_title == "Senior Software Engineer"
        assert plan.company_name == "TechCorp"
        assert plan.archetype == "SENIOR_TA"
        assert isinstance(plan.value_propositions, list)
        assert isinstance(plan.sections, list)
        
        # Verify all value props are pure data
        for vp in plan.value_propositions:
            assert isinstance(vp, LICValueProposition)
            assert isinstance(vp.achievement_snippet, str)
            assert isinstance(vp.signal_snippet, str)
            assert isinstance(vp.archetype_target, str)
            assert isinstance(vp.priority, int)
            assert isinstance(vp.angle, str)
            assert isinstance(vp.expected_impact, str)
            assert isinstance(vp.metadata, dict)
        
        # Verify all sections are pure data
        for section in plan.sections:
            assert isinstance(section, LICMessageSectionPlan)
            assert isinstance(section.section_type, str)
            assert isinstance(section.archetype_target, str)
            assert isinstance(section.value_proposition_ids, list)
            assert isinstance(section.tone_guidance, str)
            assert isinstance(section.metadata, dict)
    
    def test_custom_max_body_sections_configuration(
        self,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test custom max_body_sections configuration."""
        planner = LICFusionPlanner(max_body_sections=3)
        
        plan = planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Count body sections
        body_sections = [s for s in plan.sections if s.section_type == "body"]
        assert len(body_sections) <= 3
    
    def test_exec_strict_cta_configuration(
        self,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test enable_exec_strict_cta configuration."""
        # Test with strict CTA enabled
        planner_strict = LICFusionPlanner(enable_exec_strict_cta=True)
        plan_strict = planner_strict.plan(
            role_title="VP Engineering",
            company_name="TechCorp",
            archetype="EXECUTIVE",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        assert plan_strict.primary_cta_style == "light_touch"
        
        # Test with strict CTA disabled
        planner_loose = LICFusionPlanner(enable_exec_strict_cta=False)
        plan_loose = planner_loose.plan(
            role_title="VP Engineering",
            company_name="TechCorp",
            archetype="EXECUTIVE",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        assert plan_loose.primary_cta_style == "exploratory_call"
    
    def test_telemetry_recording(
        self,
        planner_with_telemetry,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
        mock_telemetry_bus,
    ):
        """Test that telemetry is recorded correctly."""
        plan = planner_with_telemetry.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Verify telemetry was recorded
        mock_telemetry_bus.record_event.assert_called_once_with(
            "lic_fusion_plan_created",
            layer="L1",
            payload={
                "archetype": "SENIOR_TA",
                "role_title": "Senior Software Engineer",
                "company_name": "TechCorp",
                "value_prop_count": len(plan.value_propositions),
                "section_count": len(plan.sections),
                "primary_cta_style": plan.primary_cta_style,
            },
        )
    
    def test_telemetry_error_handling(
        self,
        planner_with_telemetry,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that telemetry errors don't break planning."""
        # Make telemetry bus raise exceptions
        planner_with_telemetry.telemetry_bus.record_event.side_effect = Exception("Telemetry failed")
        
        # Planning should still work despite telemetry failure
        plan = planner_with_telemetry.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Should still produce valid plan
        assert isinstance(plan, LICFusionPlan)
        assert len(plan.value_propositions) > 0
        assert len(plan.sections) > 0
    
    def test_empty_resume_features_handling(
        self,
        default_planner,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test handling of empty resume features."""
        empty_resume = {"achievements": []}
        
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=empty_resume,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Should still produce a plan structure
        assert isinstance(plan, LICFusionPlan)
        assert plan.role_title == "Senior Software Engineer"
        assert plan.company_name == "TechCorp"
        assert plan.archetype == "SENIOR_TA"
        
        # But no value propositions
        assert len(plan.value_propositions) == 0
    
    def test_empty_research_signals_handling(
        self,
        default_planner,
        sample_resume_features,
        sample_outreach_context,
    ):
        """Test handling of empty research signals."""
        empty_signals = {
            "company_signals": [],
            "role_signals": [],
            "strategic_themes": [],
        }
        
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=empty_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Should still produce a plan structure
        assert isinstance(plan, LICFusionPlan)
        assert plan.role_title == "Senior Software Engineer"
        assert plan.company_name == "TechCorp"
        assert plan.archetype == "SENIOR_TA"
        
        # But no value propositions
        assert len(plan.value_propositions) == 0
    
    def test_deterministic_planning(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that planning is deterministic."""
        plan1 = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        plan2 = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Plans should be identical (deterministic)
        assert len(plan1.value_propositions) == len(plan2.value_propositions)
        assert len(plan1.sections) == len(plan2.sections)
        assert plan1.primary_cta_style == plan2.primary_cta_style
        assert plan1.fallback_cta_style == plan2.fallback_cta_style
        
        # Value props should be identical
        for vp1, vp2 in zip(plan1.value_propositions, plan2.value_propositions):
            assert vp1.achievement_snippet == vp2.achievement_snippet
            assert vp1.signal_snippet == vp2.signal_snippet
            assert vp1.priority == vp2.priority
            assert vp1.angle == vp2.angle
    
    def test_archetype_target_determination(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that archetype targets are determined correctly."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        # Should have EXECUTIVE targets for executive seniority
        executive_vps = [
            vp for vp in plan.value_propositions 
            if vp.archetype_target == "EXECUTIVE"
        ]
        assert len(executive_vps) > 0
    
    def test_text_truncation_in_snippets(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test that text snippets are properly truncated."""
        plan = default_planner.plan(
            role_title="Senior Software Engineer",
            company_name="TechCorp",
            archetype="SENIOR_TA",
            resume_features=sample_resume_features,
            research_signals=sample_research_signals,
            outreach_context=sample_outreach_context,
        )
        
        for vp in plan.value_propositions:
            # Achievement snippets should be truncated to 100 chars
            assert len(vp.achievement_snippet) <= 100
            # Signal snippets should be truncated to 80 chars
            assert len(vp.signal_snippet) <= 80
    
    def test_different_archetypes_and_roles(
        self,
        default_planner,
        sample_resume_features,
        sample_research_signals,
        sample_outreach_context,
    ):
        """Test planner with different archetypes and roles."""
        test_cases = [
            ("Product Manager", "EXECUTIVE"),
            ("Data Scientist", "SENIOR_TA"),
            ("Technical Recruiter", "RECRUITER"),
        ]
        
        for role_title, archetype in test_cases:
            plan = default_planner.plan(
                role_title=role_title,
                company_name="TechCorp",
                archetype=archetype,
                resume_features=sample_resume_features,
                research_signals=sample_research_signals,
                outreach_context=sample_outreach_context,
            )
            
            assert plan.role_title == role_title
            assert plan.archetype == archetype
            assert plan.company_name == "TechCorp"
            assert isinstance(plan.value_propositions, list)
            assert isinstance(plan.sections, list)


if __name__ == "__main__":
    pytest.main([__file__])
