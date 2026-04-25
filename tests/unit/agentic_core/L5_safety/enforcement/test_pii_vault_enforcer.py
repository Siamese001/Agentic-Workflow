"""Smoke tests for pii_vault_enforcer — wave 18."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.pii_vault_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_PiiVault_class_present():
    assert hasattr(mod, "PiiVault")
    assert isinstance(mod.PiiVault, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
