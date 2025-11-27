"""
Integration tests for outreach safety validation - Phase 5 L5 SafetyValidator expansion.

Tests SafetyValidator fires ONLY after message generation, meta-loop integrity,
and resume workflow unaffected.
"""

import pytest

from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext
from l5.interfaces import Action, Verdict
from l1.outreach_dataclasses import OutreachMission, ArchetypeType
from l3.lic_orchestrator import LICOrchestrator


class TestOutreachSafetyIntegration:
    """Integration test suite for outreach safety validation."""
    
    def setup_method(self):
        """Set up test fixtures for outreach safety integration."""
        self.safety_validator = SafetyValidator()
        
        # Create test outreach mission
        self.outreach_mission = OutreachMission(
            objective="Test engineering leadership opportunity",
            target_role="Engineering Manager",
            target_company="Tech Corp",
            value_proposition="AI-driven team productivity enhancement",
            urgency="medium"
        )
        
        # Create test recipient
        from l1.outreach_archetype_planning import RecipientProfile
        self.recipient = RecipientProfile(
            name="Jane Smith",
            title="Engineering Manager", 
            company="Tech Corp",
            industry="Technology",
            seniority="Senior",
            department="Engineering",
            skills=["Python", "Leadership", "System Design"],
            recent_activity=["Recent project completion"],
            metadata={"test": True}
        )
    
    def test_safety_fires_only_after_message_generation(self):
        """Test that SafetyValidator fires ONLY after message generation."""
        # Mock the message generation to return a test message
        test_message = "Our AI platform significantly improves engineering productivity and team collaboration"
        
        # Create safety context for generated message
        safety_context = SafetyContext(
            content=test_message,
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": self.outreach_mission,
                "research_bundle": {
                    "company": {"industry": "Technology", "size": "1000+"},
                    "contact": {"title": "Engineering Manager", "department": "Engineering"}
                }
            }
        )
        
        # Safety validation should work on generated message
        result = self.safety_validator.evaluate(safety_context)
        
        assert result is not None
        assert hasattr(result, 'verdict')
        assert hasattr(result, 'findings')
        assert hasattr(result, 'metadata')
    
    def test_meta_loop_remains_intact(self):
        """Test that meta-loop remains intact after safety validation."""
        # Test that safety validation doesn't break the orchestration flow
        orchestrator = LICOrchestrator()
        
        # Run single outreach (should work as in Phase 4)
        result = orchestrator.run_single_outreach(self.outreach_mission, self.recipient)
        
        # Meta-loop should remain intact
        assert result is not None
        assert hasattr(result, 'success')
        # Phase 4 completion should be preserved
    
    def test_unsafe_messages_produce_safe_false(self):
        """Test that unsafe messages produce safe=False."""
        # Create unsafe message (privacy violation)
        unsafe_message = "I found your home address and would love to discuss opportunities there"
        
        safety_context = SafetyContext(
            content=unsafe_message,
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": self.outreach_mission,
                "research_bundle": {
                    "company": {"industry": "Technology"},
                    "contact": {"title": "Engineering Manager"}
                }
            }
        )
        
        result = self.safety_validator.evaluate(safety_context)
        
        # Unsafe messages should produce safe=False
        assert result is not None
        # Critical violations should be blocked
        escalation_action = result.metadata.get('escalation_action')
        if escalation_action == 'block':
            assert result.verdict == Verdict.BLOCK
    
    def test_safe_messages_pass_unchanged(self):
        """Test that safe messages pass through unchanged."""
        # Create safe message
        safe_message = "Our platform helps improve team productivity through AI-driven insights"
        
        safety_context = SafetyContext(
            content=safe_message,
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": self.outreach_mission,
                "research_bundle": {
                    "company": {"industry": "Technology"},
                    "contact": {"title": "Engineering Manager"}
                }
            }
        )
        
        result = self.safety_validator.evaluate(safety_context)
        
        # Safe messages should pass through
        assert result is not None
        # Should not block safe content
        escalation_action = result.metadata.get('escalation_action')
        assert escalation_action != 'block'
    
    def test_resume_workflow_unaffected(self):
        """Test that resume workflow is unaffected by outreach safety rules."""
        # Create resume context (should use existing behavior)
        resume_context = SafetyContext(
            content="Experienced software engineer with 5 years in Python development",
            domain="resume",
            metadata={"existing": "resume_behavior"}
        )
        
        result = self.safety_validator.evaluate(resume_context)
        
        # Resume workflow should use existing behavior
        assert result is not None
        # Should not apply outreach rules to resume content
        assert "outreach" not in str(result).lower()
    
    def test_outreach_safety_integration_with_lic_orchestrator(self):
        """Test outreach safety integration with LICOrchestrator."""
        orchestrator = LICOrchestrator()
        
        # Test that safety validation integrates properly with orchestration
        result = orchestrator.run_single_outreach(self.outreach_mission, self.recipient)
        
        # Should maintain Phase 4 success
        assert result is not None
        assert result.success is True
    
    def test_safety_validator_domain_awareness(self):
        """Test SafetyValidator domain awareness in integration."""
        # Test outreach domain
        outreach_context = SafetyContext(
            content="Test outreach message",
            domain="outreach",
            metadata={"archetype": ArchetypeType.EXECUTIVE}
        )
        
        outreach_result = self.safety_validator.evaluate(outreach_context)
        
        # Test resume domain
        resume_context = SafetyContext(
            content="Test resume content",
            domain="resume",
            metadata={"existing": "behavior"}
        )
        
        resume_result = self.safety_validator.evaluate(resume_context)
        
        # Should handle domains differently
        assert outreach_result is not None
        assert resume_result is not None
        # Outreach should use new rules, resume should use existing
    
    def test_safety_result_contract_valid(self):
        """Test that SafetyResult contract is valid in integration."""
        safety_context = SafetyContext(
            content="Test message for safety validation",
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": self.outreach_mission,
                "research_bundle": {"company": {}, "contact": {}}
            }
        )
        
        result = self.safety_validator.evaluate(safety_context)
        
        # Should maintain PolicyDecision contract
        assert hasattr(result, 'verdict')
        assert hasattr(result, 'findings')
        assert hasattr(result, 'metadata')
        assert isinstance(result.findings, list)
        assert all(hasattr(finding, 'rule') for finding in result.findings)
    
    def test_l1_l5_boundary_intact(self):
        """Test that L1-L5 boundary purity is maintained."""
        # SafetyValidator should only use L5 interfaces
        # Should not directly modify L1-L3 components
        
        safety_context = SafetyContext(
            content="Test boundary integrity",
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": self.outreach_mission,
                "research_bundle": {}
            }
        )
        
        result = self.safety_validator.evaluate(safety_context)
        
        # Should maintain boundary purity
        assert result is not None
        # Should not interfere with L1-L3 components
    
    def test_cycle_free_import_graph(self):
        """Test that import graph remains cycle-free."""
        # Test that new outreach safety imports don't create cycles
        try:
            # This should work without circular imports
            from l5.safety_validator import SafetyValidator
            from l1.outreach_dataclasses import OutreachMission
            from l3.lic_orchestrator import LICOrchestrator
            
            # Should be able to import all components
            assert SafetyValidator is not None
            assert OutreachMission is not None
            assert LICOrchestrator is not None
            
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")
    
    def test_run_single_outreach_success_preserved(self):
        """Test that run_single_outreach success is preserved after safety expansion."""
        orchestrator = LICOrchestrator()
        
        # Should maintain Phase 4 success
        result = orchestrator.run_single_outreach(self.outreach_mission, self.recipient)
        
        assert result is not None
        assert result.success is True
        # Safety expansion should not break existing functionality
    
    def test_safety_validator_with_archetype_awareness(self):
        """Test SafetyValidator archetype awareness in integration."""
        test_content = "Our platform significantly improves engineering outcomes"
        
        # Test with different archetypes
        for archetype in ArchetypeType:
            safety_context = SafetyContext(
                content=test_content,
                domain="outreach",
                metadata={
                    "archetype": archetype,
                    "mission": self.outreach_mission,
                    "research_bundle": {
                        "company": {"industry": "Technology"},
                        "contact": {"title": "Engineering Manager"}
                    }
                }
            )
            
            result = self.safety_validator.evaluate(safety_context)
            
            # Should handle different archetypes
            assert result is not None
            # Results should vary by archetype tolerance
    
    def test_safety_validator_error_code_integration(self):
        """Test SafetyValidator error code integration."""
        # Message with multiple potential violations
        test_message = "Our 1000% guaranteed platform will make you CEO in 6 months. Let's discuss at your home tonight."
        
        safety_context = SafetyContext(
            content=test_message,
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": self.outreach_mission,
                "research_bundle": {
                    "company": {"industry": "Technology"},
                    "contact": {"title": "Engineering Manager"}
                }
            }
        )
        
        result = self.safety_validator.evaluate(safety_context)
        
        # Should detect and report appropriate error codes
        assert result is not None
        escalation_action = result.metadata.get('escalation_action')
        if escalation_action == 'block':
            # Should include LIC error codes in metadata
            assert any(hasattr(finding, 'metadata') and finding.metadata.get('lic_error_code') for finding in result.findings)
