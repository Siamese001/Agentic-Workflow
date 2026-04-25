"""Smoke tests for ssot_import_enforcer — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.ssot_import_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_needs_ssot_import_callable():
    assert callable(mod.needs_ssot_import)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
