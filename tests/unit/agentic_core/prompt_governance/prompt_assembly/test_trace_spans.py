"""Unit tests for PA trace spans."""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.prompt_assembly.trace_spans import (
    PA_PARENT_SPAN_NAME,
    PA_SPAN_DEFINITIONS,
    SPAN_NAMES,
    SpanCollector,
)


def test_eight_pa_spans_defined():
    assert len(PA_SPAN_DEFINITIONS) == 8


def test_all_spans_have_pa_prefix():
    for s in PA_SPAN_DEFINITIONS:
        assert s.name.startswith("prompt_assembly.")


def test_all_spans_share_parent():
    for s in PA_SPAN_DEFINITIONS:
        assert s.parent == PA_PARENT_SPAN_NAME


def test_span_names_set_contains_each_definition():
    for s in PA_SPAN_DEFINITIONS:
        assert s.name in SPAN_NAMES


def test_span_collector_emit_appends():
    c = SpanCollector()
    c.emit("prompt_assembly.boundary_check", {"plan_id": "p1"})
    c.emit("prompt_assembly.bom_resolve", {"bom_id": "b1"})
    assert c.names() == ("prompt_assembly.boundary_check", "prompt_assembly.bom_resolve")
    assert c.spans[0].attributes["plan_id"] == "p1"


def test_span_collector_unknown_span_raises():
    c = SpanCollector()
    with pytest.raises(ValueError):
        c.emit("prompt_assembly.bogus", {})
