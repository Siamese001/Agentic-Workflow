"""Tests for antipattern edge_kind routing in RepairRoute._RELATION_TO_ROUTE.

Verifies that the 4 newly wired antipattern edge_kinds produce repair routes
with severity=high and ci_lane=governance, and that route_violations() correctly
picks them up via the edge_kind fallback lookup.
"""

from __future__ import annotations

import pytest

from agentic_core.adg.analysis.RepairRoute import (
    _RELATION_TO_ROUTE,
    repair_routing_summary,
    route_violations,
)
from agentic_core.adg.extraction.static_scanner import Edge

_HIGH_ANTIPATTERN_KINDS = [
    "broad_exception_catch",
    "silent_exception_swallow",
    "log_and_swallow",
    "return_none_swallow",
]

_LOW_ANTIPATTERN_KINDS = [
    "retry_without_backoff",
    "blocking_call_in_async",
    "global_state_mutation",
]


def _make_antipattern_edge(edge_kind: str, source_file: str = "agentic_core/L0_routing/foo.py") -> Edge:
    return Edge(
        from_name="ADG::Module::agentic_core/L0_routing/foo",
        relation_type="antipattern",
        to_name="ADG::AntipatternCategory::broad_exception_catch",
        edge_kind=edge_kind,
        source_file=source_file,
        line_no=42,
        symbol="except:Exception",
    )


@pytest.mark.parametrize("edge_kind", _HIGH_ANTIPATTERN_KINDS)
def test_high_antipattern_kinds_in_relation_to_route(edge_kind: str) -> None:
    """Each high-severity antipattern edge_kind must be present in _RELATION_TO_ROUTE."""
    assert edge_kind in _RELATION_TO_ROUTE, f"{edge_kind!r} missing from _RELATION_TO_ROUTE"


@pytest.mark.parametrize("edge_kind", _HIGH_ANTIPATTERN_KINDS)
def test_high_antipattern_kinds_have_correct_severity(edge_kind: str) -> None:
    """High antipattern edge_kinds must map to severity=high."""
    _agent, _lane, severity, _desc = _RELATION_TO_ROUTE[edge_kind]
    assert severity == "high", f"{edge_kind!r} should be 'high', got {severity!r}"


@pytest.mark.parametrize("edge_kind", _HIGH_ANTIPATTERN_KINDS)
def test_high_antipattern_kinds_route_to_governance_lane(edge_kind: str) -> None:
    """High antipattern edge_kinds must route to the governance CI lane."""
    _agent, lane, _severity, _desc = _RELATION_TO_ROUTE[edge_kind]
    assert lane == "governance", f"{edge_kind!r} should be lane='governance', got {lane!r}"


@pytest.mark.parametrize("edge_kind", _HIGH_ANTIPATTERN_KINDS)
def test_route_violations_picks_up_antipattern_via_edge_kind_fallback(edge_kind: str) -> None:
    """route_violations() must return a route for antipattern edges via edge_kind fallback."""
    edge = _make_antipattern_edge(edge_kind)
    routes = route_violations([edge])
    assert len(routes) == 1, f"Expected 1 route for {edge_kind!r}, got {len(routes)}"
    assert routes[0].severity == "high"
    assert routes[0].ci_lane == "governance"
    assert routes[0].source_file == "agentic_core/L0_routing/foo.py"


def test_routing_summary_counts_high_antipatterns() -> None:
    """repair_routing_summary must aggregate HIGH counts from antipattern routes."""
    edges = [_make_antipattern_edge(k) for k in _HIGH_ANTIPATTERN_KINDS]
    routes = route_violations(edges)
    summary = repair_routing_summary(routes)
    assert summary["by_severity"].get("high", 0) == len(_HIGH_ANTIPATTERN_KINDS)


@pytest.mark.parametrize("edge_kind", _LOW_ANTIPATTERN_KINDS)
def test_low_antipattern_kinds_not_in_relation_to_route(edge_kind: str) -> None:
    """False-positive-prone antipattern kinds must NOT be in _RELATION_TO_ROUTE (stay LOW/invisible to routing)."""
    assert edge_kind not in _RELATION_TO_ROUTE, (
        f"{edge_kind!r} should NOT be in _RELATION_TO_ROUTE — it is false-positive-prone"
    )


@pytest.mark.parametrize("edge_kind", _LOW_ANTIPATTERN_KINDS)
def test_route_violations_ignores_low_antipattern_kinds(edge_kind: str) -> None:
    """route_violations() must produce no route for false-positive-prone antipattern kinds."""
    edge = _make_antipattern_edge(edge_kind)
    routes = route_violations([edge])
    assert len(routes) == 0, f"Expected 0 routes for {edge_kind!r}, got {len(routes)}"


def test_existing_layer_violation_routing_unchanged() -> None:
    """Existing violates→critical routing must not be affected by antipattern additions."""
    assert "violates" in _RELATION_TO_ROUTE
    _agent, ci_lane, severity, _desc = _RELATION_TO_ROUTE["violates"]
    assert severity == "critical"
    assert ci_lane == "layer_guard"


def test_existing_dynamic_exec_routing_unchanged() -> None:
    """Existing dynamic_exec→high routing must not be affected by antipattern additions."""
    assert "dynamic_exec" in _RELATION_TO_ROUTE
    _agent, ci_lane, severity, _desc = _RELATION_TO_ROUTE["dynamic_exec"]
    assert severity == "high"
    assert ci_lane == "dynamic_exec"
