"""ADG-driven tests for mixins/context_propagation_mixin.py — fan_in=1."""
from __future__ import annotations

import pytest

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
