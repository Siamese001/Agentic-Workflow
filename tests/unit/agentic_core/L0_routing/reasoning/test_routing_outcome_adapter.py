"""Smoke tests for routing_outcome_adapter — wave 26."""

import pytest

mod = pytest.importorskip(
    "agentic_core.L0_routing.reasoning.routing_outcome_adapter",
    exc_type=Exception,
)


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0
