"""Smoke tests for secure_error_handler_enforcer — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.secure_error_handler_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_SecureError_present():
    assert hasattr(mod, "SecureError")
    assert isinstance(mod.SecureError, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
