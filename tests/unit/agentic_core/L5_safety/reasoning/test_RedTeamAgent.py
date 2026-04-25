"""Smoke tests for RedTeamAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.RedTeamAgent")


def test_module_imports_clean():
    assert mod is not None


def test_RedTeamAgent_class_present():
    assert hasattr(mod, "RedTeamAgent")
    assert isinstance(mod.RedTeamAgent, type)


def test_RedTeamAgent_has_heal_repository():
    assert callable(getattr(mod.RedTeamAgent, "heal_repository", None))
