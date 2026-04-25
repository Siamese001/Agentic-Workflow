"""Smoke tests for routing_optimization — wave 14."""

import pytest

mod = pytest.importorskip("agentic_core.L0_routing.reasoning.routing_optimization")


def test_module_imports_clean():
    assert mod is not None


def test_all_exports_resolvable():
    for name in mod.__all__:
        assert hasattr(mod, name), f"__all__ advertises {name!r} but it is missing"


def test_RoutingOptimizationRegistry_present():
    assert hasattr(mod, "RoutingOptimizationRegistry")
    assert isinstance(mod.RoutingOptimizationRegistry, type)


def test_RoutingOptimizationError_is_exception():
    assert issubclass(mod.RoutingOptimizationError, Exception)


def test_get_routing_optimization_registry_callable():
    assert callable(mod.get_routing_optimization_registry)


def test_reset_routing_optimization_registry_callable():
    assert callable(mod.reset_routing_optimization_registry)


def test_singleton_pattern():
    mod.reset_routing_optimization_registry()
    reg1 = mod.get_routing_optimization_registry()
    reg2 = mod.get_routing_optimization_registry()
    assert reg1 is reg2
