"""Tests for OutcomeWriteBackHook port (Phase 2)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)
from system_learning.engines.healing_success_rate_store import HealingSuccessRateStore
from system_learning.ports.outcome_write_back_hook import (
    DefaultOutcomeWriteBackHook,
    NullOutcomeWriteBackHook,
    OutcomeWriteBackHook,
)


def test_null_outcome_write_back_hook() -> None:
    """NullOutcomeWriteBackHook does nothing."""
    hook = NullOutcomeWriteBackHook()

    # Should not raise any exceptions
    hook.on_outcome(
        healing_input=None,
        decision=None,
        record=None,
        success=True,
    )


def test_default_outcome_write_back_hook_success() -> None:
    """Default hook records success outcome."""
    store = HealingSuccessRateStore()
    hook = DefaultOutcomeWriteBackHook(store)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    decision = HealingDecision(
        heal_confidence=0.8,
        tier=HealingTier.LOCAL_AGENT,
        reason_codes=("test",),
    )

    # Record success
    hook.on_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=True,
    )

    # Store should have the outcome
    assert store.get_counts().get("test_sig", 0) == 1


def test_default_outcome_write_back_hook_failure() -> None:
    """Default hook records failure outcome."""
    store = HealingSuccessRateStore()
    hook = DefaultOutcomeWriteBackHook(store)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    decision = HealingDecision(
        heal_confidence=0.8,
        tier=HealingTier.LOCAL_AGENT,
        reason_codes=("test",),
    )

    # Record failure
    hook.on_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=False,
    )

    # Store should have the outcome
    assert store.get_counts().get("test_sig", 0) == 1


def test_default_outcome_write_back_hook_uses_default_store() -> None:
    """Default hook uses process-global store when none provided."""
    with patch("system_learning.engines.healing_success_rate_store.get_default_store") as mock_get_default:
        mock_store = MagicMock()
        mock_get_default.return_value = mock_store

        hook = DefaultOutcomeWriteBackHook()

        healing_input = HealingInput(
            error_signature="test_sig",
            failure_type="syntax_error",
            blast_radius_estimate=0.1,
            required_tools=[],
            retry_count=0,
            trace_id="test-trace",
            agent_id="test-agent",
        )

        decision = HealingDecision(
            heal_confidence=0.8,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("test",),
        )

        hook.on_outcome(
            healing_input=healing_input,
            decision=decision,
            record=None,
            success=True,
        )

        # Store injected at construction time from get_default_store
        mock_store.record_outcome.assert_called_once_with("test_sig", True)


def test_default_outcome_write_back_hook_qwen_update() -> None:
    """Default hook calls update_qwen_confidence_prior for Qwen tier."""
    store = HealingSuccessRateStore()
    hook = DefaultOutcomeWriteBackHook(store)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    decision = HealingDecision(
        heal_confidence=0.8,
        tier=HealingTier.QWEN_VLLM,
        reason_codes=("test",),
    )

    with patch(
        "agentic_core.L2_execution.healers.qwen_meta_learning.update_qwen_confidence_prior"
    ) as mock_update:
        hook.on_outcome(
            healing_input=healing_input,
            decision=decision,
            record=None,
            success=True,
        )

        # Should call Qwen update
        mock_update.assert_called_once_with("test_sig", True)


def test_default_outcome_write_back_hook_handles_store_exception() -> None:
    """Default hook logs but doesn't fail when store throws."""
    store = MagicMock()
    store.record_outcome.side_effect = Exception("Store error")

    hook = DefaultOutcomeWriteBackHook(store)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    decision = HealingDecision(
        heal_confidence=0.8,
        tier=HealingTier.LOCAL_AGENT,
        reason_codes=("test",),
    )

    # Should not raise exception
    with patch("system_learning.ports.outcome_write_back_hook.logger"):
        hook.on_outcome(
            healing_input=healing_input,
            decision=decision,
            record=None,
            success=True,
        )


def test_outcome_write_back_hook_protocol() -> None:
    """Default hook satisfies OutcomeWriteBackHook protocol."""
    hook = DefaultOutcomeWriteBackHook()
    assert isinstance(hook, OutcomeWriteBackHook)
