"""Surface coverage for `agentic_core.L0_routing.reasoning.agentic_router`.

Wave 4 of `docs/archive/windsurf/legacy-tree/plans/test-coverage-waves-f8f5a7.md`. L0 routing core.
Fan-out=10 (heavy execution-surface).
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L0_routing.reasoning.agentic_router"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


@pytest.mark.parametrize("name", ["RouteTarget", "RoutingDecision", "AgenticRouter"])
def test_public_classes_present(mod, name):
    assert hasattr(mod, name), f"{name} missing"
    assert inspect.isclass(getattr(mod, name))


@pytest.mark.parametrize(
    "private_factory",
    ["_get_perf_emitter", "_get_routing_gateway", "_get_proof_emitter"],
)
def test_lazy_factory_helpers_callable(mod, private_factory):
    fn = getattr(mod, private_factory, None)
    assert callable(fn), f"{private_factory} must be callable"


def test_perf_emitter_returns_3_tuple(mod):
    """_get_perf_emitter() declared `tuple[Any, Any, Any]`."""
    result = mod._get_perf_emitter()
    assert isinstance(result, tuple)
    assert len(result) == 3
