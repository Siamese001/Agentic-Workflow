"""ADG-driven tests for L2_execution/healers/escalation_context.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.escalation_context import (
    MonotonicityViolation,
    EscalationContext,
)


class TestMonotonicityViolation:
    def test_is_runtime_error(self):
        assert issubclass(MonotonicityViolation, RuntimeError)


class TestEscalationContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EscalationContext)

    def test_is_frozen(self):
        ctx = EscalationContext(
            trace_id="t1", retry_count=1, healing_tier="tier_1", previous_retry_count=0
        )
        with pytest.raises((AttributeError, TypeError)):
            ctx.retry_count = 2

    def test_creates(self):
        ctx = EscalationContext(
            trace_id="t1", retry_count=2, healing_tier="tier_2", previous_retry_count=1
        )
        assert ctx.trace_id == "t1"
        assert ctx.retry_count == 2
