"""Smoke tests for HygieneGuardianAgent — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.validators.HygieneGuardianAgent")


def test_module_imports_clean():
    assert mod is not None


def test_HygieneGuardianAgent_class_present():
    assert hasattr(mod, "HygieneGuardianAgent")
    assert isinstance(mod.HygieneGuardianAgent, type)


def test_HygieneGuardianAgent_has_heal_repository():
    assert callable(getattr(mod.HygieneGuardianAgent, "heal_repository", None))
