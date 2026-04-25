"""Smoke tests for hash_chain_audit_log — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.audit.hash_chain_audit_log")


def test_module_imports_clean():
    assert mod is not None


def test_AuditEntry_present():
    assert hasattr(mod, "AuditEntry")
    assert isinstance(mod.AuditEntry, type)


def test_canonical_bytes_callable():
    assert callable(mod.canonical_bytes)
