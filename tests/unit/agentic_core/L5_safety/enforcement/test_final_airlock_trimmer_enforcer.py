"""Smoke tests for final_airlock_trimmer_enforcer — wave 21."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.final_airlock_trimmer_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)


def test_get_validated_project_root_callable():
    assert callable(mod.get_validated_project_root)
