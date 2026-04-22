"""Regression coverage for antipattern routing in RepairRoute.

Plan: .windsurf/plans/antipattern-reclassify-e5a569.md Wave 4 (Priority 5).

Confirms that the 4 HIGH-severity exception antipatterns are wired into
``_RELATION_TO_ROUTE`` and that ``route_violations`` produces RepairRoute
entries for them via the ``edge.edge_kind`` fallback lookup
(``relation_type='antipattern'`` is not a direct key; the edge_kind is).
"""

from __future__ import annotations

import pytest

from agentic_core.adg.analysis.RepairRoute import (
    _RELATION_TO_ROUTE,
    RepairRoute,
    route_violations,
)
from agentic_core.adg.extraction.static_scanner import Edge

ANTIPATTERN_EDGE_KINDS: tuple[str, ...] = (
    "broad_exception_catch",
    "silent_exception_swallow",
    "log_and_swallow",
    "return_none_swallow",
)


@pytest.mark.parametrize("edge_kind", ANTIPATTERN_EDGE_KINDS)
def test_antipattern_edge_kind_is_registered(edge_kind: str) -> None:
    """Each of the 4 HIGH-severity antipattern edge_kinds must be routed."""
    assert edge_kind in _RELATION_TO_ROUTE, (
        f"{edge_kind} missing from _RELATION_TO_ROUTE — "
        "regressed the antipattern-reclassify W2 wiring"
    )


@pytest.mark.parametrize("edge_kind", ANTIPATTERN_EDGE_KINDS)
def test_antipattern_route_shape(edge_kind: str) -> None:
    """Each antipattern must route to ManualReview / governance / high."""
    agent, lane, severity, description = _RELATION_TO_ROUTE[edge_kind]
    assert agent == "ManualReview"
    assert lane == "governance"
    assert severity == "high"
    assert description, "description must be non-empty"


def _make_edge(edge_kind: str, *, relation_type: str = "antipattern") -> Edge:
    return Edge(
        from_name="pkg.mod",
        relation_type=relation_type,
        to_name="builtins.Exception",
        edge_kind=edge_kind,
        source_file="agentic_core/L0_routing/reasoning/sample.py",
        line_no=42,
        symbol="except:Exception",
    )


@pytest.mark.parametrize("edge_kind", ANTIPATTERN_EDGE_KINDS)
def test_route_violations_emits_route_for_each_antipattern(edge_kind: str) -> None:
    """route_violations must produce exactly one RepairRoute per antipattern edge."""
    routes = route_violations([_make_edge(edge_kind)])
    assert len(routes) == 1
    route = routes[0]
    assert isinstance(route, RepairRoute)
    assert route.severity == "high"
    assert route.recommended_agent == "ManualReview"
    assert route.ci_lane == "governance"
    assert route.violation_type == "antipattern"


def test_route_violations_via_edge_kind_fallback() -> None:
    """route_violations falls back to edge_kind when relation_type is not a key.

    ``relation_type='antipattern'`` is NOT a direct key in _RELATION_TO_ROUTE.
    The edge_kind-based fallback at RepairRoute.py line 160 is what makes
    antipattern routing work. This test guards that fallback.
    """
    edge = _make_edge("broad_exception_catch", relation_type="antipattern")
    assert "antipattern" not in _RELATION_TO_ROUTE, (
        "if 'antipattern' ever becomes a direct key, this test must be revisited"
    )
    routes = route_violations([edge])
    assert len(routes) == 1
    assert routes[0].severity == "high"


def test_route_violations_skips_unknown_edge_kinds() -> None:
    """Edges with neither known relation_type nor known edge_kind are skipped."""
    edge = Edge(
        from_name="pkg.mod",
        relation_type="unknown_relation",
        to_name="pkg.other",
        edge_kind="unknown_edge_kind",
        source_file="agentic_core/L0_routing/reasoning/sample.py",
        line_no=1,
    )
    assert route_violations([edge]) == []
