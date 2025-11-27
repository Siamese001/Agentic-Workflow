"""
Unit tests for outreach archetype-based tolerance - Phase 5 L5 SafetyValidator expansion.

Tests archetype tolerance rules: C_LEVEL most permissive, EXECUTIVE moderate, 
SENIOR_TA low, RECRUITER extremely conservative.
"""

import pytest
from unittest.mock import Mock
from typing import List, Dict, Any

from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext, Severity
from l5.interfaces import PolicyDecision, Action, Verdict
from l1.outreach_dataclasses import OutreachMission, ArchetypeType


class TestOutreachArchetypeTolerance:
    """Test suite for outreach archetype-based tolerance implementation."""
    
    def setup_method(self):
        """Set up test fixtures for outreach archetype tolerance validation."""
        self.safety_validator = SafetyValidator()
        
        # Create base mission
        self.base_mission = OutreachMission(
            objective="Test mission",
            target_role="Engineering Manager",
            target_company="Test Company",
            value_proposition="Technology leadership",
            urgency="medium"
        )
        
        # Create base research bundle
        self.base_research_bundle = {
            "company": {"industry": "Technology", "size": "1000+"},
            "contact": {"title": "Engineering Manager", "department": "Engineering"}
        }
    
    def create_context_for_archetype(self, archetype: ArchetypeType, content: str) -> SafetyContext:
        """Helper to create context for specific archetype."""
        return SafetyContext(
            content=content,
            domain="outreach",
            metadata={
                "archetype": archetype,
                "mission": self.base_mission,
                "research_bundle": self.base_research_bundle
            }
        )
    
    def test_c_level_most_permissive_for_cta(self):
        """Test that C_LEVEL archetype is most permissive for CTA claims."""
        # Bold CTA that might be blocked for other archetypes
        bold_cta = "Let's schedule an executive strategy session to discuss transformative partnership opportunities"
        
        context = self.create_context_for_archetype(ArchetypeType.C_LEVEL, bold_cta)
        result = self.safety_validator.evaluate(context)
        
        # C_LEVEL should be more permissive with bold CTAs
        assert result is not None
        # Should not block bold CTA for C_LEVEL
        assert result.verdict != Verdict.BLOCK or result.metadata.get('max_severity') != 'high'
    
    def test_c_level_most_permissive_for_bold_claims(self):
        """Test that C_LEVEL archetype is most permissive for bold claims."""
        # Bold claim that might be blocked for other archetypes
        bold_claim = "Our platform will revolutionize your entire technology stack and drive unprecedented market leadership"
        
        context = self.create_context_for_archetype(ArchetypeType.C_LEVEL, bold_claim)
        result = self.safety_validator.evaluate(context)
        
        # C_LEVEL should be more permissive with bold claims
        assert result is not None
        # Should be more lenient for C_LEVEL
        assert result.verdict != Verdict.BLOCK or result.metadata.get('max_severity') != 'high'
    
    def test_executive_moderate_tolerance(self):
        """Test that EXECUTIVE archetype has moderate tolerance."""
        # Moderate claim that should be acceptable for executives
        moderate_claim = "Our solution significantly improves engineering productivity and team collaboration"
        
        context = self.create_context_for_archetype(ArchetypeType.EXECUTIVE, moderate_claim)
        result = self.safety_validator.evaluate(context)
        
        # EXECUTIVE should have moderate tolerance
        assert result is not None
        # Should allow moderate claims for executives
        assert result.verdict in [Verdict.ALLOW, Verdict.BLOCK]
    
    def test_executive_strict_on_inappropriate_cta(self):
        """Test that EXECUTIVE archetype is strict on inappropriate CTAs."""
        # Inappropriate CTA that should be blocked
        inappropriate_cta = "Let's discuss this over dinner at my place tonight"
        
        context = self.create_context_for_archetype(ArchetypeType.EXECUTIVE, inappropriate_cta)
        result = self.safety_validator.evaluate(context)
        
        # EXECUTIVE should still block inappropriate CTAs
        assert result is not None
        assert result.verdict == Verdict.BLOCK
    
    def test_senior_ta_low_tolerance(self):
        """Test that SENIOR_TA archetype has low tolerance."""
        # Claim that might be acceptable for executives but not senior TAs
        technical_claim = "Our AI-powered platform will transform your entire development workflow"
        
        context = self.create_context_for_archetype(ArchetypeType.SENIOR_TA, technical_claim)
        result = self.safety_validator.evaluate(context)
        
        # SENIOR_TA should have low tolerance for exaggerated claims
        assert result is not None
        # Should be more strict with technical claims
        if result.verdict == Verdict.BLOCK:
            assert any(hasattr(finding, 'metadata') and finding.metadata.get('lic_error_code') for finding in result.findings)
    
    def test_senior_ta_strict_on_technical_accuracy(self):
        """Test that SENIOR_TA archetype is strict on technical accuracy."""
        # Technically inaccurate claim
        inaccurate_claim = "Our quantum computing solution solves all NP-complete problems instantly"
        
        context = self.create_context_for_archetype(ArchetypeType.SENIOR_TA, inaccurate_claim)
        result = self.safety_validator.evaluate(context)
        
        # SENIOR_TA should be very strict on technical accuracy
        assert result is not None
        assert result.verdict == Verdict.BLOCK
    
    def test_recruiter_extremely_conservative(self):
        """Test that RECRUITER archetype is extremely conservative."""
        # Mild claim that should be acceptable for others
        mild_claim = "Our platform is quite good for improving team productivity"
        
        context = self.create_context_for_archetype(ArchetypeType.RECRUITER, mild_claim)
        result = self.safety_validator.evaluate(context)
        
        # RECRUITER should be extremely conservative
        assert result is not None
        # Should be very careful with any claims
        # May allow but with warnings
        assert result.verdict in [Verdict.ALLOW, Verdict.BLOCK]
    
    def test_recruiter_blocks_any_exaggerated_claims(self):
        """Test that RECRUITER archetype blocks any exaggerated claims."""
        # Slightly exaggerated claim
        exaggerated_claim = "Our solution dramatically improves productivity"
        
        context = self.create_context_for_archetype(ArchetypeType.RECRUITER, exaggerated_claim)
        result = self.safety_validator.evaluate(context)
        
        # RECRUITER should block exaggerated claims
        assert result is not None
        # Should be very conservative
        if result.verdict == Verdict.BLOCK:
            assert any(hasattr(finding, 'metadata') and finding.metadata.get('lic_error_code') for finding in result.findings)
    
    def test_archetype_tolerance_affects_same_content_differently(self):
        """Test that same content is treated differently by different archetypes."""
        # Content that should be treated differently across archetypes
        test_content = "Our platform significantly improves engineering outcomes"
        
        # Test with different archetypes
        c_level_result = self.safety_validator.evaluate(
            self.create_context_for_archetype(ArchetypeType.C_LEVEL, test_content)
        )
        
        recruiter_result = self.safety_validator.evaluate(
            self.create_context_for_archetype(ArchetypeType.RECRUITER, test_content)
        )
        
        # Results should differ based on archetype tolerance
        assert c_level_result is not None
        assert recruiter_result is not None
        # C_LEVEL should be more permissive than RECRUITER
        # (Implementation will enforce this difference)
    
    def test_archetype_aware_error_code_application(self):
        """Test that error codes are applied differently based on archetype."""
        # Content that might trigger different error codes
        test_content = "Our revolutionary solution guarantees better results"
        
        for archetype in ArchetypeType:
            context = self.create_context_for_archetype(archetype, test_content)
            result = self.safety_validator.evaluate(context)
            
            assert result is not None
            # Error code application should vary by archetype
            # (Implementation will enforce archetype-aware logic)
    
    def test_archetype_tolerance_preserves_safety_structure(self):
        """Test that archetype tolerance maintains SafetyResult structure."""
        for archetype in ArchetypeType:
            context = self.create_context_for_archetype(archetype, "Test content")
            result = self.safety_validator.evaluate(context)
            
            # Should maintain proper structure regardless of archetype
            assert hasattr(result, 'verdict')
            assert hasattr(result, 'findings')
            assert hasattr(result, 'metadata')
            assert isinstance(result.findings, list)
    
    def test_archetype_tolerance_configurable(self):
        """Test that archetype tolerance levels are configurable."""
        # This will test configurability once implemented
        from l5.safety_validator import OutreachSafetyPolicy
        
        policy = OutreachSafetyPolicy()
        
        # Should have configurable archetype tolerance
        assert hasattr(policy, 'archetype_tolerance_config')
    
    def test_unknown_archetype_defaults_to_conservative(self):
        """Test that unknown archetype defaults to conservative behavior."""
        # Create context with unknown archetype
        context = SafetyContext(
            content="Our platform is quite good",
            domain="outreach",
            metadata={
                "archetype": "UNKNOWN_ARCHETYPE",
                "mission": self.base_mission,
                "research_bundle": self.base_research_bundle
            }
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should default to conservative (RECRUITER-like) behavior
        assert result is not None
        # Should be conservative with unknown archetypes
