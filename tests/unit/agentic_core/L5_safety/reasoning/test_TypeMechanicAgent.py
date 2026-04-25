"""Smoke tests for TypeMechanicAgent — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.TypeMechanicAgent")


def test_module_imports_clean():
    assert mod is not None


def test_TypeMechanicAgent_class_present():
    assert hasattr(mod, "TypeMechanicAgent")
    assert isinstance(mod.TypeMechanicAgent, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
