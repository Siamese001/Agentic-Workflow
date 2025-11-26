"""
Tests for message planner reasoning-intensity functionality.

Verifies that message planner uses unified temperature adjustments,
content expansion, and exports complete metadata to L2.
"""

import pytest
from l1.outreach_dataclasses import (
    ArchetypeType,
    EXECUTIVE_REASONING_PROFILES,
    SECTION_TEMPERATURE_SCHEDULE,
    adjust_temperature_by_intensity,
    expand_section_by_intensity
)
from l1.message_planning import MessagePlanner, MessageContent
from l1.outreach_archetype_planning import OutreachArchetypePlanner


class TestMessageReasoningIntensity:
    """Test message planner reasoning-intensity functionality."""
    
    def test_temperature_adjustments_scale_correctly_per_section(self):
        """Test temperature adjustments scale correctly per section type."""
        base_schedule = SECTION_TEMPERATURE_SCHEDULE
        
        # Test C_LEVEL extreme intensity
        c_level_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        
        # Hook should increase (+0.15)
        hook_temp = adjust_temperature_by_intensity(base_schedule["hook"], c_level_profile, "hook")
        assert hook_temp == pytest.approx(0.95)  # 0.80 + 0.15
        
        # Value should increase (+0.15)
        value_temp = adjust_temperature_by_intensity(base_schedule["value"], c_level_profile, "value")
        assert value_temp == pytest.approx(0.70)  # 0.55 + 0.15
        
        # Subject should decrease (-0.05)
        subject_temp = adjust_temperature_by_intensity(base_schedule["subject"], c_level_profile, "subject")
        assert subject_temp == pytest.approx(0.60)  # 0.65 - 0.05
        
        # Signature should decrease (-0.05)
        signature_temp = adjust_temperature_by_intensity(base_schedule["signature"], c_level_profile, "signature")
        assert signature_temp == pytest.approx(0.40)  # 0.45 - 0.05
        
        # CTA should increase slightly (+0.05)
        cta_temp = adjust_temperature_by_intensity(base_schedule["cta"], c_level_profile, "cta")
        assert cta_temp == pytest.approx(0.75)  # 0.70 + 0.05
    
    def test_executive_high_intensity_temperature_adjustments(self):
        """Test EXECUTIVE high intensity temperature adjustments."""
        base_schedule = SECTION_TEMPERATURE_SCHEDULE
        executive_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE]
        
        # Hook should increase (+0.10)
        hook_temp = adjust_temperature_by_intensity(base_schedule["hook"], executive_profile, "hook")
        assert hook_temp == pytest.approx(0.90)  # 0.80 + 0.10
        
        # Value should increase (+0.10)
        value_temp = adjust_temperature_by_intensity(base_schedule["value"], executive_profile, "value")
        assert value_temp == pytest.approx(0.65)  # 0.55 + 0.10
        
        # Subject should decrease (-0.05)
        subject_temp = adjust_temperature_by_intensity(base_schedule["subject"], executive_profile, "subject")
        assert subject_temp == pytest.approx(0.60)  # 0.65 - 0.05
    
    def test_senior_ta_medium_intensity_temperature_adjustments(self):
        """Test SENIOR_TA medium intensity temperature adjustments."""
        base_schedule = SECTION_TEMPERATURE_SCHEDULE
        senior_ta_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.SENIOR_TA]
        
        # Hook should increase slightly (+0.05)
        hook_temp = adjust_temperature_by_intensity(base_schedule["hook"], senior_ta_profile, "hook")
        assert hook_temp == pytest.approx(0.85)  # 0.80 + 0.05
        
        # Value should increase slightly (+0.05)
        value_temp = adjust_temperature_by_intensity(base_schedule["value"], senior_ta_profile, "value")
        assert value_temp == pytest.approx(0.60)  # 0.55 + 0.05
        
        # Other sections should remain unchanged
        subject_temp = adjust_temperature_by_intensity(base_schedule["subject"], senior_ta_profile, "subject")
        assert subject_temp == pytest.approx(0.65)  # No change for medium intensity
    
    def test_recruiter_low_intensity_no_temperature_adjustments(self):
        """Test RECRUITER low intensity has no temperature adjustments."""
        base_schedule = SECTION_TEMPERATURE_SCHEDULE
        recruiter_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER]
        
        # All sections should remain at base temperature
        for section, base_temp in base_schedule.items():
            adjusted_temp = adjust_temperature_by_intensity(base_temp, recruiter_profile, section)
            assert adjusted_temp == base_temp
    
    def test_value_section_expansion_for_executive_archetypes(self):
        """Test value section content expansion for EXECUTIVE/C_LEVEL archetypes."""
        base_content = "Key value: Strategic business alignment"
        
        # Test C_LEVEL extreme expansion
        c_level_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        expanded_value = expand_section_by_intensity(base_content, c_level_profile, "value")
        
        assert "Across 8 key dimensions including:" in expanded_value
        assert "Strategic business impact with quantifiable outcomes" in expanded_value
        assert "Technical innovation aligned with market needs" in expanded_value
        assert "Operational excellence and scalability considerations" in expanded_value
        assert len(expanded_value) > len(base_content)
        
        # Test EXECUTIVE high expansion
        executive_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE]
        expanded_value = expand_section_by_intensity(base_content, executive_profile, "value")
        
        assert "Key business value propositions:" in expanded_value
        assert "Strategic alignment with your objectives" in expanded_value
        assert len(expanded_value) > len(base_content)
        assert "Across 8 key dimensions including:" not in expanded_value  # C_LEVEL only
    
    def test_hook_section_expansion_for_executive_archetypes(self):
        """Test hook section content expansion for EXECUTIVE/C_LEVEL archetypes."""
        base_content = "Following TechCorp's strategic direction thought you might find this relevant"
        
        # Test C_LEVEL extreme expansion
        c_level_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        expanded_hook = expand_section_by_intensity(base_content, c_level_profile, "hook")
        
        assert "Given strategic priorities," in expanded_hook
        assert "With deep consideration of your organizational context" in expanded_hook
        assert len(expanded_hook) > len(base_content)
        
        # Test EXECUTIVE high expansion
        executive_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE]
        expanded_hook = expand_section_by_intensity(base_content, executive_profile, "hook")
        
        assert "Given strategic priorities," in expanded_hook
        assert "With deep consideration of your organizational context" in expanded_hook
        assert len(expanded_hook) > len(base_content)
    
    def test_no_expansion_for_low_medium_intensity_archetypes(self):
        """Test no content expansion for low/medium intensity archetypes."""
        base_content = "Basic content"
        
        # Test SENIOR_TA medium intensity - no expansion
        senior_ta_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.SENIOR_TA]
        expanded_content = expand_section_by_intensity(base_content, senior_ta_profile, "value")
        assert expanded_content == base_content
        
        # Test RECRUITER low intensity - no expansion
        recruiter_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER]
        expanded_content = expand_section_by_intensity(base_content, recruiter_profile, "value")
        assert expanded_content == base_content
    
    def test_message_plan_exports_complete_reasoning_metadata(self):
        """Test MessagePlan exports complete reasoning-intensity metadata."""
        planner = MessagePlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Create C_LEVEL context
        context = archetype_planner.build_archetype_context(
            target_title="CEO",
            target_company="TechCorp",
            recipient_description="Chief Executive Officer"
        )
        
        content = MessageContent(
            recipient_name="John Doe",
            recipient_title="CEO",
            company_name="TechCorp",
            value_proposition="Strategic leadership",
            key_points=["business growth", "market expansion"],
            personalization_elements=["recent funding"],
            constraints=["formal tone"],
            metadata={}
        )
        
        # Generate message plan
        plan = planner.create_message_plan(content, context)
        
        # Verify complete reasoning-intensity metadata export
        metadata = plan.metadata
        
        # Base metadata
        assert metadata["archetype"] == ArchetypeType.C_LEVEL
        assert metadata["target_company"] == "TechCorp"
        assert "reasoning_mode" in metadata
        
        # Reasoning-intensity metadata
        assert metadata["reasoning_intensity"] == "extreme"
        assert metadata["cot_depth"] == 12
        assert metadata["tot_branches"] == 10
        assert metadata["reasoning_multiplier"] == 120  # 12 * 10
        assert metadata["reflexion_passes"] == 3
        assert metadata["sc_k"] == 10
        assert metadata["cognitive_axes"] == ["strategic", "financial", "technical", "competitive", "product", "operational", "risk", "psychographic"]
        assert metadata["require_deep_research"] is True
        assert "executive_profile" in metadata
    
    def test_message_plan_temperature_schedule_uses_unified_logic(self):
        """Test MessagePlan temperature schedule uses unified reasoning-intensity logic."""
        planner = MessagePlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Create EXECUTIVE context
        context = archetype_planner.build_archetype_context(
            target_title="VP Engineering",
            target_company="TechCorp",
            recipient_description="Vice President of Engineering"
        )
        
        content = MessageContent(
            recipient_name="Jane Smith",
            recipient_title="VP Engineering",
            company_name="TechCorp",
            value_proposition="Technical leadership",
            key_points=["team scaling", "innovation"],
            personalization_elements=["recent product launch"],
            constraints=["technical depth"],
            metadata={}
        )
        
        # Generate message plan
        plan = planner.create_message_plan(content, context)
        
        # Verify temperature adjustments match unified logic
        temps = plan.temperature_schedule
        
        # EXECUTIVE: hook +0.10, value +0.10, subject -0.05, signature -0.05, cta +0.05
        assert temps["hook"] == 0.90  # 0.80 + 0.10
        assert temps["value"] == 0.65  # 0.55 + 0.10
        assert temps["subject"] == 0.60  # 0.65 - 0.05
        assert temps["signature"] == 0.40  # 0.45 - 0.05
        assert temps["cta"] == 0.75  # 0.70 + 0.05
    
    def test_message_richness_increases_with_higher_intensity(self):
        """Test message richness increases with higher reasoning intensity."""
        planner = MessagePlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        content = MessageContent(
            recipient_name="Test Person",
            recipient_title="Test Title",
            company_name="TestCorp",
            value_proposition="Test value",
            key_points=["point 1", "point 2"],
            personalization_elements=["personalization"],
            constraints=["basic"],
            metadata={}
        )
        
        # Generate plans for different archetypes
        recruiter_context = archetype_planner.build_archetype_context(
            target_title="Recruiter",
            target_company="TestCorp",
            recipient_description="Technical Recruiter"
        )
        recruiter_context.archetype = ArchetypeType.RECRUITER
        recruiter_context.executive_reasoning_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER]
        
        c_level_context = archetype_planner.build_archetype_context(
            target_title="CEO",
            target_company="TestCorp",
            recipient_description="Chief Executive Officer"
        )
        c_level_context.archetype = ArchetypeType.C_LEVEL
        c_level_context.executive_reasoning_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        
        recruiter_plan = planner.create_message_plan(content, recruiter_context)
        c_level_plan = planner.create_message_plan(content, c_level_context)
        
        # Verify C_LEVEL plan is richer
        assert len(c_level_plan.value_plan) > len(recruiter_plan.value_plan)
        assert len(c_level_plan.hook_plan) > len(recruiter_plan.hook_plan)
        
        # Verify C_LEVEL has more detailed content
        assert "Across 8 key dimensions including:" in c_level_plan.value_plan
        assert "Across 8 key dimensions including:" not in recruiter_plan.value_plan
