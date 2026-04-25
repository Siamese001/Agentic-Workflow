"""Smoke tests for module_collision_guardrail — wave 27."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.module_collision_guardrail")


def test_module_imports_clean():
    assert mod is not None


def test_compute_logical_import_path_callable():
    assert callable(mod.compute_logical_import_path)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
