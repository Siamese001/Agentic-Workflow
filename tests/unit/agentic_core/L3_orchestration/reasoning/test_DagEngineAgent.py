"""Smoke tests for DagEngineAgent — wave 30."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.reasoning.DagEngineAgent")


def test_module_imports_clean():
    assert mod is not None


def test_module_has_public_surface():
    public = [k for k in dir(mod) if not k.startswith("_")]
    assert len(public) > 0


def test_get_routing_gateway_callable():
    assert callable(mod.get_routing_gateway)
