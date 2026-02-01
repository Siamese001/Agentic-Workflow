"""
Phase 3 Test Suite: Complex Mixed Agents

Comprehensive testing of Phase 3 complex agents:
- GovernanceShieldDeterministic (60% deterministic)
- Advanced HOP validation scenarios
- Security-critical validation

All tests must pass 100% before Phase 3 commit.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_maintenance.deterministic.GovernanceShieldDeterministic import (
    GovernanceResult,
    GovernanceShieldDeterministic,
)
from agentic_core.L0_maintenance.deterministic.HOPValidationDeterministic import (
    HOP1ProfileDeterministic,
    HOP3DataExtractionDeterministic,
    HOP4ConditionDeterministic,
    HOP6PlaceholderDeterministic,
    HOP7GateDecisionDeterministic,
    HOPValidationDeterministic,
    HOPValidationResult,
)


class TestGovernanceShieldDeterministic:
    """Test Governance Shield Deterministic Layer - 100% pass required."""

    @pytest.fixture
    def validator(self) -> GovernanceShieldDeterministic:
        """Governance shield validator for testing."""
        return GovernanceShieldDeterministic({})

    def test_risk_level_scanning_high(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 1: High risk detection is deterministic."""
        content = "We guarantee results always and promise never to fail"

        result = validator.scan_risk_level(content)

        assert isinstance(result, GovernanceResult)
        assert result.risk_level == "high"
        assert not result.passed

    def test_risk_level_scanning_medium(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 2: Medium risk detection is deterministic."""
        content = "This will likely work and probably succeed usually"

        result = validator.scan_risk_level(content)

        assert result.risk_level in ["medium", "high"]

    def test_risk_level_scanning_low(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 3: Low risk detection is deterministic."""
        content = "Thank you for your interest in our professional services"

        result = validator.scan_risk_level(content)

        assert result.risk_level == "low"
        assert result.passed

    def test_privacy_language_detection(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 4: Privacy language detection is deterministic."""
        content = "Please provide your SSN and credit card number"

        result = validator.detect_privacy_language(content)

        assert not result.passed
        assert result.risk_level in ["medium", "high"]
        assert len(result.issues) > 0

    def test_privacy_clean_content(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 5: Clean content passes privacy check."""
        content = "Thank you for your interest in our services"

        result = validator.detect_privacy_language(content)

        assert result.passed
        assert result.risk_level == "low"

    def test_forbidden_patterns_detection(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 6: Forbidden patterns detection is deterministic."""
        content = "100% money back guarantee, risk free offer"

        result = validator.check_forbidden_patterns(content)

        assert not result.passed
        assert result.risk_level == "high"

    def test_forbidden_patterns_clean(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 7: Clean content passes forbidden patterns check."""
        content = "We offer excellent service with great results"

        result = validator.check_forbidden_patterns(content)

        assert result.passed
        assert result.risk_level == "low"

    def test_safety_protocol_generation_high(
        self, validator: GovernanceShieldDeterministic
    ) -> None:
        """Test 8: High risk protocol generation is deterministic."""
        result = validator.generate_safety_protocol("high", "Test content")

        assert result.passed
        assert result.protocol is not None
        assert "HIGH_RISK" in result.protocol

    def test_safety_protocol_generation_low(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 9: Low risk protocol generation is deterministic."""
        result = validator.generate_safety_protocol("low", "Test content")

        assert result.passed
        assert result.protocol is not None
        assert "LOW_RISK" in result.protocol

    def test_comprehensive_audit(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 10: Comprehensive audit combines all checks."""
        content = "We guarantee 100% success always"

        result = validator.audit_content_compliance(content)

        assert isinstance(result, GovernanceResult)
        assert result.risk_level in ["high", "medium", "low"]
        assert result.score is not None

    def test_claim_sanitization(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 11: Claim sanitization is deterministic."""
        content = "We always guarantee perfect results"

        result = validator.sanitize_claims(content)

        assert isinstance(result, GovernanceResult)
        assert len(result.issues) > 0  # Should have sanitizations

    def test_clean_content_audit(self, validator: GovernanceShieldDeterministic) -> None:
        """Test 12: Clean content passes comprehensive audit."""
        content = "We offer professional services with excellent support"

        result = validator.audit_content_compliance(content)

        assert result.passed
        assert result.risk_level == "low"


class TestHOPValidationAdvanced:
    """Test HOP Validation Advanced Scenarios - 100% pass required."""

    def test_hop1_incomplete_profile(self) -> None:
        """Test 1: HOP1 handles incomplete profiles correctly."""
        config = {
            "industry_keywords": {"tech": ["software", "developer"]},
            "seniority_keywords": {"senior": ["senior", "lead"]},
            "min_profile_completeness": 0.75,
        }

        validator = HOP1ProfileDeterministic(config)
        incomplete_profile = {"name": "John"}

        result = validator.classify_profile_heuristic(incomplete_profile)

        assert not result.passed
        assert any("completeness" in issue.lower() for issue in result.issues)

    def test_hop1_complete_profile(self) -> None:
        """Test 2: HOP1 validates complete profiles correctly."""
        config = {
            "industry_keywords": {"tech": ["software", "developer"]},
            "seniority_keywords": {"senior": ["senior", "lead"]},
            "min_profile_completeness": 0.5,
        }

        validator = HOP1ProfileDeterministic(config)
        complete_profile = {
            "name": "John Doe",
            "experience": ["Senior Software Developer"],
            "education": ["CS Degree"],
            "skills": ["Python"],
        }

        result = validator.classify_profile_heuristic(complete_profile)

        assert result.passed
        assert result.score is not None

    def test_hop3_missing_entities(self) -> None:
        """Test 3: HOP3 detects missing required entities."""
        config = {"required_entities": ["name", "email", "company"], "entity_patterns": {}}

        validator = HOP3DataExtractionDeterministic(config)
        incomplete_data = {"name": "John"}

        result = validator.extract_grounded_entities(incomplete_data)

        assert not result.passed
        assert any("email" in issue for issue in result.issues)
        assert any("company" in issue for issue in result.issues)

    def test_hop3_complete_entities(self) -> None:
        """Test 4: HOP3 validates complete entities correctly."""
        config = {"required_entities": ["name", "email"], "entity_patterns": {}}

        validator = HOP3DataExtractionDeterministic(config)
        complete_data = {"name": "John", "email": "john@example.com"}

        result = validator.extract_grounded_entities(complete_data)

        assert result.passed
        assert result.score == 1.0

    def test_hop4_failing_conditions(self) -> None:
        """Test 5: HOP4 detects failing conditions."""
        config = {
            "conditions": [
                {"name": "has_email", "type": "equals", "field": "has_email", "value": True},
                {"name": "score_check", "type": "greater_than", "field": "score", "value": 0.5},
            ]
        }

        validator = HOP4ConditionDeterministic(config)
        context = {"has_email": False, "score": 0.3}

        result = validator.check_conditions(context)

        assert not result.passed
        assert len(result.issues) == 2

    def test_hop4_passing_conditions(self) -> None:
        """Test 6: HOP4 validates passing conditions correctly."""
        config = {
            "conditions": [
                {"name": "has_email", "type": "equals", "field": "has_email", "value": True},
            ]
        }

        validator = HOP4ConditionDeterministic(config)
        context = {"has_email": True}

        result = validator.check_conditions(context)

        assert result.passed
        assert result.score == 1.0

    def test_hop6_multiple_placeholders(self) -> None:
        """Test 7: HOP6 detects multiple placeholder types."""
        config = {"placeholder_patterns": [r"\[.*?\]", r"\{.*?\}", r"<.*?>"]}

        validator = HOP6PlaceholderDeterministic(config)
        content = "Hello [Name], welcome to {Company} at <Location>"

        result = validator.validate_placeholders(content)

        assert not result.passed
        assert len(result.metadata["placeholders"]) == 3

    def test_hop6_clean_content(self) -> None:
        """Test 8: HOP6 validates clean content correctly."""
        config = {"placeholder_patterns": [r"\[.*?\]", r"\{.*?\}"]}

        validator = HOP6PlaceholderDeterministic(config)
        content = "Hello John, welcome to Acme Corp"

        result = validator.validate_placeholders(content)

        assert result.passed
        assert result.score == 1.0

    def test_hop7_reject_decision(self) -> None:
        """Test 9: HOP7 makes reject decision correctly."""
        config = {
            "violation_categories": {},
            "decision_thresholds": {"critical": {"critical": 1, "retry": 0}},
        }

        validator = HOP7GateDecisionDeterministic(config)
        violations = [{"category": "critical"}, {"category": "critical"}]

        result = validator.classify_gate_decision(violations)

        assert not result.passed
        assert result.classification == "reject"

    def test_hop7_proceed_decision(self) -> None:
        """Test 10: HOP7 makes proceed decision correctly."""
        config = {
            "violation_categories": {},
            "decision_thresholds": {"critical": {"critical": 5, "retry": 3}},
        }

        validator = HOP7GateDecisionDeterministic(config)
        violations = []

        result = validator.classify_gate_decision(violations)

        assert result.passed
        assert result.classification == "proceed"


class TestPhase3Integration:
    """Integration tests for Phase 3 components."""

    def test_governance_and_hop_combined(self) -> None:
        """Test 1: Governance and HOP validators work together."""
        governance = GovernanceShieldDeterministic({})
        hop_config = {
            "hop1": {"industry_keywords": {}, "seniority_keywords": {}},
            "hop3": {"required_entities": []},
            "hop4": {"conditions": []},
            "hop6": {"placeholder_patterns": []},
            "hop7": {"violation_categories": {}, "decision_thresholds": {}},
        }
        hop = HOPValidationDeterministic(hop_config)

        content = "Professional content here"
        gov_result = governance.audit_content_compliance(content)
        hop6_result = hop.validate_hop6_placeholders(content)

        assert isinstance(gov_result, GovernanceResult)
        assert isinstance(hop6_result, HOPValidationResult)

    def test_security_validation_pipeline(self) -> None:
        """Test 2: Security validation pipeline works correctly."""
        validator = GovernanceShieldDeterministic({})

        # Step 1: Risk scan
        risk_result = validator.scan_risk_level("Professional content")
        assert risk_result.risk_level == "low"

        # Step 2: Privacy check
        privacy_result = validator.detect_privacy_language("Professional content")
        assert privacy_result.passed

        # Step 3: Forbidden patterns
        forbidden_result = validator.check_forbidden_patterns("Professional content")
        assert forbidden_result.passed

    def test_deterministic_consistency(self) -> None:
        """Test 3: All validators produce consistent results."""
        validator = GovernanceShieldDeterministic({})
        content = "We offer excellent professional services"

        results = [validator.audit_content_compliance(content) for _ in range(10)]

        first_result = results[0]
        for result in results[1:]:
            assert result.passed == first_result.passed
            assert result.risk_level == first_result.risk_level

    def test_performance_benchmark(self) -> None:
        """Test 4: Validators perform within acceptable time."""
        import time

        validator = GovernanceShieldDeterministic({})
        content = "Test content for performance benchmark " * 10

        start_time = time.time()
        for _ in range(100):
            validator.audit_content_compliance(content)
        end_time = time.time()

        assert (end_time - start_time) < 2.0


def test_phase3_execution_summary() -> None:
    """Summary: All Phase 3 tests validate complex agent behavior."""
    print("=" * 60)
    print("Phase 3 Test Suite Summary")
    print("=" * 60)
    print("✅ GovernanceShieldDeterministic: 12 tests")
    print("✅ HOPValidationAdvanced: 10 tests")
    print("✅ Phase3Integration: 4 tests")
    print("-" * 60)
    print("Total: 26 tests")
    print("=" * 60)
