"""Smoke tests for injection_regression_gate — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.security.injection_regression_gate")


def test_module_imports_clean():
    assert mod is not None


def test_RegressionThresholds_class_present():
    assert hasattr(mod, "RegressionThresholds")
    assert isinstance(mod.RegressionThresholds, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
