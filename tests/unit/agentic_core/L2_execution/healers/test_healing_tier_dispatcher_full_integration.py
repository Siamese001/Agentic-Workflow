"""Tests for healing_tier_dispatcher full meta-learning integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    dispatch_healing,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
)
from system_learning.engines.default_healing_pattern_advisor import (
    DefaultHealingPatternAdvisor,
)
from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
from system_learning.ports.healing_pattern_advisor import (
    NullHealingPatternAdvisor,
)
from system_learning.ports.meta_outcome_bus_hook import (
    NullMetaOutcomeBusHook,
)
from system_learning.ports.meta_prior_provider import (
    NeutralMetaPriorProvider,
)
from system_learning.ports.outcome_write_back_hook import (
    DefaultOutcomeWriteBackHook,
    NullOutcomeWriteBackHook,
)


class MockMetaPriorProvider:
    """Mock provider with configurable priors."""

    def __init__(self, priors: dict[str, float]) -> None:
        self._priors = priors

    def get_prior(self, error_signature: str) -> float:
        return self._priors.get(error_signature, 0.50)


class MockHealingProviderInvoker:
    """Mock invoker that always succeeds."""

    def invoke_local(self, healing_input, decision, config, agent_name=""):
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import InvocationRecord

        return InvocationRecord(
            tier=decision.tier,
            method_called="invoke_local",
            model_id="",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
        )


def test_full_integration_all_phases() -> None:
    """Full integration of all meta-learning phases."""
    # Phase 1: Meta prior provider
    meta_prior_provider = MockMetaPriorProvider({"test_sig": 0.90})

    # Phase 2: Outcome write-back hook
    store = HealingSuccessRateStore()
    outcome_write_back_hook = DefaultOutcomeWriteBackHook(store)

    # Phase 3: Pattern advisor
    mock_ml_client = MagicMock()
    mock_patterns = [
        {
            "pattern_id": "pattern_1",
            "pattern_name": "test_pattern",
            "confidence_boost": 0.08,
            "description": "Test pattern",
        },
    ]
    mock_ml_client.retrieve_healing_patterns.return_value = mock_patterns
    pattern_advisor = DefaultHealingPatternAdvisor(mock_ml_client)

    # Phase 4: Meta outcome bus hook (mock the hook directly to assert publish_outcome)
    mock_bus_hook = MagicMock()

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=meta_prior_provider,
        outcome_write_back_hook=outcome_write_back_hook,
        pattern_advisor=pattern_advisor,
        meta_outcome_bus_hook=mock_bus_hook,
    )

    # Phase 1: Should have used meta prior in routing
    assert decision.tier in HealingTier
    assert any("historical_success_rate=0.9000" in code for code in decision.reason_codes)

    # Phase 2: Should have recorded outcome in store
    assert store.get_counts().get("test_sig", 0) == 1

    # Phase 3: Should have queried ML client for patterns
    mock_ml_client.retrieve_healing_patterns.assert_called_once_with(error_signature="test_sig")

    # Phase 4: Should have published outcome to meta bus
    mock_bus_hook.publish_outcome.assert_called_once()

    # Should have successful invocation record
    assert record.tier == decision.tier


def test_full_integration_with_null_hooks() -> None:
    """Full integration works with all null hooks."""
    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=NeutralMetaPriorProvider(),
        outcome_write_back_hook=NullOutcomeWriteBackHook(),
        pattern_advisor=NullHealingPatternAdvisor(),
        meta_outcome_bus_hook=NullMetaOutcomeBusHook(),
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_full_integration_hooks_fail_gracefully() -> None:
    """All hooks fail gracefully without affecting dispatch."""
    failing_outcome_hook = MagicMock()
    failing_outcome_hook.on_outcome.side_effect = Exception("Outcome hook failed")

    failing_pattern_advisor = MagicMock()
    failing_pattern_advisor.advise.side_effect = Exception("Pattern advisor failed")

    failing_bus_hook = MagicMock()
    failing_bus_hook.publish_outcome.side_effect = Exception("Bus hook failed")

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    with patch("system_learning.engines.default_healing_pattern_advisor.logger"):
        with patch("system_learning.ports.meta_outcome_bus_hook.logger"):
            decision, record = dispatch_healing(
                healing_input,
                config,
                invoker=invoker,
                agent_name="test-agent",
                timestamp_utc=1234567890,
                outcome_write_back_hook=failing_outcome_hook,
                pattern_advisor=failing_pattern_advisor,
                meta_outcome_bus_hook=failing_bus_hook,
            )

    # Should still succeed despite hook failures
    assert decision.tier in HealingTier
    assert record.tier == decision.tier

    # All hooks should have been called
    failing_outcome_hook.on_outcome.assert_called_once()
    failing_pattern_advisor.advise.assert_called_once()
    failing_bus_hook.publish_outcome.assert_called_once()


def test_full_integration_invocation_failure() -> None:
    """Hooks are called even when invocation fails."""

    class FailingInvoker:
        def invoke_local(self, healing_input, decision, config, agent_name=""):
            raise Exception("Invocation failed")

    store = HealingSuccessRateStore()
    outcome_hook = DefaultOutcomeWriteBackHook(store)
    mock_bus_hook = MagicMock()

    config = HealingTierConfig()
    invoker = FailingInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should raise invocation exception
    with pytest.raises(Exception, match="Invocation failed"):
        dispatch_healing(
            healing_input,
            config,
            invoker=invoker,
            agent_name="test-agent",
            timestamp_utc=1234567890,
            outcome_write_back_hook=outcome_hook,
            meta_outcome_bus_hook=mock_bus_hook,
        )

    # Hooks should still have been called with failure info
    assert store.get_counts().get("test_sig", 0) == 1
    mock_bus_hook.publish_outcome.assert_called_once()


def test_full_integration_backward_compatibility() -> None:
    """Full integration works without any meta-learning components."""
    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    # Should work with all hooks as None
    decision, record = dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        meta_prior_provider=None,
        outcome_write_back_hook=None,
        pattern_advisor=None,
        meta_outcome_bus_hook=None,
    )

    assert decision.tier in HealingTier
    assert record.tier == decision.tier


def test_full_integration_phase_order() -> None:
    """Hooks are called in correct order: outcome -> pattern -> bus."""
    call_order = []

    def track_call(name):
        def wrapper(*args, **kwargs):
            call_order.append(name)

        return wrapper

    outcome_hook = MagicMock()
    outcome_hook.on_outcome = track_call("outcome")

    pattern_advisor = MagicMock()
    pattern_advisor.advise = MagicMock(
        return_value={
            "pattern_match": False,
            "pattern_name": None,
            "pattern_boost": 0.0,
            "extra_reason_codes": (),
        }
    )
    pattern_advisor.advise = track_call("pattern")

    bus_hook = MagicMock()
    bus_hook.publish_outcome = track_call("bus")

    config = HealingTierConfig()
    invoker = MockHealingProviderInvoker()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
    )

    dispatch_healing(
        healing_input,
        config,
        invoker=invoker,
        agent_name="test-agent",
        timestamp_utc=1234567890,
        outcome_write_back_hook=outcome_hook,
        pattern_advisor=pattern_advisor,
        meta_outcome_bus_hook=bus_hook,
    )

    # Should be called in order: outcome -> pattern -> bus
    assert call_order == ["outcome", "pattern", "bus"]
