"""Smoke tests for pytest_config_guardrail — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.pytest_config_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_PytestEnforcementGuard_present():
    assert hasattr(mod, "PytestEnforcementGuard")
    assert isinstance(mod.PytestEnforcementGuard, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
