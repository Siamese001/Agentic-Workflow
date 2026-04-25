"""Smoke tests for TestGeneratorAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.TestGeneratorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_TestGeneratorAgent_class_present():
    assert hasattr(mod, "TestGeneratorAgent")
    assert isinstance(mod.TestGeneratorAgent, type)


def test_TestGeneratorAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.TestGeneratorAgent.__mro__]
    assert "SovereignBaseAgent" in bases


def test_TestGeneratorAgent_has_heal_repository():
    assert callable(getattr(mod.TestGeneratorAgent, "heal_repository", None))
