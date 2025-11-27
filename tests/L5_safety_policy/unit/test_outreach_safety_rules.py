"""
Unit tests for outreach safety rules - Phase 5 L5 SafetyValidator expansion.

Tests domain-aware routing and outreach-specific constraint categories.
"""

from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext
from l5.interfaces import Verdict
from l1.outreach_dataclasses import OutreachMission, ArchetypeType


class TestOutreachSafetyRules:
    """Test suite for outreach safety rule implementation."""
    
    def setup_method(self):
        """Set up test fixtures for outreach safety validation."""
        self.safety_validator = SafetyValidator()
        
        # Create test outreach context
        self.outreach_context = SafetyContext(
            content="Test outreach message content",
            content_type="text",
            domain="outreach",
            metadata={
                "archetype": ArchetypeType.EXECUTIVE,
                "mission": OutreachMission(
                    objective="Test mission",
                    target_role="Engineering Manager",
                    target_company="Test Company",
                    value_proposition="Technology leadership",
                    urgency="medium"
                ),
                "research_bundle": {
                    "company": {"industry": "Technology", "size": "1000+"},
                    "contact": {"title": "Engineering Manager", "department": "Engineering"}
                }
            }
        )
        
        # Create test resume context (should use existing behavior)
        self.resume_context = SafetyContext(
            content="Test resume content",
            content_type="text",
            domain="resume",
            metadata={"existing": "behavior"}
        )
    
    def test_domain_gating_blocks_non_outreach_content(self):
        """Test that outreach safety rules only apply to outreach domain."""
        # Resume context should not trigger outreach rules
        result = self.safety_validator.evaluate(self.resume_context)
        
        # Should use existing resume behavior
        assert result.verdict != Verdict.BLOCK
        assert "outreach" not in str(result).lower()
    
    def test_domain_gating_allows_outreach_content(self):
        """Test that outreach domain triggers outreach safety rules."""
        # Outreach context should trigger outreach rules
        result = self.safety_validator.evaluate(self.outreach_context)
        
        # Should process through outreach safety logic
        assert result is not None
        assert hasattr(result, 'verdict')
    
    def test_outreach_constraint_categories_exist(self):
        """Test that outreach constraint categories are properly defined."""
        # This will test the actual implementation once created
        from l5.safety_validator import OutreachSafetyPolicy
        
        policy = OutreachSafetyPolicy()
        
        # Should have outreach-specific constraint categories (error codes)
        expected_error_codes = [
            "LIC-E001", "LIC-E002", "LIC-E003", "LIC-E004", "LIC-E005",
            "LIC-E006", "LIC-E007", "LIC-E008", "LIC-E009", "LIC-E010", 
            "LIC-E011", "LIC-E012", "LIC-E013"
        ]
        
        # Implementation should have all error codes
        assert hasattr(policy, 'constraints')
        constraints = policy.constraints
        for error_code in expected_error_codes:
            assert error_code in constraints, f"Missing error code: {error_code}"
    
    def test_outreach_safety_policy_initialization(self):
        """Test OutreachSafetyPolicy can be initialized properly."""
        from l5.safety_validator import OutreachSafetyPolicy
        
        policy = OutreachSafetyPolicy()
        
        assert policy is not None
        assert hasattr(policy, 'evaluate')
        assert hasattr(policy, 'policy_id')
    
    def test_safety_result_structure_validation(self):
        """Test that SafetyResult structure is maintained for outreach."""
        # Test that outreach safety validation returns proper PolicyDecision
        result = self.safety_validator.evaluate(self.outreach_context)
        
        # Should maintain PolicyDecision contract
        assert hasattr(result, 'verdict')
        assert hasattr(result, 'findings')
        assert isinstance(result.findings, list)
    
    def test_layer_applicability_respect(self):
        """Test that outreach safety rules respect L5 boundary purity."""
        # Outreach safety should not interfere with other layers
        result = self.safety_validator.evaluate(self.outreach_context)
        
        # Should be L5-only operation
        assert result is not None
        # Additional boundary checks will be added with implementation
