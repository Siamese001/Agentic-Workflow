"""Smoke tests for error_recovery_strategy — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.error_recovery_strategy")


def test_module_imports_clean():
    assert mod is not None


def test_ErrorRecoveryStrategy_class_present():
    assert hasattr(mod, "ErrorRecoveryStrategy")
    assert isinstance(mod.ErrorRecoveryStrategy, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
