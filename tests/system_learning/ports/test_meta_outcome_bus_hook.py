"""Tests for MetaOutcomeBusHook port (Phase 4)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)
from system_learning.ports.meta_outcome_bus_hook import (
    DefaultMetaOutcomeBusHook,
    MetaOutcomeBusHook,
    NullMetaOutcomeBusHook,
)


def test_null_meta_outcome_bus_hook() -> None:
    """NullMetaOutcomeBusHook does nothing."""
    hook = NullMetaOutcomeBusHook()

    # Should not raise any exceptions
    hook.publish_outcome(
        healing_input=None,
        decision=None,
        record=None,
        success=True,
    )


def test_default_meta_outcome_bus_hook_no_bus_is_noop() -> None:
    """Default hook with no bus is a no-op (NullBus default)."""
    hook = DefaultMetaOutcomeBusHook()  # bus=None

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

    # Should not raise, and no bus to call
    hook.publish_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=True,
    )


def test_default_meta_outcome_bus_hook_success() -> None:
    """Default hook enqueues success outcome."""
    mock_bus = MagicMock()
    hook = DefaultMetaOutcomeBusHook(bus=mock_bus)

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

    hook.publish_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=True,
    )

    # Should enqueue change package on bus
    mock_bus.enqueue.assert_called_once()
    package = mock_bus.enqueue.call_args[0][0]

    assert package.proposal_only is True
    assert package.payload["error_signature"] == "test_sig"
    assert package.payload["success"] is True
    assert package.payload["heal_confidence"] == 0.8
    assert package.payload["trace_id"] == "test-trace"
    assert package.payload["retry_count"] == 0
    assert package.payload["reason_codes"] == ("test",)


def test_default_meta_outcome_bus_hook_failure() -> None:
    """Default hook enqueues failure outcome."""
    mock_bus = MagicMock()
    hook = DefaultMetaOutcomeBusHook(bus=mock_bus)

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

    hook.publish_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=False,
    )

    mock_bus.enqueue.assert_called_once()
    package = mock_bus.enqueue.call_args[0][0]

    assert package.proposal_only is True
    assert package.payload["error_signature"] == "test_sig"
    assert package.payload["success"] is False


def test_default_meta_outcome_bus_hook_handles_bus_exception() -> None:
    """Default hook logs but doesn't fail when bus throws."""
    mock_bus = MagicMock()
    mock_bus.enqueue.side_effect = Exception("Bus error")

    hook = DefaultMetaOutcomeBusHook(bus=mock_bus)

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

    # Should not raise exception despite bus failure
    with patch("system_learning.ports.meta_outcome_bus_hook.logger"):
        hook.publish_outcome(
            healing_input=healing_input,
            decision=decision,
            record=None,
            success=True,
        )


def test_default_meta_outcome_bus_hook_proposal_only_enforced() -> None:
    """proposal_only=True is always enforced regardless of inputs."""
    mock_bus = MagicMock()
    hook = DefaultMetaOutcomeBusHook(bus=mock_bus)

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
        heal_confidence=0.85,
        tier=HealingTier.QWEN_VLLM,
        reason_codes=("historical_success=0.90",),
    )

    hook.publish_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=True,
    )

    package = mock_bus.enqueue.call_args[0][0]
    assert package.proposal_only is True


def test_default_meta_outcome_bus_hook_tier_in_payload() -> None:
    """Tier value is included in payload."""
    mock_bus = MagicMock()
    hook = DefaultMetaOutcomeBusHook(bus=mock_bus)

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
        heal_confidence=0.85,
        tier=HealingTier.QWEN_VLLM,
        reason_codes=("historical_success=0.90",),
    )

    hook.publish_outcome(
        healing_input=healing_input,
        decision=decision,
        record=None,
        success=True,
    )

    package = mock_bus.enqueue.call_args[0][0]
    # Tier value should be present (string or enum value)
    assert "tier" in package.payload


def test_meta_outcome_bus_hook_protocol() -> None:
    """DefaultMetaOutcomeBusHook satisfies MetaOutcomeBusHook protocol."""
    hook = DefaultMetaOutcomeBusHook()
    assert isinstance(hook, MetaOutcomeBusHook)
