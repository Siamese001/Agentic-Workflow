"""Smoke tests for SecurityManagerAgent — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.SecurityManagerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_PermissionLevel_present():
    assert hasattr(mod, "PermissionLevel")


def test_SecurityAction_present():
    assert hasattr(mod, "SecurityAction")


def test_SecurityAuditEntry_present():
    assert hasattr(mod, "SecurityAuditEntry")
    assert isinstance(mod.SecurityAuditEntry, type)
