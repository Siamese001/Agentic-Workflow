"""Smoke tests for CostGovernorAgent — wave 15."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.CostGovernorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_CostGovernorAgent_class_present():
    assert hasattr(mod, "CostGovernorAgent")
    assert isinstance(mod.CostGovernorAgent, type)


def test_CostGovernorAgent_inherits_SovereignBaseAgent():
    bases = [c.__name__ for c in mod.CostGovernorAgent.__mro__]
    assert "SovereignBaseAgent" in bases
