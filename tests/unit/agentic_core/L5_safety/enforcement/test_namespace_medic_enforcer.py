"""Smoke tests for namespace_medic_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.namespace_medic_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_find_missing_imports_callable():
    assert callable(mod.find_missing_imports)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
