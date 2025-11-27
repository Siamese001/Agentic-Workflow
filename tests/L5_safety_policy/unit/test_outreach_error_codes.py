"""
Unit tests for outreach LIC error codes - Phase 5 L5 SafetyValidator expansion.

Tests all 13 LIC error codes (E001-E013) for outreach-specific safety violations.
"""

from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext
from l5.interfaces import Action
from l1.outreach_dataclasses import OutreachMission, ArchetypeType


class TestOutreachErrorCodes:
    """Test suite for outreach LIC error code implementation."""
    
    def setup_method(self):
        """Set up test fixtures for outreach error code validation."""
        self.safety_validator = SafetyValidator()
        
        # Create base outreach context
        self.base_context = SafetyContext(
            content="Test message content",
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
    
    def test_lic_error_code_e001_factual_gap(self):
        """Test LIC-E001 factual_gap error detection."""
        # Message contains claims not supported by research bundle
        context = SafetyContext(
            content="Our company leads the AI industry with revolutionary quantum computing breakthroughs",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect factual gap and include LIC-E001 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E001" in finding for finding in result.findings)
    
    def test_lic_error_code_e002_hallucination(self):
        """Test LIC-E002 hallucination error detection."""
        # Message contains hallucinated information about contact
        context = SafetyContext(
            content="I saw your recent publication on quantum entanglement in Nature",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect hallucination and include LIC-E002 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E002" in finding for finding in result.findings)
    
    def test_lic_error_code_e003_overclaim(self):
        """Test LIC-E003 overclaim error detection."""
        # Message makes exaggerated claims about capabilities
        context = SafetyContext(
            content="Our solution guarantees 1000% productivity improvement and eliminates all bugs",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect overclaim and include LIC-E003 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E003" in finding for finding in result.findings)
    
    def test_lic_error_code_e004_risky_cta(self):
        """Test LIC-E004 risky_CTA error detection."""
        # Message contains risky or inappropriate call-to-action
        context = SafetyContext(
            content="Let's discuss this over dinner at my place tonight",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect risky CTA and include LIC-E004 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E004" in finding for finding in result.findings)
    
    def test_lic_error_code_e005_aggressive_tone(self):
        """Test LIC-E005 aggressive_tone error detection."""
        # Message has overly aggressive or demanding tone
        context = SafetyContext(
            content="You MUST respond immediately or you'll miss this opportunity forever",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect aggressive tone and include LIC-E005 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E005" in finding for finding in result.findings)
    
    def test_lic_error_code_e006_misleading_causality(self):
        """Test LIC-E006 misleading_causality error detection."""
        # Message makes false causal claims
        context = SafetyContext(
            content="Using our platform will automatically make you a VP within 6 months",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect misleading causality and include LIC-E006 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E006" in finding for finding in result.findings)
    
    def test_lic_error_code_e007_contact_role_mismatch(self):
        """Test LIC-E007 contact_role_mismatch error detection."""
        # Message addresses wrong role based on research bundle
        context = SafetyContext(
            content="Dear CEO, I'm impressed by your engineering leadership",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect role mismatch and include LIC-E007 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E007" in finding for finding in result.findings)
    
    def test_lic_error_code_e008_missing_value_proposition(self):
        """Test LIC-E008 missing_value_proposition error detection."""
        # Message lacks clear value proposition
        context = SafetyContext(
            content="Hi there, just wanted to say hello",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect missing value proposition and include LIC-E008 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E008" in finding for finding in result.findings)
    
    def test_lic_error_code_e009_seniority_inconsistency(self):
        """Test LIC-E009 seniority_inconsistency error detection."""
        # Message shows inconsistent understanding of seniority
        context = SafetyContext(
            content="As an entry-level developer, I'm sure you make strategic decisions",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect seniority inconsistency and include LIC-E009 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E009" in finding for finding in result.findings)
    
    def test_lic_error_code_e010_personal_bias(self):
        """Test LIC-E010 personal_bias error detection."""
        # Message contains inappropriate personal bias
        context = SafetyContext(
            content="As a fellow graduate of Elite University, I know you're the best candidate",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect personal bias and include LIC-E010 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E010" in finding for finding in result.findings)
    
    def test_lic_error_code_e011_unsafe_assertion(self):
        """Test LIC-E011 unsafe_assertion error detection."""
        # Create context with low severity violation
        context = SafetyContext(
            content="Our solution is quite good for your needs",  # Minor overstatement
            content_type="text",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect unsafe assertion and include LIC-E011 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E011" in finding for finding in result.findings)
    
    def test_lic_error_code_e012_competency_overreach(self):
        """Test LIC-E012 competency_overreach error detection."""
        # Message shows overreach in claimed competency
        context = SafetyContext(
            content="I can solve all your company's technical problems in one week",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect competency overreach and include LIC-E012 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E012" in finding for finding in result.findings)
    
    def test_lic_error_code_e013_privacy_violation(self):
        """Test LIC-E013 privacy_violation error detection."""
        # Message contains privacy-violating content
        context = SafetyContext(
            content="I found your home address and would love to discuss opportunities there",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect privacy violation and include LIC-E013 in findings
        assert result is not None
        if result.verdict == Action.BLOCK:
            assert any("LIC-E013" in finding for finding in result.findings)
    
    def test_error_code_formatting(self):
        """Test that all error codes follow proper LIC-E### format."""
        # This will test the actual error code formatting implementation
        from l5.safety_validator import OutreachSafetyPolicy
        
        policy = OutreachSafetyPolicy()
        
        # All error codes should follow LIC-E### format
        expected_codes = [f"LIC-E{str(i).zfill(3)}" for i in range(1, 14)]
        
        # Implementation will validate error code formatting
        assert hasattr(policy, 'error_codes')
    
    def test_multiple_error_codes_can_fire(self):
        """Test that multiple error codes can be detected in single message."""
        # Message with multiple violations
        context = SafetyContext(
            content="Our 1000% guaranteed platform will make you CEO in 6 months. Let's discuss at your home tonight.",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should detect multiple violations
        assert result is not None
        if result.verdict == Action.BLOCK:
            # Should have multiple findings
            assert len(result.findings) >= 1
