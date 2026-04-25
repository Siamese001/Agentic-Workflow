"""Smoke tests for subprocess_security_util — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.utils.subprocess_security_util")


def test_module_imports_clean():
    assert mod is not None


def test_SecurityViolationError_class_present():
    assert hasattr(mod, "SecurityViolationError")
    assert isinstance(mod.SecurityViolationError, type)


def test_safe_execute_callable():
    assert callable(mod.safe_execute)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
