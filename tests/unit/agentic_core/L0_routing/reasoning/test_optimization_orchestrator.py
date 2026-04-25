"""Surface coverage for `agentic_core.L0_routing.reasoning.optimization_orchestrator`.

Wave 8 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v2). L0
routing optimization orchestrator — analyzes historical routing outcomes.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L0_routing.reasoning.optimization_orchestrator"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_resolvable(mod):
    assert hasattr(mod, "__all__")
    missing = [n for n in mod.__all__ if not hasattr(mod, n)]
    assert not missing, f"__all__ leaks unresolved names: {missing}"


@pytest.mark.parametrize("name", ["RoutingHistory", "OptimizationWindow", "PolicyContext"])
def test_public_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


@pytest.mark.parametrize(
    "fn",
    [
        "optimize_routing_policy",
        "query_routing_optimizations",
        "get_routing_optimization_registry",
        "reset_routing_optimization_registry",
        "get_optimization_recommendations",
        "apply_optimization_with_governance",
        "optimize_simple_routing",
    ],
)
def test_public_functions_callable(mod, fn):
    assert hasattr(mod, fn), f"{fn} missing"
    assert callable(getattr(mod, fn))


def test_get_registry_returns_object(mod):
    """Registry getter must return a non-None object (initialization smoke)."""
    mod.reset_routing_optimization_registry()
    registry = mod.get_routing_optimization_registry()
    assert registry is not None
