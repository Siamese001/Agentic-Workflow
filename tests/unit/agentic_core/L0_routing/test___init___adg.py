"""Behavioral contract tests for agentic_core.L0_routing.__init__."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.L0_routing.__init__"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_capacitydecisionreason_is_instantiable(mod):
    """CapacityDecisionReason is accessible and is a type."""
    cls = getattr(mod, "CapacityDecisionReason", None)
    assert cls is not None, "CapacityDecisionReason must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CapacityDecisionReason must be a class"


def test_capacitysnapshot_is_instantiable(mod):
    """CapacitySnapshot is accessible and is a type."""
    cls = getattr(mod, "CapacitySnapshot", None)
    assert cls is not None, "CapacitySnapshot must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CapacitySnapshot must be a class"


def test_optimizationwindow_is_instantiable(mod):
    """OptimizationWindow is accessible and is a type."""
    cls = getattr(mod, "OptimizationWindow", None)
    assert cls is not None, "OptimizationWindow must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "OptimizationWindow must be a class"


def test_policycontext_is_instantiable(mod):
    """PolicyContext is accessible and is a type."""
    cls = getattr(mod, "PolicyContext", None)
    assert cls is not None, "PolicyContext must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "PolicyContext must be a class"


def test_routecapacitymetrics_is_instantiable(mod):
    """RouteCapacityMetrics is accessible and is a type."""
    cls = getattr(mod, "RouteCapacityMetrics", None)
    assert cls is not None, "RouteCapacityMetrics must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RouteCapacityMetrics must be a class"


def test_routedegradationstate_is_instantiable(mod):
    """RouteDegradationState is accessible and is a type."""
    cls = getattr(mod, "RouteDegradationState", None)
    assert cls is not None, "RouteDegradationState must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RouteDegradationState must be a class"


def test_routingcapacitycontext_is_instantiable(mod):
    """RoutingCapacityContext is accessible and is a type."""
    cls = getattr(mod, "RoutingCapacityContext", None)
    assert cls is not None, "RoutingCapacityContext must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingCapacityContext must be a class"


def test_routingcapacityerror_is_instantiable(mod):
    """RoutingCapacityError is accessible and is a type."""
    cls = getattr(mod, "RoutingCapacityError", None)
    assert cls is not None, "RoutingCapacityError must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "RoutingCapacityError must be a class"


def test_apply_optimization_with_governance_is_callable(mod):
    """apply_optimization_with_governance is accessible and callable."""
    func = getattr(mod, "apply_optimization_with_governance", None)
    assert func is not None, "apply_optimization_with_governance must be defined in {MODULE_PATH}"
    assert callable(func), "apply_optimization_with_governance must be callable"


def test_capacity_aware_routing_is_callable(mod):
    """capacity_aware_routing is accessible and callable."""
    func = getattr(mod, "capacity_aware_routing", None)
    assert func is not None, "capacity_aware_routing must be defined in {MODULE_PATH}"
    assert callable(func), "capacity_aware_routing must be callable"


def test_capacity_snapshot_emitted_is_callable(mod):
    """capacity_snapshot_emitted is accessible and callable."""
    func = getattr(mod, "capacity_snapshot_emitted", None)
    assert func is not None, "capacity_snapshot_emitted must be defined in {MODULE_PATH}"
    assert callable(func), "capacity_snapshot_emitted must be callable"


def test_choose_route_with_capacity_is_callable(mod):
    """choose_route_with_capacity is accessible and callable."""
    func = getattr(mod, "choose_route_with_capacity", None)
    assert func is not None, "choose_route_with_capacity must be defined in {MODULE_PATH}"
    assert callable(func), "choose_route_with_capacity must be callable"


def test_choose_route_with_simple_capacity_is_callable(mod):
    """choose_route_with_simple_capacity is accessible and callable."""
    func = getattr(mod, "choose_route_with_simple_capacity", None)
    assert func is not None, "choose_route_with_simple_capacity must be defined in {MODULE_PATH}"
    assert callable(func), "choose_route_with_simple_capacity must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_get_capacity_registry_is_callable(mod):
    """get_capacity_registry is accessible and callable."""
    func = getattr(mod, "get_capacity_registry", None)
    assert func is not None, "get_capacity_registry must be defined in {MODULE_PATH}"
    assert callable(func), "get_capacity_registry must be callable"

