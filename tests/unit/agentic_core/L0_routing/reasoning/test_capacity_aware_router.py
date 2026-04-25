"""Surface coverage for `agentic_core.L0_routing.reasoning.capacity_aware_router`.

Wave 11 of `.windsurf/plans/test-coverage-waves-f8f5a7.md` (Top-15 v3). L0
capacity-aware routing.
"""

from __future__ import annotations

import inspect

import pytest

pytestmark = pytest.mark.unit

MODULE = "agentic_core.L0_routing.reasoning.capacity_aware_router"


@pytest.fixture(scope="module")
def mod():
    return pytest.importorskip(MODULE)


def test_module_imports_cleanly(mod):
    assert mod is not None


def test_all_exports_resolvable(mod):
    assert hasattr(mod, "__all__")
    missing = [n for n in mod.__all__ if not hasattr(mod, n)]
    assert not missing, f"__all__ leaks unresolved: {missing}"


@pytest.mark.parametrize("name", ["RoutingCapacityContext", "RoutingPolicyContext"])
def test_public_classes_present(mod, name):
    assert hasattr(mod, name)
    assert inspect.isclass(getattr(mod, name))


@pytest.mark.parametrize(
    "fn",
    [
        "choose_route_with_capacity",
        "choose_route_with_simple_capacity",
        "query_capacity_snapshots",
        "capacity_aware_routing",
        "route_chosen_with_capacity",
        "capacity_snapshot_emitted",
    ],
)
def test_public_functions_callable(mod, fn):
    assert hasattr(mod, fn)
    assert callable(getattr(mod, fn))
