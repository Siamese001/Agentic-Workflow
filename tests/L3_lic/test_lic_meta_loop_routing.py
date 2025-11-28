"""Tests for LIC meta-loop router - L3 orchestration layer."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, call
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from l3.lic_meta_loop import (
    LICMetaLoopRouter,
    LICMetaLoopConfig,
    LICFallbackHop,
    LICMetaLoopOutcome,
    OutreachContext,
    LICFailureInfo,
    LICFailureClassifier,
    LICCircuitBreaker,
    OutreachOrchestratorInterface,
)
from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext


@pytest.fixture
def mock_safety_validator():
    """Mock safety validator."""
    validator = MagicMock(spec=SafetyValidator)
    return validator


@pytest.fixture
def mock_failure_classifier():
    """Mock failure classifier."""
    classifier = AsyncMock(spec=LICFailureClassifier)
    return classifier


@pytest.fixture
def mock_outreach_orchestrator():
    """Mock outreach orchestrator."""
    orchestrator = AsyncMock(spec=OutreachOrchestratorInterface)
    return orchestrator


@pytest.fixture
def mock_circuit_breaker():
    """Mock circuit breaker."""
    breaker = AsyncMock(spec=LICCircuitBreaker)
    breaker.check_can_attempt.return_value = True
    return breaker


@pytest.fixture
def mock_telemetry_bus():
    """Mock telemetry bus."""
    bus = MagicMock()
    bus.record_event = MagicMock()
    return bus


@pytest.fixture
def sample_outreach_context():
    """Sample outreach context for testing."""
    return OutreachContext(
        recipient_profile={"name": "John Doe", "title": "Engineering Manager"},
        company_data={"name": "TechCorp", "industry": "Software"},
        mission="Recruit for Senior Engineer position",
        target_archetype="EXECUTIVE",
        metadata={"test": True},
    )


@pytest.fixture
def lic_meta_loop_router(
    mock_safety_validator,
    mock_failure_classifier,
    mock_outreach_orchestrator,
    mock_circuit_breaker,
    mock_telemetry_bus,
):
    """LIC meta-loop router fixture."""
    config = LICMetaLoopConfig(
        archetype_order=["EXECUTIVE", "SENIOR_TA", "RECRUITER"],
        max_retries_per_archetype=2,
        max_total_attempts=6,
        enable_circuit_breaker=True,
    )
    
    return LICMetaLoopRouter(
        safety_validator=mock_safety_validator,
        failure_classifier=mock_failure_classifier,
        outreach_orchestrator=mock_outreach_orchestrator,
        circuit_breaker=mock_circuit_breaker,
        config=config,
        telemetry_bus=mock_telemetry_bus,
    )


class TestLICMetaLoopRouter:
    """Test suite for LIC meta-loop router."""
    
    @pytest.mark.asyncio
    async def test_exec_success_no_fallback(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test successful EXECUTIVE archetype with no fallback."""
        # Mock successful message generation
        mock_outreach_orchestrator.run_for_archetype.return_value = "Hello, I'm recruiting..."
        
        # Mock safety pass
        mock_safety_result = MagicMock()
        mock_safety_result.passes = True
        mock_safety_result.severity = "LOW"
        mock_safety_validator.evaluate.return_value = mock_safety_result
        
        # Mock failure classification (success case)
        mock_failure_classifier.classify.return_value = LICFailureInfo(
            failure_type="none",
            should_retry=False,
            should_fallback=False,
            escalation_level="ALLOW",
            metadata={},
        )
        
        # Run meta-loop
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions
        assert result.success is True
        assert result.final_archetype == "EXECUTIVE"
        assert result.final_message == "Hello, I'm recruiting..."
        assert result.failure_type == "none"
        assert result.escalation_level == "ALLOW"
        assert result.attempts_total == 1
        assert len(result.fallback_chain) == 0
        
        # Verify orchestrator called once for EXECUTIVE only
        mock_outreach_orchestrator.run_for_archetype.assert_called_once_with(
            context=sample_outreach_context,
            archetype="EXECUTIVE",
        )
    
    @pytest.mark.asyncio
    async def test_creative_failure_triggers_fallback_to_senior_ta(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test creative failure triggers fallback from EXECUTIVE to SENIOR_TA."""
        # Mock EXECUTIVE message generation
        mock_outreach_orchestrator.run_for_archetype.return_value = "Weak executive message"
        
        # Mock safety failure
        mock_safety_result = MagicMock()
        mock_safety_result.passes = False
        mock_safety_result.severity = "MEDIUM"
        mock_safety_validator.evaluate.return_value = mock_safety_result
        
        # Mock creative failure classification with fallback
        mock_failure_classifier.classify.return_value = LICFailureInfo(
            failure_type="creative",
            should_retry=False,
            should_fallback=True,
            escalation_level="REQUIRE_APPROVAL",
            metadata={"creative_weakness": True},
        )
        
        # Mock SENIOR_TA success
        senior_ta_message = "Better senior TA message"
        mock_safety_result_pass = MagicMock()
        mock_safety_result_pass.passes = True
        mock_safety_result_pass.severity = "LOW"
        
        def mock_orchestrator_side_effect(context, archetype):
            if archetype == "SENIOR_TA":
                return senior_ta_message
            return "Weak executive message"
        
        def mock_safety_side_effect(safety_context):
            if "SENIOR_TA" in str(safety_context.metadata):
                return mock_safety_result_pass
            return mock_safety_result
        
        def mock_failure_side_effect(message, safety_result, outreach_context, archetype):
            if archetype == "SENIOR_TA":
                return LICFailureInfo(
                    failure_type="none",
                    should_retry=False,
                    should_fallback=False,
                    escalation_level="ALLOW",
                    metadata={},
                )
            return LICFailureInfo(
                failure_type="creative",
                should_retry=False,
                should_fallback=True,
                escalation_level="REQUIRE_APPROVAL",
                metadata={"creative_weakness": True},
            )
        
        mock_outreach_orchestrator.run_for_archetype.side_effect = mock_orchestrator_side_effect
        mock_safety_validator.evaluate.side_effect = mock_safety_side_effect
        mock_failure_classifier.classify.side_effect = mock_failure_side_effect
        
        # Run meta-loop
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions
        assert result.success is True
        assert result.final_archetype == "SENIOR_TA"
        assert result.final_message == senior_ta_message
        assert result.failure_type == "none"
        assert result.escalation_level == "ALLOW"
        assert result.attempts_total == 2
        
        # Verify fallback chain
        assert len(result.fallback_chain) == 1
        hop = result.fallback_chain[0]
        assert hop.from_archetype == "EXECUTIVE"
        assert hop.to_archetype == "SENIOR_TA"
        assert hop.failure_type == "creative"
        assert hop.reason == "Fallback: creative"
        
        # Verify both archetypes were attempted
        assert mock_outreach_orchestrator.run_for_archetype.call_count == 2
        calls = mock_outreach_orchestrator.run_for_archetype.call_args_list
        assert calls[0][1]["archetype"] == "EXECUTIVE"
        assert calls[1][1]["archetype"] == "SENIOR_TA"
    
    @pytest.mark.asyncio
    async def test_factual_failure_triggers_block(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test factual failure triggers immediate block."""
        # Mock message generation
        mock_outreach_orchestrator.run_for_archetype.return_value = "Factually incorrect message"
        
        # Mock safety failure
        mock_safety_result = MagicMock()
        mock_safety_result.passes = False
        mock_safety_result.severity = "HIGH"
        mock_safety_validator.evaluate.return_value = mock_safety_result
        
        # Mock factual failure classification with block
        mock_failure_classifier.classify.return_value = LICFailureInfo(
            failure_type="factual",
            should_retry=False,
            should_fallback=False,
            escalation_level="BLOCK",
            metadata={"factual_error": True},
        )
        
        # Run meta-loop
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions
        assert result.success is False
        assert result.final_archetype == "EXECUTIVE"
        assert result.final_message is None
        assert result.failure_type == "factual"
        assert result.escalation_level == "BLOCK"
        assert result.attempts_total == 1
        
        # Verify fallback chain has terminal block hop
        assert len(result.fallback_chain) == 1
        hop = result.fallback_chain[0]
        assert hop.from_archetype == "EXECUTIVE"
        assert hop.to_archetype is None
        assert hop.failure_type == "factual"
        assert hop.reason == "Block escalation: factual"
        
        # Verify only one attempt was made
        mock_outreach_orchestrator.run_for_archetype.assert_called_once_with(
            context=sample_outreach_context,
            archetype="EXECUTIVE",
        )
    
    @pytest.mark.asyncio
    async def test_retry_within_archetype_respects_limits(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test retry logic respects max_retries_per_archetype limit."""
        # Mock message generation
        mock_outreach_orchestrator.run_for_archetype.return_value = "Retryable message"
        
        # Mock safety failure
        mock_safety_result = MagicMock()
        mock_safety_result.passes = False
        mock_safety_result.severity = "MEDIUM"
        mock_safety_validator.evaluate.return_value = mock_safety_result
        
        # Mock failure classification with retry (then fallback)
        retry_count = 0
        def mock_failure_side_effect(message, safety_result, outreach_context, archetype):
            if archetype == "SENIOR_TA":
                return LICFailureInfo(
                    failure_type="none",
                    should_retry=False,
                    should_fallback=False,
                    escalation_level="ALLOW",
                    metadata={},
                )
            # EXECUTIVE retry logic
            nonlocal retry_count
            retry_count += 1
            if retry_count == 1:  # First attempt: retry
                return LICFailureInfo(
                    failure_type="creative",
                    should_retry=True,
                    should_fallback=False,
                    escalation_level="REQUIRE_APPROVAL",
                    metadata={},
                )
            else:  # Second attempt: fallback (after retry exhausted)
                return LICFailureInfo(
                    failure_type="creative",
                    should_retry=False,
                    should_fallback=True,
                    escalation_level="REQUIRE_APPROVAL",
                    metadata={},
                )
        
        mock_failure_classifier.classify.side_effect = mock_failure_side_effect
        
        # Mock SENIOR_TA success
        senior_ta_message = "Final successful message"
        mock_safety_result_pass = MagicMock()
        mock_safety_result_pass.passes = True
        mock_safety_result_pass.severity = "LOW"
        
        def mock_orchestrator_side_effect(context, archetype):
            if archetype == "SENIOR_TA":
                return senior_ta_message
            return "Retryable message"
        
        def mock_safety_side_effect(safety_context):
            if "SENIOR_TA" in str(safety_context.metadata):
                return mock_safety_result_pass
            return mock_safety_result
        
        mock_outreach_orchestrator.run_for_archetype.side_effect = mock_orchestrator_side_effect
        mock_safety_validator.evaluate.side_effect = mock_safety_side_effect
        
        # Run meta-loop
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions
        assert result.success is True
        assert result.final_archetype == "SENIOR_TA"
        assert result.final_message == senior_ta_message
        assert result.attempts_total == 3  # 2 retries + 1 fallback attempt
        
        # Verify EXECUTIVE attempted 2 times (max_retries_per_archetype)
        exec_calls = [call for call in mock_outreach_orchestrator.run_for_archetype.call_args_list 
                     if call[1]["archetype"] == "EXECUTIVE"]
        assert len(exec_calls) == 2
        
        # Verify fallback chain
        assert len(result.fallback_chain) == 1
        hop = result.fallback_chain[0]
        assert hop.attempts_used == 2
        assert hop.reason == "Fallback: creative"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_blocks_when_open(
        self,
        mock_safety_validator,
        mock_failure_classifier,
        mock_outreach_orchestrator,
        mock_circuit_breaker,
        mock_telemetry_bus,
        sample_outreach_context,
    ):
        """Test circuit breaker blocks attempts when open."""
        # Configure circuit breaker to be open
        mock_circuit_breaker.check_can_attempt.return_value = False
        
        # Create router with circuit breaker enabled
        config = LICMetaLoopConfig(
            archetype_order=["EXECUTIVE", "SENIOR_TA", "RECRUITER"],
            max_retries_per_archetype=2,
            max_total_attempts=6,
            enable_circuit_breaker=True,
        )
        
        router = LICMetaLoopRouter(
            safety_validator=mock_safety_validator,
            failure_classifier=mock_failure_classifier,
            outreach_orchestrator=mock_outreach_orchestrator,
            circuit_breaker=mock_circuit_breaker,
            config=config,
            telemetry_bus=mock_telemetry_bus,
        )
        
        # Run meta-loop
        result = await router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions
        assert result.success is False
        assert result.failure_type == "safety"
        assert result.escalation_level == "BLOCK"
        assert result.metadata["circuit_breaker_open"] is True
        
        # Verify fallback chain indicates circuit breaker open
        assert len(result.fallback_chain) == 1
        hop = result.fallback_chain[0]
        assert hop.reason == "Circuit breaker open"
        assert hop.failure_type == "safety"
        
        # Verify circuit breaker was checked
        mock_circuit_breaker.check_can_attempt.assert_called_once()
        
        # Verify no message generation attempts were made
        mock_outreach_orchestrator.run_for_archetype.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_metadata_fallback_chain_is_populated(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test fallback chain metadata is properly populated."""
        # Mock multiple failures to build fallback chain
        messages = ["Exec message", "Senior TA message", "Recruiter message"]
        safety_results = [
            MagicMock(passes=False, severity="MEDIUM"),
            MagicMock(passes=False, severity="MEDIUM"),
            MagicMock(passes=True, severity="LOW"),
        ]
        
        failure_infos = [
            LICFailureInfo(
                failure_type="creative",
                should_retry=False,
                should_fallback=True,
                escalation_level="REQUIRE_APPROVAL",
                metadata={"exec_weakness": True},
            ),
            LICFailureInfo(
                failure_type="factual",
                should_retry=False,
                should_fallback=True,
                escalation_level="REQUIRE_APPROVAL",
                metadata={"senior_ta_issue": True},
            ),
            LICFailureInfo(
                failure_type="none",
                should_retry=False,
                should_fallback=False,
                escalation_level="ALLOW",
                metadata={},
            ),
        ]
        
        mock_outreach_orchestrator.run_for_archetype.side_effect = messages
        mock_safety_validator.evaluate.side_effect = safety_results
        mock_failure_classifier.classify.side_effect = failure_infos
        
        # Run meta-loop
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions
        assert result.success is True
        assert result.final_archetype == "RECRUITER"
        assert result.attempts_total == 3
        
        # Verify fallback chain has 2 hops (EXECUTIVE -> SENIOR_TA -> RECRUITER)
        assert len(result.fallback_chain) == 2
        
        # First hop: EXECUTIVE -> SENIOR_TA
        hop1 = result.fallback_chain[0]
        assert hop1.from_archetype == "EXECUTIVE"
        assert hop1.to_archetype == "SENIOR_TA"
        assert hop1.failure_type == "creative"
        assert hop1.attempts_used == 1
        assert hop1.metadata["exec_weakness"] is True
        
        # Second hop: SENIOR_TA -> RECRUITER
        hop2 = result.fallback_chain[1]
        assert hop2.from_archetype == "SENIOR_TA"
        assert hop2.to_archetype == "RECRUITER"
        assert hop2.failure_type == "factual"
        assert hop2.attempts_used == 1
        assert hop2.metadata["senior_ta_issue"] is True
    
    @pytest.mark.asyncio
    async def test_max_total_attempts_respected(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test max_total_attempts is respected across all archetypes."""
        # Configure low total attempt limit
        lic_meta_loop_router.config.max_total_attempts = 2
        
        # Mock continuous failures
        mock_outreach_orchestrator.run_for_archetype.return_value = "Failing message"
        mock_safety_result = MagicMock(passes=False, severity="MEDIUM")
        mock_safety_validator.evaluate.return_value = mock_safety_result
        
        mock_failure_classifier.classify.return_value = LICFailureInfo(
            failure_type="creative",
            should_retry=False,
            should_fallback=True,
            escalation_level="REQUIRE_APPROVAL",
            metadata={},
        )
        
        # Run meta-loop
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="EXECUTIVE",
        )
        
        # Assertions - should stop after 2 attempts total
        assert result.success is False
        assert result.attempts_total == 2
        assert result.metadata["completion_reason"] == "All archetype attempts exhausted"
        
        # Verify only 2 attempts were made
        assert mock_outreach_orchestrator.run_for_archetype.call_count == 2
    
    @pytest.mark.asyncio
    async def test_initial_archetype_not_in_sequence(
        self,
        lic_meta_loop_router,
        mock_outreach_orchestrator,
        mock_safety_validator,
        mock_failure_classifier,
        sample_outreach_context,
    ):
        """Test behavior when initial_archetype is not in configured sequence."""
        # Mock success for first archetype in sequence
        mock_outreach_orchestrator.run_for_archetype.return_value = "Success message"
        mock_safety_result = MagicMock(passes=True, severity="LOW")
        mock_safety_validator.evaluate.return_value = mock_safety_result
        
        mock_failure_classifier.classify.return_value = LICFailureInfo(
            failure_type="none",
            should_retry=False,
            should_fallback=False,
            escalation_level="ALLOW",
            metadata={},
        )
        
        # Run meta-loop with unknown initial archetype
        result = await lic_meta_loop_router.run_meta_loop(
            outreach_context=sample_outreach_context,
            initial_archetype="UNKNOWN_ARCHETYPE",
        )
        
        # Should start with first archetype in sequence (EXECUTIVE)
        assert result.success is True
        assert result.final_archetype == "EXECUTIVE"
        assert result.attempts_total == 1
        
        # Verify EXECUTIVE was used
        mock_outreach_orchestrator.run_for_archetype.assert_called_once_with(
            context=sample_outreach_context,
            archetype="EXECUTIVE",
        )


if __name__ == "__main__":
    pytest.main([__file__])
