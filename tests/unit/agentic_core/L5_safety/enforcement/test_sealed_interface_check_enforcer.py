"""Smoke tests for sealed_interface_check_enforcer — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.sealed_interface_check_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_check_file_callable():
    assert callable(mod.check_file)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
