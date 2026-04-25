"""Smoke tests for RootCustomsAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.RootCustomsAgent")


def test_module_imports_clean():
    assert mod is not None


def test_RootCustomsAgent_class_present():
    assert hasattr(mod, "RootCustomsAgent")
    assert isinstance(mod.RootCustomsAgent, type)


def test_RootCustomsAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.RootCustomsAgent.__mro__]
    assert "SovereignBaseAgent" in bases


def test_RootCustomsAgent_has_heal_repository():
    assert callable(getattr(mod.RootCustomsAgent, "heal_repository", None))
