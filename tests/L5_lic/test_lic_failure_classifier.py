"""Tests for LIC Failure Classifier - L5 policy engine."""

import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass
from typing import Any, Dict

from l5.lic_failure_classifier import (
    LICFailureClassifier,
    LICFailureClassifierConfig,
)
from l5.safety_validator import SafetyResult, SafetyViolation, Severity


@pytest.fixture
def mock_telemetry_bus():
    """Mock telemetry bus."""
    bus = MagicMock()
    bus.record_event = MagicMock()
    return bus


@pytest.fixture
def default_config():
    """Default classifier configuration."""
    return LICFailureClassifierConfig()


@pytest.fixture
def lic_failure_classifier(default_config, mock_telemetry_bus):
    """LIC failure classifier fixture."""
    return LICFailureClassifier(
        config=default_config,
        telemetry_bus=mock_telemetry_bus,
    )


@pytest.fixture
def sample_outreach_context():
    """Sample outreach context for testing."""
    @dataclass
    class OutreachContext:
        recipient_profile: Dict[str, Any]
        company_data: Dict[str, Any]
        mission: str
        target_archetype: str
        metadata: Dict[str, Any]
    
    return OutreachContext(
        recipient_profile={"name": "John Doe"},
        company_data={"name": "TechCorp"},
        mission="Test mission",
        target_archetype="EXECUTIVE",
        metadata={"test": True},
    )


@pytest.fixture
def safety_result_pass():
    """Safety result that passes validation."""
    return SafetyResult(
        passes=True,
        violations=[],
        severity="LOW",
        metadata={},
    )


@pytest.fixture
def safety_result_creative_violation():
    """Safety result with creative violation."""
    violation = SafetyViolation(
        code="C001",
        message="Creative weakness detected",
        severity=Severity.MEDIUM,
        category="style",
        metadata={"failure_type_hint": "creative"},
    )
    return SafetyResult(
        passes=False,
        violations=[violation],
        severity="MEDIUM",
        metadata={},
    )


@pytest.fixture
def safety_result_factual_violation():
    """Safety result with factual violation."""
    violation = SafetyViolation(
        code="F001",
        message="Factual error detected",
        severity=Severity.HIGH,
        category="accuracy",
        metadata={"failure_type_hint": "factual"},
    )
    return SafetyResult(
        passes=False,
        violations=[violation],
        severity="HIGH",
        metadata={},
    )


@pytest.fixture
def safety_result_safety_violation():
    """Safety result with safety violation."""
    violation = SafetyViolation(
        code="S001",
        message="Safety violation detected",
        severity=Severity.CRITICAL,
        category="safety",
        metadata={},
    )
    return SafetyResult(
        passes=False,
        violations=[violation],
        severity="CRITICAL",
        metadata={},
    )


