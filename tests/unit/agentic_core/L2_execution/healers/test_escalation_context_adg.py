"""ADG-driven tests for L2_execution/healers/escalation_context.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_escalation_context_adg")
_emit_applies_guardrail("p0", "test_escalation_context_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_escalation_context_adg", "policy_binding")
_emit_snapshots_state("p0", "test_escalation_context_adg", "state_snapshot")
emit_replay_key("p0", "test_escalation_context_adg")
emit_determinism_digest("p0", "test_escalation_context_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.escalation_context import (
    EscalationContext,
    MonotonicityViolation,
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
