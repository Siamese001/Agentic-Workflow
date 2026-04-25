"""Smoke tests for gravity_validator — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.gravity_validator")


def test_module_imports_clean():
    assert mod is not None


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_SSOTScanner_present():
    assert hasattr(mod, "SSOTScanner")
