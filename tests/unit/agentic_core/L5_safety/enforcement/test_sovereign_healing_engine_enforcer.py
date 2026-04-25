"""Smoke tests for sovereign_healing_engine_enforcer — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.sovereign_healing_engine_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_get_filesystem_client_callable():
    assert callable(mod.get_filesystem_client)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
