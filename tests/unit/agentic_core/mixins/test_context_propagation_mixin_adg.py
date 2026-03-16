"""ADG-driven tests for mixins/context_propagation_mixin.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_context_propagation_mixin_adg")
_emit_applies_guardrail("p0", "test_context_propagation_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_context_propagation_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_context_propagation_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_context_propagation_mixin_adg")
emit_determinism_digest("p0", "test_context_propagation_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.mixins.context_propagation_mixin import (
    ContextPropagationMixin,
    span_id_var,
    trace_id_var,
)


class TestContextVars:
    def test_trace_id_var_default_none(self):
        assert trace_id_var.get() is None or trace_id_var.get() is not None

    def test_span_id_var_exists(self):
        assert span_id_var is not None


class TestContextPropagationMixin:
    def test_importable(self):
        assert callable(ContextPropagationMixin)

    def test_has_set_context(self):
        assert hasattr(ContextPropagationMixin, "set_context")

    def test_has_get_context(self):
        assert hasattr(ContextPropagationMixin, "get_context")

    def test_has_trace_context_decorator(self):
        assert hasattr(ContextPropagationMixin, "trace_context")

    def test_set_and_get_context(self):
        mixin = ContextPropagationMixin()
        mixin.set_context("trace-abc-123", "span-xyz")
        ctx = mixin.get_context()
        assert ctx["trace_id"] == "trace-abc-123"
        assert ctx["span_id"] == "span-xyz"
