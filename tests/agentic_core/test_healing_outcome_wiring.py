"""L2.3 Healing Outcome Wiring Tests — emit-only seam verification.

Tests:
  - Inject fake sink; assert exactly one event emitted on success.
  - Inject fake sink; assert exactly one event emitted on failure.
  - No sink provided: default runtime unchanged (no emission).
  - Sink exception swallowed: dispatch still returns normally.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.healers.healing_tier_config import (
    load_default_healing_tier_config,
)
from agentic_core.L2_execution.healers.healing_tier_dispatcher import (
    DefaultHealingProviderInvoker,
    HealingProviderInvoker,
    InvocationRecord,
    dispatch_healing,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)
from system_learning.types.healing_outcome_types import HealingOutcomeEvent


# -------------------------------------------------------------------------
# Fake sink that records emitted events
# -------------------------------------------------------------------------


class FakeOutcomeSink:
    """Test double: records all emitted events."""

    def __init__(self) -> None:
        self.events: list[HealingOutcomeEvent] = []

    def emit(self, event: HealingOutcomeEvent) -> None:
        self.events.append(event)


class ExplodingSink:
    """Test double: raises on emit to prove swallow behaviour."""

    def emit(self, event: HealingOutcomeEvent) -> None:
        raise RuntimeError("sink exploded")


# -------------------------------------------------------------------------
# Fake invoker that always succeeds
# -------------------------------------------------------------------------


class SuccessInvoker:
    """Test invoker that always returns a successful InvocationRecord."""

    def invoke_local(self, healing_input, decision, config, *, agent_name=""):
        return InvocationRecord(
            tier=HealingTier.LOCAL_AGENT,
            model_id="local",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_local",
        )

    def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
        return InvocationRecord(
            tier=HealingTier.QWEN_VLLM,
            model_id="qwen-test",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_qwen_vllm",
        )

    def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
        return InvocationRecord(
            tier=HealingTier.GEMINI_2_5_PRO,
            model_id="gemini-test",
            agent_name=agent_name,
            trace_id=healing_input.trace_id,
            heal_confidence=decision.heal_confidence,
            method_called="invoke_gemini",
        )


class FailingInvoker:
    """Test invoker that always raises on every method."""

    def invoke_local(self, healing_input, decision, config, *, agent_name=""):
        raise RuntimeError("provider failed")

    def invoke_qwen_vllm(self, healing_input, decision, config, *, agent_name=""):
        raise RuntimeError("provider failed")

    def invoke_gemini(self, healing_input, decision, config, *, agent_name=""):
        raise RuntimeError("provider failed")


# -------------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------------


def _make_input(
    *,
    failure_type: str = "syntax_error",
    blast_radius: float = 0.3,
    retry_count: int = 0,
) -> HealingInput:
    return HealingInput(
        failure_type=failure_type,
        error_signature="sig-abc123",
        trace_id="trace-001",
        retry_count=retry_count,
        blast_radius_estimate=blast_radius,
        required_tools=("ast_rewrite",),
        violation_metadata_refs=(),
    )


# -------------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------------


class TestOutcomeSinkWiring:
    """Verify emit-only wiring via injected outcome_sink."""

    def test_success_emits_exactly_one_event(self) -> None:
        """On successful invocation, exactly one event with success=True is emitted."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=sink,
            timestamp_utc=1000,
        )

        assert len(sink.events) == 1
        ev = sink.events[0]
        assert ev.success is True
        assert ev.healer_id == "test_healer"
        assert ev.tier == decision.tier.value
        assert ev.failure_type == "syntax_error"
        assert ev.timestamp_utc == 1000
        assert ev.trace_id == "trace-001"
        assert ev.error_signature == "sig-abc123"

    def test_failure_emits_exactly_one_event(self) -> None:
        """On failed invocation, exactly one event with success=False is emitted."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        with pytest.raises(RuntimeError, match="provider failed"):
            dispatch_healing(
                inp,
                config,
                invoker=FailingInvoker(),
                agent_name="test_healer",
                outcome_sink=sink,
                timestamp_utc=2000,
            )

        assert len(sink.events) == 1
        ev = sink.events[0]
        assert ev.success is False
        assert ev.healer_id == "test_healer"
        assert ev.timestamp_utc == 2000

    def test_no_sink_no_emission(self) -> None:
        """When outcome_sink is None, dispatch works exactly as before."""
        config = load_default_healing_tier_config()
        inp = _make_input()

        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=None,
            timestamp_utc=3000,
        )

        # Should succeed normally without any sink-related issues
        assert record.method_called in ("invoke_local", "invoke_qwen_vllm", "invoke_gemini")

    def test_sink_exception_swallowed(self) -> None:
        """If sink.emit() raises, dispatch still returns normally."""
        sink = ExplodingSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        # Should NOT raise despite ExplodingSink
        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=sink,
            timestamp_utc=4000,
        )

        assert record.method_called in ("invoke_local", "invoke_qwen_vllm", "invoke_gemini")

    def test_no_timestamp_skips_emission(self) -> None:
        """When timestamp_utc is None, no emission even with a sink."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        decision, record = dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="test_healer",
            outcome_sink=sink,
            timestamp_utc=None,
        )

        assert len(sink.events) == 0

    def test_default_healer_id_when_agent_name_empty(self) -> None:
        """When agent_name is empty, healer_id defaults to 'unknown'."""
        sink = FakeOutcomeSink()
        config = load_default_healing_tier_config()
        inp = _make_input()

        dispatch_healing(
            inp,
            config,
            invoker=SuccessInvoker(),
            agent_name="",
            outcome_sink=sink,
            timestamp_utc=5000,
        )

        assert len(sink.events) == 1
        assert sink.events[0].healer_id == "unknown"
