"""Smoke tests for trace_id_generator — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.enforcement.trace_id_generator")


def test_module_imports_clean():
    assert mod is not None


def test_TraceIdGenerator_present():
    assert hasattr(mod, "TraceIdGenerator")
    assert isinstance(mod.TraceIdGenerator, type)


def test_generate_trace_id_callable():
    assert callable(mod.generate_trace_id)
