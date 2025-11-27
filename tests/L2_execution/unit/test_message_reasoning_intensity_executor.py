"""
Tests for L2 message generation executor reasoning-intensity integration.

Validates that L2 executors consume and respect reasoning-intensity metadata
exported by L1 MessagePlan, including prompt construction and temperature usage.
"""

import pytest
from unittest.mock import Mock
from l2.message_generation_executor import (
    MessageGenerationExecutor,
    GenerationContext,
    MessageSection,
    MessageResult
)
from l1.outreach_dataclasses import (
    ArchetypeType,
    EXECUTIVE_REASONING_PROFILES,
    reasoning_intensity_metadata
)
from l1.message_planning import MessagePlanner, MessageContent
from l1.outreach_archetype_planning import OutreachArchetypePlanner, RecipientProfile, OutreachMission


class TestMessageReasoningIntensityExecutor:
    """Test L2 executor reasoning-intensity metadata consumption."""
    
    def test_l2_consumes_reasoning_multiplier_for_executive(self):
        """Test L2 uses reasoning multiplier for EXECUTIVE intensity prompts."""
        # Create mock LLM caller
        mock_llm_caller = Mock()
        mock_llm_caller.generate.return_value = "Generated content"
        mock_llm_caller.generate.return_value = "Generated content"
        mock_llm_caller.call_llm.return_value = "Generated content"
        
        # Create executor
        executor = MessageGenerationExecutor(mock_llm_caller)
        
        # Create EXECUTIVE message plan with reasoning-intensity metadata
        executive_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.EXECUTIVE]
        reasoning_metadata = reasoning_intensity_metadata(executive_profile)
        
        message_plan = {
            "subject_plan": "Strategic Business Opportunity",
            "hook_plan": "Interested in your team's work at TechCorp",
            "value_plan": "Key business value propositions: Strategic alignment",
            "cta_plan": "For detailed business value discussion,",
            "signature_plan": "[Sender Name] | [Title] | [Contact Information]",
            "temperature_schedule": {
                "subject": 0.60, "hook": 0.90, "value": 0.65, "cta": 0.75, "signature": 0.40
            },
            "metadata": reasoning_metadata,
            "generation_strategy": "balanced_approach"
        }
        
        # Create generation context
        ctx = GenerationContext(
            mission_id="test-mission",
            archetype="executive",
            target_role="VP Engineering",
            target_company="TechCorp",
            value_proposition="Technical leadership",
            personalization_points=["product launch"],
            constraints=["technical depth"],
            metadata={}
        )
        
        # Generate message
        result = executor.generate_message(message_plan, ctx, [])
        
        # Verify LLM was called with reasoning-intensity enhanced prompts
        assert mock_llm_caller.generate.call_count == 5  # 5 sections
        
        # Check that value section prompt includes reasoning instructions
        value_prompt = mock_llm_caller.generate.call_args_list[2][0][0]  # 3rd call (value)
        assert "REASONING INTENSITY: HIGH" in value_prompt
        assert "structured reasoning with clear justification steps" in value_prompt
        assert "Chain-of-Thought depth: 8 steps" in value_prompt
        assert "Tree-of-Thought branches: 6" in value_prompt
        
        # Check that hook section prompt includes reasoning instructions
        hook_prompt = mock_llm_caller.generate.call_args_list[1][0][0]  # 2nd call (hook)
        assert "REASONING INTENSITY: HIGH" in hook_prompt
        assert "structured reasoning with clear justification steps" in hook_prompt
    
    def test_l2_respects_section_temperatures(self):
        """Test L2 uses temperature values from L1 MessagePlan."""
        # Create mock LLM caller
        mock_llm_caller = Mock()
        mock_llm_caller.generate.return_value = "Generated content"
        mock_llm_caller.call_llm.return_value = "Generated content"
        
        # Create executor
        executor = MessageGenerationExecutor(mock_llm_caller)
        
        # Create C_LEVEL message plan with specific temperature schedule
        c_level_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        reasoning_metadata = reasoning_intensity_metadata(c_level_profile)
        
        message_plan = {
            "subject_plan": "Strategic Partnership Discussion",
            "hook_plan": "Following TechCorp's strategic direction",
            "value_plan": "Across 8 key dimensions including: Strategic business impact",
            "cta_plan": "For comprehensive discussion of strategic implications,",
            "signature_plan": "[Sender Name] | [Title] | [Contact Information]",
            "temperature_schedule": {
                "subject": 0.60, "hook": 0.95, "value": 0.70, "cta": 0.75, "signature": 0.40
            },
            "metadata": reasoning_metadata,
            "generation_strategy": "concise_priority"
        }
        
        # Create generation context
        ctx = GenerationContext(
            mission_id="test-mission",
            archetype="c_level",
            target_role="CEO",
            target_company="TechCorp",
            value_proposition="Strategic leadership",
            personalization_points=["funding"],
            constraints=["formal"],
            metadata={}
        )
        
        # Generate message
        result = executor.generate_message(message_plan, ctx, [])
        
        # Verify temperature schedule is preserved in result
        assert result.temperature_schedule["subject"] == 0.60
        assert result.temperature_schedule["hook"] == 0.95
        assert result.temperature_schedule["value"] == 0.70
        assert result.temperature_schedule["cta"] == 0.75
        assert result.temperature_schedule["signature"] == 0.40
        
        # Verify sections use correct temperatures
        assert result.sections["subject"].temperature_used == 0.60
        assert result.sections["hook"].temperature_used == 0.95
        assert result.sections["value"].temperature_used == 0.70
        assert result.sections["cta"].temperature_used == 0.75
        assert result.sections["signature"].temperature_used == 0.40
    
    def test_l2_does_not_break_for_low_intensity(self):
        """Test L2 handles RECRUITER low intensity without over-expansion."""
        # Create mock LLM caller
        mock_llm_caller = Mock()
        mock_llm_caller.generate.return_value = "Generated content"
        mock_llm_caller.call_llm.return_value = "Generated content"
        
        # Create executor
        executor = MessageGenerationExecutor(mock_llm_caller)
        
        # Create RECRUITER message plan with low intensity metadata
        recruiter_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.RECRUITER]
        reasoning_metadata = reasoning_intensity_metadata(recruiter_profile)
        
        message_plan = {
            "subject_plan": "Potential Opportunity",
            "hook_plan": "Regarding opportunities at TechCorp",
            "value_plan": "Key value: Technical skills",
            "cta_plan": "Would you be open to a brief conversation to learn more?",
            "signature_plan": "[Sender Name] | [Title] | [Contact Information]",
            "temperature_schedule": {
                "subject": 0.65, "hook": 0.80, "value": 0.55, "cta": 0.70, "signature": 0.45
            },
            "metadata": reasoning_metadata,
            "generation_strategy": "sequential"
        }
        
        # Create generation context
        ctx = GenerationContext(
            mission_id="test-mission",
            archetype="recruiter",
            target_role="Technical Recruiter",
            target_company="TechCorp",
            value_proposition="Technical skills",
            personalization_points=[],
            constraints=["basic"],
            metadata={}
        )
        
        # Generate message
        result = executor.generate_message(message_plan, ctx, [])
        
        # Verify LLM was called with clean prompts (no reasoning instructions)
        assert mock_llm_caller.generate.call_count == 5
        
        # Check that value section prompt does NOT include reasoning instructions
        value_prompt = mock_llm_caller.generate.call_args_list[2][0][0]  # 3rd call (value)
        assert "REASONING INTENSITY:" not in value_prompt
        assert "Chain-of-Thought depth:" not in value_prompt
        assert "Tree-of-Thought branches:" not in value_prompt
        
        # Verify reasonable temperatures (no extreme adjustments)
        assert result.temperature_schedule["hook"] == 0.80  # Base temperature
        assert result.temperature_schedule["value"] == 0.55  # Base temperature
    
    def test_l2_extreme_intensity_includes_comprehensive_reasoning(self):
        """Test C_LEVEL extreme intensity gets comprehensive reasoning instructions."""
        # Create mock LLM caller
        mock_llm_caller = Mock()
        mock_llm_caller.generate.return_value = "Generated content"
        mock_llm_caller.call_llm.return_value = "Generated content"
        
        # Create executor
        executor = MessageGenerationExecutor(mock_llm_caller)
        
        # Create C_LEVEL message plan with extreme intensity
        c_level_profile = EXECUTIVE_REASONING_PROFILES[ArchetypeType.C_LEVEL]
        reasoning_metadata = reasoning_intensity_metadata(c_level_profile)
        
        message_plan = {
            "value_plan": "Strategic business alignment",
            "temperature_schedule": {"value": 0.70},
            "metadata": reasoning_metadata,
            "generation_strategy": "concise_priority"
        }
        
        # Create generation context
        ctx = GenerationContext(
            mission_id="test-mission",
            archetype="c_level",
            target_role="CEO",
            target_company="TechCorp",
            value_proposition="Strategic leadership",
            personalization_points=["funding"],
            constraints=["formal"],
            metadata={}
        )
        
        # Generate single section to test prompt
        section = executor._generate_section(
            section_name="value",
            plan="Strategic business alignment",
            temperature=0.70,
            ctx=ctx,
            signal_context="",
            reasoning_metadata=reasoning_metadata
        )
        
        # Verify LLM was called with comprehensive reasoning instructions
        value_prompt = mock_llm_caller.generate.call_args[0][0]
        assert "REASONING INTENSITY: EXTREME" in value_prompt
        assert "multi-step justification with explicit reasoning chains" in value_prompt
        assert "3-4 distinct value dimensions with specific examples" in value_prompt
        assert "strategic implications and business impact quantification" in value_prompt
        assert "Chain-of-Thought depth: 12 steps" in value_prompt
        assert "Tree-of-Thought branches: 10" in value_prompt
        assert "precision, specificity, and quantifiable outcomes" in value_prompt
    
    def test_l2_reasoning_instructions_helper_method(self):
        """Test _build_reasoning_instructions helper method behavior."""
        executor = MessageGenerationExecutor(Mock())
        
        # Test extreme intensity for value section
        extreme_metadata = {
            "reasoning_intensity": "extreme",
            "reasoning_multiplier": 120,
            "cot_depth": 12,
            "tot_branches": 10
        }
        
        instructions = executor._build_reasoning_instructions(extreme_metadata, "value")
        
        assert "REASONING INTENSITY: EXTREME" in instructions
        assert "multi-step justification" in instructions
        assert "12 steps" in instructions
        assert "10" in instructions  # Tree-of-Thought branches
        
        # Test low intensity for any section
        low_metadata = {
            "reasoning_intensity": "low",
            "reasoning_multiplier": 4,
            "cot_depth": 2,
            "tot_branches": 2
        }
        
        instructions = executor._build_reasoning_instructions(low_metadata, "value")
        assert instructions == ""
        
        # Test high intensity for subject section (lighter enhancement)
        high_metadata = {
            "reasoning_intensity": "high",
            "reasoning_multiplier": 48,
            "cot_depth": 8,
            "tot_branches": 6
        }
        
        instructions = executor._build_reasoning_instructions(high_metadata, "subject")
        assert "REASONING INTENSITY: HIGH" in instructions
        assert "professional" in instructions.lower() or "benefit" in instructions.lower()
    
    def test_end_to_end_reasoning_intensity_propagation(self):
        """Test complete end-to-end propagation from L1 to L2."""
        # Create L1 planner and archetype planner
        message_planner = MessagePlanner()
        archetype_planner = OutreachArchetypePlanner()
        
        # Create C_LEVEL context
        recipient = RecipientProfile(
            name="John Doe", title="CEO", company="TechCorp", industry="Technology",
            seniority="Executive", department="Executive", skills=["leadership"],
            recent_activity=["funding"], metadata={}
        )
        
        mission = OutreachMission(
            objective="Strategic partnership", target_role="CEO",
            value_proposition="Strategic leadership", urgency="high",
            personalization_points=["funding"], constraints=["formal"], metadata={}
        )
        
        context = archetype_planner.build_archetype_context(recipient, mission)
        
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
        
        # Generate L1 message plan
        l1_plan = message_planner.create_message_plan(content, context)
        
        # Create L2 executor
        mock_llm_caller = Mock()
        mock_llm_caller.generate.return_value = "Generated content"
        mock_llm_caller.call_llm.return_value = "Generated content"
        executor = MessageGenerationExecutor(mock_llm_caller)
        
        # Convert L1 plan to dict format for L2
        message_plan_dict = {
            "subject_plan": l1_plan.subject_plan,
            "hook_plan": l1_plan.hook_plan,
            "value_plan": l1_plan.value_plan,
            "cta_plan": l1_plan.cta_plan,
            "signature_plan": l1_plan.signature_plan,
            "temperature_schedule": l1_plan.temperature_schedule,
            "metadata": l1_plan.metadata,
            "generation_strategy": l1_plan.generation_strategy
        }
        
        # Create L2 generation context
        ctx = GenerationContext(
            mission_id="test-mission",
            archetype="c_level",
            target_role="CEO",
            target_company="TechCorp",
            value_proposition="Strategic leadership",
            personalization_points=["funding"],
            constraints=["formal"],
            metadata={}
        )
        
        # Generate message in L2
        result = executor.generate_message(message_plan_dict, ctx, [])
        
        # Verify reasoning-intensity metadata propagated correctly
        assert result.metadata["archetype"] == "c_level"
        assert l1_plan.metadata["reasoning_intensity"] == "extreme"
        assert l1_plan.metadata["reasoning_multiplier"] == 120
        
        # Verify L2 used reasoning-intensity enhanced prompts
        value_prompt = mock_llm_caller.generate.call_args_list[2][0][0]
        assert "REASONING INTENSITY: EXTREME" in value_prompt
        assert "12 steps" in value_prompt
        assert "10" in value_prompt
        
        # Verify temperature schedule preserved
        assert result.temperature_schedule == l1_plan.temperature_schedule
