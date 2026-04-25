"""Smoke tests for safety_layer_enforcer — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.safety_layer_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_create_l5_safety_layer_callable():
    assert callable(mod.create_l5_safety_layer)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
