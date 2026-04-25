"""Smoke tests for capability_registry — wave 25."""

import pytest

mod = pytest.importorskip("agentic_core.L3_orchestration.utils.registry.capability_registry")


def test_module_imports_clean():
    assert mod is not None


def test_CapabilityNotFoundError_present():
    assert hasattr(mod, "CapabilityNotFoundError")
    assert isinstance(mod.CapabilityNotFoundError, type)


def test_get_routing_gateway_callable():
    assert callable(mod.get_routing_gateway)
