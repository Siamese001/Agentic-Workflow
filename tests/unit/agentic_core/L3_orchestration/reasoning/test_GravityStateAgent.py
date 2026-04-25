"""Smoke tests for GravityStateAgent — wave 24."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.GravityStateAgent")


def test_module_imports_clean():
    assert mod is not None


def test_GravityStateAgent_present():
    assert hasattr(mod, "GravityStateAgent")
    assert isinstance(mod.GravityStateAgent, type)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
