"""Smoke tests for escalation_router — wave 26."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.escalation_router")


def test_module_imports_clean():
    assert mod is not None


def test_decide_mode_from_prior_violations_callable():
    assert callable(mod.decide_mode_from_prior_violations)


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
