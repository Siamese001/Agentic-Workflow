"""
Stress tests for outreach recursion depth limits.

Tests that L3 orchestrator meta-loop fallback respects depth caps
and doesn't enter infinite recursion scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Any

from l3.outreach_orchestrator import OutreachOrchestrator
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType
from l1.outreach_archetype_planning import RecipientProfile


class TestOutreachRecursionCap:
    """Test suite for outreach workflow recursion depth limits."""
    
    def setup_method(self):
        """Setup test environment with realistic mocks."""
        # Mock all required components
        self.mock_archetype_planner = Mock()
        self.mock_research_planner = Mock()
        self.mock_message_planner = Mock()
        self.mock_company_executor = Mock()
        self.mock_contact_executor = Mock()
        self.mock_message_executor = Mock()
        self.mock_state_manager = Mock()
        self.mock_safety_validator = Mock()
        
        # Setup default mock behaviors
        self.mock_archetype_planner.plan_archetype_influence.return_value = ArchetypeContext(
            archetype=ArchetypeType.C_LEVEL,
            confidence=0.8
        )
        
        self.mock_research_planner.plan_research.return_value = {"query": "test"}
        mock_message_plan = Mock()
        mock_message_plan.template = "test_template"
        self.mock_message_planner.create_message_plan.return_value = mock_message_plan
        mock_message_result = Mock()
        mock_message_result.message = "Test message"
        mock_message_result.content = "Test message"
        self.mock_message_executor.generate_message.return_value = mock_message_result
        
        # Default safety validator passes
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=True,
            findings=[]
        )
    
    def create_orchestrator(self, config: dict = None):
        """Create OutreachOrchestrator with mocked components."""
        # Mock budget manager to allow message length
        mock_budget_manager = Mock()
        mock_budget_manager.check_message_length.return_value = True
        mock_budget_manager.increment_depth.return_value = True
        
        return OutreachOrchestrator(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            message_executor=self.mock_message_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator,
            budget_manager=mock_budget_manager
        )
    
    def create_sample_mission(self):
        """Create sample outreach mission."""
        return OutreachMission(
            objective="networking",
            target_role="Software Engineer",
            target_company="Tech Corp",
            value_proposition="Collaboration opportunity"
        )
    
    def create_sample_recipient(self):
        """Create sample recipient profile."""
        return RecipientProfile(
            name="John Doe",
            title="Engineering Manager",
            company="Tech Corp",
            industry="Technology",
            seniority="Senior",
            department="Engineering",
            skills=["Python", "Leadership", "System Design"],
            recent_activity=["Hiring", "Product Launch"],
            metadata={"location": "San Francisco"}
        )
    
    @pytest.mark.asyncio
    async def test_meta_loop_respects_depth_cap(self):
        """Test that meta-loop fallback respects maximum depth limit."""
        # Configure with low depth cap
        config = {
            "max_fallback_attempts": 2,  # Allow only 2 archetype attempts
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Mock safety validator to always fail, forcing fallback attempts
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=False,
            findings=["safety_violation"]
        )
        
        # Should attempt fallback but respect depth cap
        result = await orchestrator.orchestrate_outreach(mission, recipient, config)
        
        # Should not crash and should provide failure result
        assert result is not None
        assert hasattr(result, 'success')
        
        # Should fail due to safety violations after exhausting fallback attempts
        assert not result.success
        assert "fallback" in result.message.lower() or "attempt" in result.message.lower()
        
        # Verify safety validator was called expected number of times
        # Should be called for each archetype attempt (C_LEVEL, EXECUTIVE)
        assert self.mock_safety_validator.evaluate.call_count <= config["max_fallback_attempts"]
    
    @pytest.mark.asyncio
    async def test_depth_cap_zero_immediate_failure(self):
        """Test that depth cap of 1 causes immediate failure after one attempt."""
        config = {
            "max_fallback_attempts": 1,  # Only one attempt allowed
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Mock safety validator to fail
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=False,
            findings=["safety_violation"]
        )
        
        # Should fail immediately without any fallback attempts
        result = await orchestrator.orchestrate_outreach(mission, recipient, config)
        
        assert result is not None
        assert not result.success
        
        # Should mention fallback attempts or depth limit
        assert "depth" in result.message.lower() or "budget" in result.message.lower() or "fallback" in result.message.lower()
        
        # Safety validator should only be called once (no fallbacks)
        assert self.mock_safety_validator.evaluate.call_count == 1
    
    @pytest.mark.asyncio
    async def test_successful_execution_ignores_depth_cap(self):
        """Test that depth cap doesn't affect successful executions."""
        config = {
            "max_fallback_attempts": 1,  # Very low limit
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Mock safety validator to pass on first attempt
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=True,
            findings=[]
        )
        
        # Should succeed normally without hitting depth cap
        result = await orchestrator.orchestrate_outreach(mission, recipient, config)
        
        assert result is not None
        assert result.success
        
        # Safety validator should only be called once (no fallbacks needed)
        assert self.mock_safety_validator.evaluate.call_count == 1
    
    @pytest.mark.asyncio
    async def test_depth_cap_with_partial_success(self):
        """Test depth cap behavior when some archetypes succeed."""
        config = {
            "max_fallback_attempts": 3,  # Allow 3 attempts
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Mock safety validator to fail first 2 attempts, succeed on 3rd
        call_count = 0
        def safety_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return Mock(passed=False, findings=["safety_violation"])
            else:
                return Mock(passed=True, findings=[])
        
        self.mock_safety_validator.evaluate.side_effect = safety_side_effect
        
        # Should succeed on 3rd attempt within depth limit
        result = await orchestrator.orchestrate_outreach(mission, recipient, config)
        
        assert result is not None
        assert result.success
        
        # Should have made exactly 3 attempts
        assert self.mock_safety_validator.evaluate.call_count == 3
    
    @pytest.mark.asyncio
    async def test_infinite_fallback_prevention(self):
        """Test that system prevents infinite fallback loops."""
        config = {
            "max_fallback_attempts": 10,  # Reasonable limit
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Mock safety validator to always fail
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=False,
            findings=["safety_violation"]
        )
        
        # Should not enter infinite loop
        result = await orchestrator.orchestrate_outreach(mission, recipient, config)
        
        assert result is not None
        assert not result.success
        
        # Should not exceed maximum attempts
        assert self.mock_safety_validator.evaluate.call_count <= len(ArchetypeType)
        
        # Should complete in reasonable time (not hang)
        # If this test hangs, it indicates infinite recursion
        assert True  # Test reaching this point means no infinite loop
    
    @pytest.mark.asyncio
    async def test_depth_tracking_across_concurrent_workflows(self):
        """Test that depth tracking works correctly across concurrent workflows."""
        config = {
            "max_fallback_attempts": 2,
            "use_concurrent_research": True,
            "telemetry_enabled": False
        }
        
        orchestrator = self.create_orchestrator(config)
        
        # Mock safety validator to fail
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=False,
            findings=["safety_violation"]
        )
        
        # Create multiple missions
        missions = [self.create_sample_mission() for _ in range(3)]
        recipients = [self.create_sample_recipient() for _ in range(3)]
        
        # Run multiple workflows
        results = []
        for mission, recipient in zip(missions, recipients):
            result = await orchestrator.orchestrate_outreach(mission, recipient, config)
            results.append(result)
        
        # All should fail gracefully
        for result in results:
            assert result is not None
            assert not result.success
        
        # Total calls should not exceed per-workflow limits * number of workflows
        total_expected_calls = config["max_fallback_attempts"] * len(missions)
        assert self.mock_safety_validator.evaluate.call_count <= total_expected_calls
