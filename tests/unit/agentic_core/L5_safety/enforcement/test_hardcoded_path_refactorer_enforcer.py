"""Smoke tests for hardcoded_path_refactorer_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.hardcoded_path_refactorer_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_should_exclude_path_callable():
    assert callable(mod.should_exclude_path)
