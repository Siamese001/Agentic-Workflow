"""Smoke tests for toxic_dependency_auditor_enforcer — wave 20."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.toxic_dependency_auditor_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_SovereignBaseAgent_in_module():
    assert hasattr(mod, "SovereignBaseAgent")


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
