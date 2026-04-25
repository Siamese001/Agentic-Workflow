"""Smoke tests for TypeHintFixerAgent — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.TypeHintFixerAgent")


def test_module_imports_clean():
    assert mod is not None


def test_TypeHintFixerAgent_class_present():
    assert hasattr(mod, "TypeHintFixerAgent")
    assert isinstance(mod.TypeHintFixerAgent, type)


def test_TypeHintFixerAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.TypeHintFixerAgent.__mro__]
    assert "SovereignBaseAgent" in bases


def test_TypeHintFixerAgent_has_heal_repository():
    assert callable(getattr(mod.TypeHintFixerAgent, "heal_repository", None))
