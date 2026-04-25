"""Smoke tests for NeuralAutoImmuneAgent — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent")


def test_module_imports_clean():
    assert mod is not None


def test_NeuralAutoImmuneAgent_class_present():
    assert hasattr(mod, "NeuralAutoImmuneAgent")
    assert isinstance(mod.NeuralAutoImmuneAgent, type)


def test_NeuralAutoImmuneAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.NeuralAutoImmuneAgent.__mro__]
    assert "SovereignBaseAgent" in bases


def test_NeuralAutoImmuneAgent_has_heal_repository():
    assert callable(getattr(mod.NeuralAutoImmuneAgent, "heal_repository", None))
