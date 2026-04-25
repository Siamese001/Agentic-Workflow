"""Smoke tests for guard_observability_footprint_util — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.guard_observability_footprint_util")


def test_module_imports_clean():
    assert mod is not None


def test_record_execution_trace_callable():
    assert callable(mod.record_execution_trace)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
