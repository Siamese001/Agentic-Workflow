"""
Tests for archetype planner reasoning-intensity profiles.

Verifies that all archetypes get correct reasoning-intensity parameters
and that ExecutiveReasoningProfile is properly integrated.
"""

from l1.outreach_dataclasses import (
    ArchetypeType,
    EXECUTIVE_REASONING_PROFILES,
    compute_reasoning_multiplier
)
from l1.outreach_archetype_planning import OutreachArchetypePlanner, RecipientProfile, OutreachMission


class TestArchetypeReasoningProfiles:
    """Test archetype reasoning-intensity profile assignments."""
    
    def test_c_level_extreme_intensity_profile(self):
        """Test C_LEVEL gets extreme reasoning intensity."""
        profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        
        assert profile.reasoning_intensity == "extreme"
        assert profile.cot_depth == 12
        assert profile.tot_branches == 10
        assert profile.reflexion_passes == 3
        assert profile.sc_k == 10
        assert profile.require_deep_research is True
        assert len(profile.cognitive_axes) == 8
        
        # Verify unified multiplier
        multiplier = compute_reasoning_multiplier(profile)
        assert multiplier == 120  # 12 * 10
    
    def test_executive_high_intensity_profile(self):
        """Test EXECUTIVE gets high reasoning intensity."""
        profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE]
        
        assert profile.reasoning_intensity == "high"
        assert profile.cot_depth == 8
        assert profile.tot_branches == 6
        assert profile.reflexion_passes == 2
        assert profile.sc_k == 6
        assert profile.require_deep_research is True
        assert len(profile.cognitive_axes) == 8
        
        # Verify unified multiplier
        multiplier = compute_reasoning_multiplier(profile)
        assert multiplier == 48  # 8 * 6
    
    def test_senior_ta_medium_intensity_profile(self):
        """Test SENIOR_TA gets medium reasoning intensity."""
        profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.SENIOR_TA]
        
        assert profile.reasoning_intensity == "medium"
        assert profile.cot_depth == 4
        assert profile.tot_branches == 3
        assert profile.reflexion_passes == 1
        assert profile.sc_k == 3
        assert profile.require_deep_research is False
        assert len(profile.cognitive_axes) == 3
        
        # Verify unified multiplier
        multiplier = compute_reasoning_multiplier(profile)
        assert multiplier == 12  # 4 * 3
    
    def test_recruiter_low_intensity_profile(self):
        """Test RECRUITER gets low reasoning intensity."""
        profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER]
        
        assert profile.reasoning_intensity == "low"
        assert profile.cot_depth == 2
        assert profile.tot_branches == 2
        assert profile.reflexion_passes == 0
        assert profile.sc_k == 2
        assert profile.require_deep_research is False
        assert len(profile.cognitive_axes) == 1
        
        # Verify unified multiplier
        multiplier = compute_reasoning_multiplier(profile)
        assert multiplier == 4  # 2 * 2
    
    def test_archetype_planner_integrates_reasoning_profile(self):
        """Test archetype planner properly integrates ExecutiveReasoningProfile."""
        planner = OutreachArchetypePlanner()
        
        # Test C_LEVEL context building
        c_level_recipient = RecipientProfile(
            name="John Doe",
            title="CEO",
            company="TechCorp",
            industry="Technology",
            seniority="Executive",
            department="Executive",
            skills=["leadership", "strategy"],
            recent_activity=["funding round"],
            metadata={}
        )
        
        c_level_mission = OutreachMission(
            objective="Strategic partnership",
            target_role="Chief Executive Officer",
            value_proposition="Strategic leadership and growth",
            urgency="high",
            personalization_points=["recent funding"],
            constraints=["formal communication"],
            metadata={}
        )
        
        c_level_context = planner.build_archetype_context(c_level_recipient, c_level_mission)
        
        assert c_level_context.archetype == "c_level"
        assert c_level_context.executive_reasoning_profile.reasoning_intensity == "extreme"
        assert c_level_context.executive_reasoning_profile.cot_depth == 12
        assert c_level_context.executive_reasoning_profile.tot_branches == 10
        
        # Test EXECUTIVE context building
        executive_recipient = RecipientProfile(
            name="Jane Smith",
            title="VP Engineering",
            company="TechCorp",
            industry="Technology",
            seniority="Executive",
            department="Engineering",
            skills=["engineering", "leadership"],
            recent_activity=["product launch"],
            metadata={}
        )
        
        executive_mission = OutreachMission(
            objective="Technical leadership opportunity",
            target_role="Vice President of Engineering",
            value_proposition="Technical excellence and team scaling",
            urgency="medium",
            personalization_points=["recent product launch"],
            constraints=["technical depth"],
            metadata={}
        )
        
        executive_context = planner.build_archetype_context(executive_recipient, executive_mission)
        
        assert executive_context.archetype == "executive"
        assert executive_context.executive_reasoning_profile.reasoning_intensity == "high"
        assert executive_context.executive_reasoning_profile.cot_depth == 8
        assert executive_context.executive_reasoning_profile.tot_branches == 6
    
    def test_reasoning_intensity_scaling_consistency(self):
        """Test reasoning intensity scales consistently across archetypes."""
        profiles = [
            EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER],
            EXECUTIVE_REASONING_PROFILES[ArchetypeType.SENIOR_TA],
            EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE],
            EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        ]
        
        multipliers = [compute_reasoning_multiplier(p) for p in profiles]
        intensities = [p.reasoning_intensity for p in profiles]
        
        # Verify monotonic scaling
        assert multipliers == [4, 12, 48, 120]
        assert intensities == ["low", "medium", "high", "extreme"]
        
        # Verify each step increases significantly
        for i in range(1, len(multipliers)):
            assert multipliers[i] > multipliers[i-1]
            assert multipliers[i] >= multipliers[i-1] * 2  # At least 2x increase