class TestLICFailureClassifier:
    """Test suite for LIC failure classifier."""
    
    @pytest.mark.asyncio
    async def test_no_violations_yields_none_allow(
        self,
        lic_failure_classifier,
        safety_result_pass,
        sample_outreach_context,
    ):
        """Test that no violations yields failure_type='none' and escalation='ALLOW'."""
        result = await lic_failure_classifier.classify(
            message="Perfect message",
            safety_result=safety_result_pass,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        assert result.failure_type == "none"
        assert result.escalation_level == "ALLOW"
        assert result.should_retry is False
        assert result.should_fallback is False
        assert result.attempt_index_for_archetype == 1
        assert result.metadata["violation_codes"] == []
        assert result.metadata["severity"] == "LOW"
    
    @pytest.mark.asyncio
    async def test_creative_low_severity_allows_retry_then_fallback(
        self,
        lic_failure_classifier,
        safety_result_creative_violation,
        sample_outreach_context,
    ):
        """Test creative low severity allows retry then fallback after limit."""
        # First attempt - should retry
        result = await lic_failure_classifier.classify(
            message="Weak creative message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",  # More tolerant
            attempt_index_for_archetype=1,
        )
        
        assert result.failure_type == "creative"
        assert result.escalation_level == "REQUIRE_APPROVAL"
        assert result.should_retry is True  # Within retry limit
        assert result.should_fallback is False
        assert result.metadata["effective_creative_retry_limit"] == 2  # RECRUITER gets +1
        
        # Second attempt - should still retry
        result = await lic_failure_classifier.classify(
            message="Still weak creative message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",
            attempt_index_for_archetype=2,
        )
        
        assert result.should_retry is True
        assert result.should_fallback is False
        
        # Third attempt - should fallback (exceeds limit)
        result = await lic_failure_classifier.classify(
            message="Still weak creative message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",
            attempt_index_for_archetype=3,
        )
        
        assert result.should_retry is False
        assert result.should_fallback is True
    
    @pytest.mark.asyncio
    async def test_creative_high_severity_requires_approval_or_block(
        self,
        lic_failure_classifier,
        sample_outreach_context,
    ):
        """Test creative high severity requires approval or blocks."""
        # Create high severity creative violation
        violation = SafetyViolation(
            code="C002",
            message="Major creative weakness",
            severity=Severity.HIGH,
            category="style",
            metadata={"failure_type_hint": "creative"},
        )
        safety_result = SafetyResult(
            passes=False,
            violations=[violation],
            severity="HIGH",
            metadata={},
        )
        
        result = await lic_failure_classifier.classify(
            message="Poor creative message",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        assert result.failure_type == "creative"
        assert result.escalation_level == "REQUIRE_APPROVAL"
        assert result.should_retry is False  # EXECUTIVE gets -1 retry limit (0)
        assert result.should_fallback is True
    
    @pytest.mark.asyncio
    async def test_factual_high_severity_blocks_immediately(
        self,
        lic_failure_classifier,
        safety_result_factual_violation,
        sample_outreach_context,
    ):
        """Test factual high severity blocks immediately."""
        result = await lic_failure_classifier.classify(
            message="Factually incorrect message",
            safety_result=safety_result_factual_violation,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        assert result.failure_type == "factual"
        assert result.escalation_level == "BLOCK"  # HIGH >= config.factual_block_severity_min
        assert result.should_retry is False
        assert result.should_fallback is False
        assert result.metadata["violation_codes"] == ["F001"]
    
    @pytest.mark.asyncio
    async def test_factual_low_severity_respects_retry_limit(
        self,
        lic_failure_classifier,
        sample_outreach_context,
    ):
        """Test factual low severity respects retry limit."""
        # Create low severity factual violation
        violation = SafetyViolation(
            code="F002",
            message="Minor factual issue",
            severity=Severity.MEDIUM,
            category="accuracy",
            metadata={"failure_type_hint": "factual"},
        )
        safety_result = SafetyResult(
            passes=False,
            violations=[violation],
            severity="MEDIUM",
            metadata={},
        )
        
        # Configure factual retry limit
        config = LICFailureClassifierConfig(
            factual_retry_limit=2,
            factual_block_severity_min="HIGH",
            default_escalation_for_factual="REQUIRE_APPROVAL",  # Allow fallback for low-severity factual
        )
        classifier = LICFailureClassifier(config=config)
        
        # First attempt - should retry
        result = await classifier.classify(
            message="Slightly inaccurate message",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",
            attempt_index_for_archetype=1,
        )
        
        assert result.failure_type == "factual"
        assert result.escalation_level == "REQUIRE_APPROVAL"  # Low severity factual doesn't block
        assert result.should_retry is True  # Within retry limit
        assert result.should_fallback is False
        
        # Second attempt - should still retry
        result = await classifier.classify(
            message="Still slightly inaccurate",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",
            attempt_index_for_archetype=2,
        )
        
        assert result.should_retry is True
        assert result.should_fallback is False
        
        # Third attempt - should not retry
        result = await classifier.classify(
            message="Still slightly inaccurate",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",
            attempt_index_for_archetype=3,
        )
        
        assert result.should_retry is False
        assert result.should_fallback is True
    
    @pytest.mark.asyncio
    async def test_safety_critical_blocks_without_retry(
        self,
        lic_failure_classifier,
        safety_result_safety_violation,
        sample_outreach_context,
    ):
        """Test safety critical violations block without retry."""
        result = await lic_failure_classifier.classify(
            message="Unsafe message",
            safety_result=safety_result_safety_violation,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        assert result.failure_type == "safety"
        assert result.escalation_level == "BLOCK"  # CRITICAL >= config.safety_block_severity_min
        assert result.should_retry is False
        assert result.should_fallback is False
        assert result.metadata["violation_codes"] == ["S001"]
    
    @pytest.mark.asyncio
    async def test_archetype_specific_behavior_exec_vs_recruiter(
        self,
        lic_failure_classifier,
        safety_result_creative_violation,
        sample_outreach_context,
    ):
        """Test archetype-specific behavior differences."""
        # EXECUTIVE - more strict on creative (fewer retries)
        exec_result = await lic_failure_classifier.classify(
            message="Weak creative message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        # RECRUITER - more tolerant on creative (more retries)
        recruiter_result = await lic_failure_classifier.classify(
            message="Weak creative message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="RECRUITER",
            attempt_index_for_archetype=1,
        )
        
        # EXECUTIVE should have lower retry limit
        assert exec_result.metadata["effective_creative_retry_limit"] == 0
        assert recruiter_result.metadata["effective_creative_retry_limit"] == 2
        
        # EXECUTIVE should fallback immediately, RECRUITER should retry
        assert exec_result.should_retry is False
        assert exec_result.should_fallback is True
        
        assert recruiter_result.should_retry is True
        assert recruiter_result.should_fallback is False
    
    @pytest.mark.asyncio
    async def test_metadata_contains_violation_codes_and_limits(
        self,
        lic_failure_classifier,
        safety_result_creative_violation,
        sample_outreach_context,
    ):
        """Test metadata contains violation codes and retry limits."""
        result = await lic_failure_classifier.classify(
            message="Test message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="SENIOR_TA",
            attempt_index_for_archetype=1,
        )
        
        # Verify required metadata fields
        assert "violation_codes" in result.metadata
        assert "severity" in result.metadata
        assert "effective_creative_retry_limit" in result.metadata
        assert "effective_factual_retry_limit" in result.metadata
        assert "archetype" in result.metadata
        assert "message_length" in result.metadata
        
        # Verify values
        assert result.metadata["violation_codes"] == ["C001"]
        assert result.metadata["severity"] == "MEDIUM"
        assert result.metadata["effective_creative_retry_limit"] == 1  # Base limit
        assert result.metadata["effective_factual_retry_limit"] == 0  # SENIOR_TA strict on factual
        assert result.metadata["archetype"] == "SENIOR_TA"
        assert result.metadata["message_length"] == len("Test message")
    
    @pytest.mark.asyncio
    async def test_failure_type_precedence_order(
        self,
        lic_failure_classifier,
        sample_outreach_context,
    ):
        """Test failure type determination follows correct precedence."""
        # Create violations with multiple hints - factual should take precedence
        violations = [
            SafetyViolation(
                code="C001",
                message="Creative issue",
                severity=Severity.MEDIUM,
                category="style",
                metadata={"failure_type_hint": "creative"},
            ),
            SafetyViolation(
                code="F001",
                message="Factual issue",
                severity=Severity.HIGH,
                category="accuracy",
                metadata={"failure_type_hint": "factual"},
            ),
        ]
        safety_result = SafetyResult(
            passes=False,
            violations=violations,
            severity="HIGH",
            metadata={},
        )
        
        result = await lic_failure_classifier.classify(
            message="Message with multiple issues",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        # Factual should take precedence over creative
        assert result.failure_type == "factual"
        assert result.metadata["violation_codes"] == ["C001", "F001"]
    
    @pytest.mark.asyncio
    async def test_safety_category_overrides_creative_hint(
        self,
        lic_failure_classifier,
        sample_outreach_context,
    ):
        """Test safety category takes precedence over creative hint."""
        violation = SafetyViolation(
            code="S001",
            message="Safety issue with creative hint",
            severity=Severity.HIGH,
            category="safety",
            metadata={"failure_type_hint": "creative"},  # Should be ignored
        )
        safety_result = SafetyResult(
            passes=False,
            violations=[violation],
            severity="HIGH",
            metadata={},
        )
        
        result = await lic_failure_classifier.classify(
            message="Safety violation message",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        # Safety category should override creative hint
        assert result.failure_type == "safety"
    
    @pytest.mark.asyncio
    async def test_metadata_fallback_type(
        self,
        lic_failure_classifier,
        sample_outreach_context,
    ):
        """Test failure type from SafetyResult metadata when no violation hints."""
        violation = SafetyViolation(
            code="O001",
            message="Generic violation",
            severity=Severity.MEDIUM,
            category="other",
            metadata={},
        )
        safety_result = SafetyResult(
            passes=False,
            violations=[violation],
            severity="MEDIUM",
            metadata={"failure_type": "creative"},
        )
        
        result = await lic_failure_classifier.classify(
            message="Message with metadata failure type",
            safety_result=safety_result,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        # Should use metadata failure type
        assert result.failure_type == "creative"
    
    @pytest.mark.asyncio
    async def test_telemetry_recording(
        self,
        lic_failure_classifier,
        safety_result_creative_violation,
        sample_outreach_context,
        mock_telemetry_bus,
    ):
        """Test telemetry is recorded correctly."""
        await lic_failure_classifier.classify(
            message="Test message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        # Verify telemetry was recorded
        mock_telemetry_bus.record_event.assert_called_once_with(
            "lic_failure_classification",
            layer="L5",
            payload={
                "archetype": "EXECUTIVE",
                "failure_type": "creative",
                "escalation_level": "REQUIRE_APPROVAL",
                "should_retry": False,
                "should_fallback": True,
                "attempt_index_for_archetype": 1,
            },
        )
    
    @pytest.mark.asyncio
    async def test_telemetry_error_handling(
        self,
        lic_failure_classifier,
        safety_result_creative_violation,
        sample_outreach_context,
    ):
        """Test telemetry errors don't break classification."""
        # Make telemetry bus raise exceptions
        lic_failure_classifier.telemetry_bus.record_event.side_effect = Exception("Telemetry failed")
        
        # Classification should still work despite telemetry failure
        result = await lic_failure_classifier.classify(
            message="Test message",
            safety_result=safety_result_creative_violation,
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            attempt_index_for_archetype=1,
        )
        
        # Should still produce valid classification
        assert result.failure_type == "creative"
        assert result.escalation_level == "REQUIRE_APPROVAL"
    
    @pytest.mark.asyncio
    async def test_default_configuration(
        self,
        mock_telemetry_bus,
        sample_outreach_context,
    ):
        """Test classifier works with default configuration."""
        classifier = LICFailureClassifier(telemetry_bus=mock_telemetry_bus)
        
        # Verify default config values
        assert classifier.config.factual_block_severity_min == "HIGH"
        assert classifier.config.safety_block_severity_min == "HIGH"
        assert classifier.config.creative_retry_limit == 1
        assert classifier.config.factual_retry_limit == 0
        assert classifier.config.default_escalation_for_creative == "REQUIRE_APPROVAL"
        assert classifier.config.default_escalation_for_factual == "BLOCK"
        assert classifier.config.default_escalation_for_safety == "BLOCK"
        assert classifier.config.default_escalation_for_other == "REQUIRE_APPROVAL"


if __name__ == "__main__":
    pytest.main([__file__])
