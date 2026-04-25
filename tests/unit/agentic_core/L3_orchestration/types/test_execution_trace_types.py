"""Smoke tests for execution_trace_types — wave 22."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.types.execution_trace_types")


def test_module_imports_clean():
    assert mod is not None


def test_GovernedPayload_present():
    assert hasattr(mod, "GovernedPayload")
    assert isinstance(mod.GovernedPayload, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
