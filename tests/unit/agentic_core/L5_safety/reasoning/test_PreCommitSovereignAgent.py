"""Smoke tests for PreCommitSovereignAgent — wave 13."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.reasoning.PreCommitSovereignAgent")


def test_module_imports_clean():
    assert mod is not None


def test_PreCommitSovereignAgent_class_present():
    assert hasattr(mod, "PreCommitSovereignAgent")
    assert isinstance(mod.PreCommitSovereignAgent, type)


def test_PreCommitSovereignAgent_has_heal_repository():
    assert callable(getattr(mod.PreCommitSovereignAgent, "heal_repository", None))
