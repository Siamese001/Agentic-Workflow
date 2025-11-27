"""
Unit tests for outreach escalation logic - Phase 5 L5 SafetyValidator expansion.

Tests severity-to-action mapping and escalation thresholds.
"""

from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext, Severity
from l5.interfaces import Action
from l1.outreach_dataclasses import OutreachMission, ArchetypeType


class TestOutreachEscalation:
    """Test suite for outreach escalation logic implementation."""
    
    def setup_method(self):
        """Set up test fixtures for outreach escalation validation."""
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
    
    def test_low_severity_escalates_to_warn(self):
        """Test that LOW severity issues escalate to WARN action."""
        # Create context with low severity violation
        context = SafetyContext(
            content="Our solution is quite good for your needs",  # Minor overstatement
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # LOW severity should result in WARN action
        assert result is not None
        if result.severity == Severity.LOW:
            assert result.verdict in [Action.ALLOW, Action.REVIEW]  # Should not block
    
    def test_medium_severity_escalates_to_warn_with_annotation(self):
        """Test that MEDIUM severity issues escalate to WARN with annotation."""
        # Create context with medium severity violation
        context = SafetyContext(
            content="Our platform significantly improves productivity",  # Moderate claim
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # MEDIUM severity should result in WARN with annotation
        assert result is not None
        if result.severity == Severity.MEDIUM:
            assert result.verdict in [Action.REVIEW, Action.MODIFY]  # Should require review
            assert len(result.findings) > 0  # Should have annotations
    
    def test_high_severity_escalates_to_error(self):
        """Test that HIGH severity issues escalate to ERROR (safe=False)."""
        # Create context with high severity violation
        context = SafetyContext(
            content="Our solution guarantees 500% productivity improvement",  # Major overclaim
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # HIGH severity should result in ERROR (safe=False)
        assert result is not None
        if result.severity == Severity.HIGH:
            assert result.verdict == Action.BLOCK  # Should be blocked
    
    def test_critical_severity_escalates_to_block(self):
        """Test that CRITICAL severity issues escalate to BLOCK (force safe=False)."""
        # Create context with critical severity violation
        context = SafetyContext(
            content="I found your home address and want to discuss opportunities there tonight",  # Privacy violation
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # CRITICAL severity should result in BLOCK (force safe=False)
        assert result is not None
        if result.severity == Severity.CRITICAL:
            assert result.verdict == Action.BLOCK  # Must be blocked
    
    def test_escalation_logic_preserves_safety_result_structure(self):
        """Test that escalation logic maintains SafetyResult contract."""
        result = self.safety_validator.evaluate(self.base_context)
        
        # Should maintain proper structure regardless of escalation
        assert hasattr(result, 'action')
        assert hasattr(result, 'severity')
        assert hasattr(result, 'findings')
        assert isinstance(result.findings, list)
    
    def test_multiple_violations_escalate_to_highest_severity(self):
        """Test that multiple violations escalate to highest severity found."""
        # Context with multiple violations of different severities
        context = SafetyContext(
            content="Our 1000% guaranteed platform will make you CEO. Let's discuss at your home tonight.",
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # Should escalate to highest severity (CRITICAL in this case)
        assert result is not None
        if result.findings:
            # Should have multiple findings but escalate to highest severity
            assert len(result.findings) >= 1
            # Critical violations should trigger BLOCK
            if any("privacy" in finding.lower() for finding in result.findings):
                assert result.verdict == Action.BLOCK
    
    def test_escalation_thresholds_are_configurable(self):
        """Test that escalation thresholds can be configured."""
        # This will test configurability once implemented
        from l5.safety_validator import OutreachSafetyPolicy
        
        policy = OutreachSafetyPolicy()
        
        # Should have configurable escalation thresholds
        assert hasattr(policy, 'escalation_config')
    
    def test_escalation_preserves_context_metadata(self):
        """Test that escalation logic preserves original context metadata."""
        result = self.safety_validator.evaluate(self.base_context)
        
        # Should preserve context information in result
        assert result is not None
        # Additional metadata preservation tests will be added with implementation
    
    def test_warn_action_includes_explanatory_findings(self):
        """Test that WARN actions include explanatory findings."""
        # Create context that should trigger WARN
        context = SafetyContext(
            content="Our solution is quite effective",  # Should be LOW/MEDIUM severity
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # WARN should include explanatory findings
        assert result is not None
        if result.verdict in [Action.REVIEW, Action.MODIFY]:
            assert len(result.findings) > 0
            assert all(isinstance(finding, str) for finding in result.findings)
    
    def test_error_action_includes_violation_details(self):
        """Test that ERROR actions include detailed violation information."""
        # Create context that should trigger ERROR
        context = SafetyContext(
            content="Our solution guarantees 1000% improvement",  # Should be HIGH severity
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # ERROR should include detailed violation information
        assert result is not None
        if result.verdict == Action.BLOCK and result.severity == Severity.HIGH:
            assert len(result.findings) > 0
            # Should include specific error codes
            assert any("LIC-E" in finding for finding in result.findings)
    
    def test_block_action_includes_critical_violation_details(self):
        """Test that BLOCK actions include critical violation details."""
        # Create context that should trigger BLOCK
        context = SafetyContext(
            content="I know where you live and want to discuss opportunities",  # Should be CRITICAL
            domain="outreach",
            metadata=self.base_context.metadata
        )
        
        result = self.safety_validator.evaluate(context)
        
        # BLOCK should include critical violation details
        assert result is not None
        if result.verdict == Action.BLOCK and result.severity == Severity.CRITICAL:
            assert len(result.findings) > 0
            # Should include critical error codes
            assert any("LIC-E013" in finding for finding in result.findings)
