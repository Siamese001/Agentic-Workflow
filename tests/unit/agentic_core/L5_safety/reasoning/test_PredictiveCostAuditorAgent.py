"""Smoke tests for PredictiveCostAuditorAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent")


def test_module_imports_clean():
    assert mod is not None


def test_PredictiveCostAuditorAgent_class_present():
    assert hasattr(mod, "PredictiveCostAuditorAgent")
    assert isinstance(mod.PredictiveCostAuditorAgent, type)


def test_PredictiveCostAuditorAgent_has_heal_repository():
    assert callable(getattr(mod.PredictiveCostAuditorAgent, "heal_repository", None))
