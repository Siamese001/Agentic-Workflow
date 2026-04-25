"""Smoke tests for layer_sovereignty_enforcer — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.layer_sovereignty_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_SovereigntyViolation_present():
    assert hasattr(mod, "SovereigntyViolation")
    assert isinstance(mod.SovereigntyViolation, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
