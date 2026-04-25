"""Smoke tests for reflexion_types — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.types.reflexion_types")


def test_module_imports_clean():
    assert mod is not None


def test_ReflexionCritique_class_present():
    assert hasattr(mod, "ReflexionCritique")
    assert isinstance(mod.ReflexionCritique, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
