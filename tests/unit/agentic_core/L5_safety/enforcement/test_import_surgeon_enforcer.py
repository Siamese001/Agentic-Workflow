"""Smoke tests for import_surgeon_enforcer — wave 23."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.import_surgeon_enforcer")


def test_module_imports_clean():
    assert mod is not None


def test_get_validated_project_root_callable():
    assert callable(mod.get_validated_project_root)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
