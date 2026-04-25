"""Smoke tests for context_validator — wave 16."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.context_validator")


def test_module_imports_clean():
    assert mod is not None


def test_L4ContextManager_class_present():
    assert hasattr(mod, "L4ContextManager")
    assert isinstance(mod.L4ContextManager, type)


def test_HealingPattern_class_present():
    assert hasattr(mod, "HealingPattern")
    assert isinstance(mod.HealingPattern, type)


def test_emit_determinism_digest_callable():
    assert callable(mod.emit_determinism_digest)
