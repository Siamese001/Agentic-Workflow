"""Smoke tests for DomainPlannerAdapter — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L5_safety.enforcement.DomainPlannerAdapter")


def test_module_imports_clean():
    assert mod is not None


def test_get_breaker_callable():
    assert callable(mod.get_breaker)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
