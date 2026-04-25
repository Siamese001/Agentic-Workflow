"""Smoke tests for healing_invocation_audit_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.healing_invocation_audit_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_HealingInvocationAudit_present():
    assert hasattr(mod, "HealingInvocationAudit")
    assert isinstance(mod.HealingInvocationAudit, type)


def test_safe_execute_callable():
    assert callable(mod.safe_execute)
