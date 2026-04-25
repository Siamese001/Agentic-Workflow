"""Smoke tests for structural_namespace_fence_enforcer — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.structural_namespace_fence_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_install_structural_namespace_fence_callable():
    assert callable(mod.install_structural_namespace_fence)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
