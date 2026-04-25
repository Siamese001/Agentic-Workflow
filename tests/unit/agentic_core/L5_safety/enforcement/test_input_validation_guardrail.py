"""Smoke tests for input_validation_guardrail — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.input_validation_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_SovereignBaseAgent_present():
    assert hasattr(mod, "SovereignBaseAgent")


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
