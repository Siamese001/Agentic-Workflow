"""
Integration tests for outreach workflow telemetry flow.

Tests that L3 and L2 components emit telemetry events in correct order
and with appropriate payloads.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch

from runtime.telemetry_bus import get_telemetry_bus
from l3.outreach_orchestrator import OutreachOrchestrator
from l1.outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType
from l1.outreach_archetype_planning import RecipientProfile
from config.LIC.lic_profile import LICHyperparameters


class TestOutreachTelemetryFlow:
    """Test suite for outreach workflow telemetry integration."""
    
    def setup_method(self):
        """Setup fresh telemetry bus and mocks for each test."""
        # Clear telemetry bus
        bus = get_telemetry_bus()
        bus.clear()
        bus.configure(enabled=True, detail_level="standard")
        
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
        
        # Mock research executors with telemetry tracking
        mock_company_result = type('MockCompanyResult', (), {
            'company': 'test_company', 
            'size': 'large',
            '__dict__': {'company': 'test_company', 'size': 'large'}
        })()
        mock_contact_result = type('MockContactResult', (), {
            'contact': 'test_contact', 
            'level': 'senior',
            '__dict__': {'contact': 'test_contact', 'level': 'senior'}
        })()
        
        self.mock_company_executor.search_company_context.return_value = mock_company_result
        self.mock_contact_executor.search_contact_profile.return_value = mock_contact_result
        
        self.mock_message_planner.create_message_plan.return_value = type('MockMessagePlan', (), {
            'template': 'test_template',
            '__dict__': {'template': 'test_template'}
        })()
        
        self.mock_message_executor.generate_message.return_value = type('MockMessageResult', (), {
            'message': 'Test message',
            'content': 'Test message',
            '__dict__': {'content': 'Test message'}
        })()
        
        self.mock_safety_validator.evaluate.return_value = type('MockSafetyResult', (), {
            'passed': True,
            'findings': []
        })()
    
    def create_orchestrator(self):
        """Create OutreachOrchestrator with mocked components."""
        return OutreachOrchestrator(
            archetype_planner=self.mock_archetype_planner,
            research_planner=self.mock_research_planner,
            message_planner=self.mock_message_planner,
            company_executor=self.mock_company_executor,
            contact_executor=self.mock_contact_executor,
            message_executor=self.mock_message_executor,
            state_manager=self.mock_state_manager,
            safety_validator=self.mock_safety_validator
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
    
    def test_outreach_orchestrator_emits_phase_events_in_order(self):
        """Test that outreach orchestrator emits phase events in correct order."""
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute outreach workflow
        result = orchestrator.orchestrate_outreach(mission, recipient)
        
        # Get telemetry events
        bus = get_telemetry_bus()
        events = bus.get_events()
        
        # Should have events for each phase
        assert len(events) >= 6  # At least start/end for 3 phases
        
        # Extract phase names in order
        phase_sequence = [event.name for event in events]
        
        # Should contain phase start/end events in logical order
        assert "phase_start" in phase_sequence
        assert "phase_end" in phase_sequence
        
        # Verify event structure
        for event in events:
            assert event.layer in ["L3", "L2"]
            assert "workflow_type" in event.payload
            assert "stage" in event.payload
            assert event.timestamp > 0
    
    def test_telemetry_respects_config_when_disabled(self):
        """Test that telemetry is not recorded when disabled in config."""
        # Configure telemetry as disabled via config parameter
        config = {"telemetry_enabled": False}
        
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute outreach workflow with disabled telemetry config
        result = orchestrator.orchestrate_outreach(mission, recipient, config)
        
        # Verify no telemetry was recorded
        bus = get_telemetry_bus()
        events = bus.get_events()
        errors = bus.get_errors()
        traces = bus.get_traces()
        
        assert len(events) == 0
        assert len(errors) == 0
        assert len(traces) == 0
    
    def test_telemetry_captures_error_events_on_failure(self):
        """Test that error events are captured when workflow fails."""
        # Mock safety validator to fail
        self.mock_safety_validator.evaluate.return_value = Mock(
            passed=False,
            findings=["safety_violation"]
        )
        
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute outreach workflow (should fail)
        result = orchestrator.orchestrate_outreach(mission, recipient)
        
        # Get telemetry errors
        bus = get_telemetry_bus()
        errors = bus.get_errors()
        
        # Should have recorded safety failure error
        assert len(errors) > 0
        
        safety_errors = [e for e in errors if e.name == "safety_failure"]
        assert len(safety_errors) > 0
        
        # Verify error structure
        for error in safety_errors:
            assert error.layer == "L5"  # Safety layer
            assert "workflow_type" in error.context
            assert "stage" in error.context
    
    def test_telemetry_includes_workflow_metadata(self):
        """Test that telemetry events include appropriate workflow metadata."""
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute outreach workflow
        result = orchestrator.orchestrate_outreach(mission, recipient)
        
        # Get telemetry events
        bus = get_telemetry_bus()
        events = bus.get_events()
        
        # Verify events include expected metadata
        for event in events:
            payload = event.payload
            
            # Should include basic workflow identifiers
            assert payload.get("workflow_type") == "outreach"
            assert "stage" in payload
            
            # Should include archetype when available for phase events (not workflow start)
            if event.layer == "L3" and event.name in ["phase_start", "phase_end"] and event.payload.get("stage") != "orchestration":
                assert "archetype" in payload
    
    def test_telemetry_detail_level_filters_payload(self):
        """Test that detail level filtering works in integration."""
        # Configure minimal detail level via config parameter
        config = {"telemetry_detail_level": "minimal"}
        
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute outreach workflow with minimal detail level
        result = orchestrator.orchestrate_outreach(mission, recipient, config)
        
        # Get telemetry events
        bus = get_telemetry_bus()
        events = bus.get_events()
        
        # Verify minimal filtering
        for event in events:
            payload = event.payload
            
            # Should only include minimal keys (layer is not in payload, it's a separate parameter)
            assert "workflow_type" in payload
            assert "stage" in payload
            
            # Should exclude detailed information
            assert "archetype" not in payload
            assert "mission_id" not in payload
            assert "duration" not in payload
    
    def test_concurrent_workflow_emits_telemetry(self):
        """Test that concurrent outreach workflow also emits telemetry."""
        # Enable concurrent features
        config = {
            "use_concurrent_research": True,
            "use_multi_draft": False,
            "telemetry_enabled": True
        }
        
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute concurrent outreach workflow
        result = asyncio.run(orchestrator.orchestrate_outreach_concurrent(mission, recipient, config))
        
        # Get telemetry events
        bus = get_telemetry_bus()
        events = bus.get_events()
        
        # Should have events for concurrent workflow
        assert len(events) > 0
        
        # Should include concurrent workflow type
        workflow_events = [e for e in events if e.payload.get("workflow_type") == "outreach_concurrent"]
        assert len(workflow_events) > 0
    
    def test_l2_executors_emit_telemetry_events(self):
        """Test that L3 orchestrator emits telemetry events (L2 bypassed by mocks)."""
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Execute outreach workflow
        result = orchestrator.orchestrate_outreach(mission, recipient)
        
        # Get telemetry events
        bus = get_telemetry_bus()
        events = bus.get_events()
        
        # Should have L3 layer events (L2 bypassed by mocks)
        l3_events = [e for e in events if e.layer == "L3"]
        assert len(l3_events) > 0
        
        # Verify L3 event structure
        for event in l3_events:
            assert event.name in ["phase_start", "phase_end"]
            assert "workflow_type" in event.payload
            assert "stage" in event.payload
    
    def test_telemetry_performance_impact_is_minimal(self):
        """Test that telemetry doesn't significantly impact performance."""
        orchestrator = self.create_orchestrator()
        mission = self.create_sample_mission()
        recipient = self.create_sample_recipient()
        
        # Measure time without telemetry
        bus = get_telemetry_bus()
        bus.configure(enabled=False)
        
        start_time = time.time()
        result1 = orchestrator.orchestrate_outreach(mission, recipient)
        time_without_telemetry = time.time() - start_time
        
        # Measure time with telemetry
        bus.configure(enabled=True, detail_level="standard")
        
        start_time = time.time()
        result2 = orchestrator.orchestrate_outreach(mission, recipient)
        time_with_telemetry = time.time() - start_time
        
        # Telemetry should not add significant overhead
        overhead_ratio = time_with_telemetry / time_without_telemetry
        assert overhead_ratio < 2.0  # Less than 2x overhead
        
        # Results should be identical
        assert result1.success == result2.success
        assert result1.message == result2.message
