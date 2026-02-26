"""
Tests for EscalationContext monotonicity enforcement.

Phase 3.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.healers.escalation_context import (
    EscalationContext,
    MonotonicityViolation,
)


class TestEscalationContextInitial:
    def test_initial_has_zero_retry(self) -> None:
        ctx = EscalationContext.initial("trace-1", "tier_1")
        assert ctx.retry_count == 0
        assert ctx.previous_retry_count == 0

    def test_initial_trace_id_preserved(self) -> None:
        ctx = EscalationContext.initial("trace-abc", "tier_1")
        assert ctx.trace_id == "trace-abc"

    def test_initial_healing_tier(self) -> None:
        ctx = EscalationContext.initial("t", "tier_2")
        assert ctx.healing_tier == "tier_2"


class TestEscalationContextFromResult:
    def test_increments_retry_count(self) -> None:
        ctx = EscalationContext.initial("t", "tier_1")
        ctx2 = EscalationContext.from_result(ctx)
        assert ctx2.retry_count == 1
        assert ctx2.previous_retry_count == 0

    def test_successive_increments(self) -> None:
        ctx = EscalationContext.initial("t", "tier_1")
        for expected in range(1, 6):
            ctx = EscalationContext.from_result(ctx)
            assert ctx.retry_count == expected

    def test_tier_update(self) -> None:
        ctx = EscalationContext.initial("t", "tier_1")
        ctx2 = EscalationContext.from_result(ctx, new_healing_tier="tier_2")
        assert ctx2.healing_tier == "tier_2"

    def test_tier_preserves_if_none(self) -> None:
        ctx = EscalationContext.initial("t", "tier_3")
        ctx2 = EscalationContext.from_result(ctx)
        assert ctx2.healing_tier == "tier_3"

    def test_trace_id_preserved(self) -> None:
        ctx = EscalationContext.initial("trace-xyz", "tier_1")
        ctx2 = EscalationContext.from_result(ctx)
        assert ctx2.trace_id == "trace-xyz"


class TestEscalationContextMonotonicity:
    def test_direct_construction_violation(self) -> None:
        with pytest.raises(MonotonicityViolation):
            EscalationContext(
                trace_id="t",
                retry_count=1,
                healing_tier="tier_1",
                previous_retry_count=3,  # previous > current → violation
            )

    def test_negative_retry_count_rejected(self) -> None:
        with pytest.raises(ValueError, match="retry_count"):
            EscalationContext(
                trace_id="t",
                retry_count=-1,
                healing_tier="tier_1",
                previous_retry_count=0,
            )

    def test_equal_counts_allowed(self) -> None:
        ctx = EscalationContext(
            trace_id="t",
            retry_count=3,
            healing_tier="tier_1",
            previous_retry_count=3,
        )
        assert ctx.retry_count == 3


class TestEscalationContextIsExhausted:
    def test_not_exhausted_below_5(self) -> None:
        ctx = EscalationContext.initial("t", "tier_1")
        for _ in range(4):
            ctx = EscalationContext.from_result(ctx)
        assert ctx.retry_count == 4
        assert ctx.is_exhausted is False

    def test_exhausted_at_5(self) -> None:
        ctx = EscalationContext.initial("t", "tier_1")
        for _ in range(5):
            ctx = EscalationContext.from_result(ctx)
        assert ctx.retry_count == 5
        assert ctx.is_exhausted is True

    def test_frozen_dataclass(self) -> None:
        ctx = EscalationContext.initial("t", "tier_1")
        with pytest.raises((AttributeError, TypeError)):
            ctx.retry_count = 99  # type: ignore[misc]
