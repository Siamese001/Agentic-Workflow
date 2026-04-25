"""Behavioral tests for L4_state/enforcement/blast_radius.py.

Covers:
- BlastRadiusMetrics dataclass (frozen).
- BlastRadiusCalculator: counts objects/bytes/depth/cross-layer, enforces limits.
- BlastRadiusEnforcer: tracks proposals, rejects duplicates, aggregates totals.
- Module-level exports: enforce_blast_radius, get_proposal_metrics, clear_proposal,
  validate_total_impact — wire through the singleton _blast_enforcer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from agentic_core.L4_state.enforcement import blast_radius as mod
from agentic_core.L4_state.enforcement.blast_radius import (
    BlastRadiusCalculator,
    BlastRadiusEnforcer,
    BlastRadiusMetrics,
    clear_proposal,
    enforce_blast_radius,
    get_proposal_metrics,
    validate_total_impact,
)


@pytest.fixture(autouse=True)
def _reset_singleton() -> None:
    """Each test gets a clean _blast_enforcer."""
    mod._blast_enforcer._active_proposals.clear()


@dataclass
class _FakeProposal:
    name: str = "fake"
    priority: int = 1


# ---- BlastRadiusMetrics ---------------------------------------------


class TestBlastRadiusMetrics:
    def test_frozen(self) -> None:
        m = BlastRadiusMetrics(
            total_affected_objects=1,
            state_surface_bytes=10,
            mutation_depth=1,
            cross_layer_impacts=0,
        )
        with pytest.raises((AttributeError, Exception)):
            m.total_affected_objects = 99  # type: ignore[misc]


# ---- BlastRadiusCalculator ------------------------------------------


class TestBlastRadiusCalculator:
    def test_count_affected_objects_dataclass(self) -> None:
        c = BlastRadiusCalculator()
        assert c._count_affected_objects(_FakeProposal()) == 2

    def test_count_affected_objects_list(self) -> None:
        assert BlastRadiusCalculator()._count_affected_objects([1, 2, 3]) == 3

    def test_count_affected_objects_dict(self) -> None:
        assert BlastRadiusCalculator()._count_affected_objects({"a": 1}) == 1

    def test_count_affected_objects_scalar(self) -> None:
        assert BlastRadiusCalculator()._count_affected_objects(42) == 1

    def test_estimate_state_surface_positive(self) -> None:
        assert BlastRadiusCalculator()._estimate_state_surface(_FakeProposal()) > 0

    def test_mutation_depth_scalar(self) -> None:
        assert BlastRadiusCalculator()._calculate_mutation_depth(42) == 1

    def test_mutation_depth_nested_list(self) -> None:
        depth = BlastRadiusCalculator()._calculate_mutation_depth([[1, 2], [3, 4]])
        assert depth >= 2

    def test_mutation_depth_capped_at_5(self) -> None:
        assert BlastRadiusCalculator()._calculate_mutation_depth({}) <= 5

    def test_count_cross_layer_impacts_detects_layers(self) -> None:
        c = BlastRadiusCalculator()
        n = c._count_cross_layer_impacts(
            {"targets": "l0_routing, l5_safety, l6_observability"},
        )
        assert n == 3

    def test_count_cross_layer_impacts_none(self) -> None:
        assert BlastRadiusCalculator()._count_cross_layer_impacts("no layers") == 0

    def test_calculate_returns_metrics(self) -> None:
        metrics = BlastRadiusCalculator().calculate_blast_radius(_FakeProposal())
        assert isinstance(metrics, BlastRadiusMetrics)
        assert metrics.total_affected_objects >= 0
        assert metrics.state_surface_bytes > 0

    def test_calculate_rejects_over_max_radius(self) -> None:
        c = BlastRadiusCalculator(max_radius=1)
        with pytest.raises(ValueError, match="exceeds maximum"):
            c.calculate_blast_radius([1, 2, 3, 4, 5])

    def test_calculate_rejects_over_max_bytes(self) -> None:
        c = BlastRadiusCalculator(max_bytes=1)
        with pytest.raises(ValueError, match="exceeds maximum"):
            c.calculate_blast_radius("x" * 1000)


# ---- BlastRadiusEnforcer --------------------------------------------


class TestBlastRadiusEnforcer:
    def test_enforce_stores_metrics(self) -> None:
        e = BlastRadiusEnforcer()
        metrics = e.enforce_blast_radius("p1", _FakeProposal())
        assert e.get_proposal_metrics("p1") is metrics

    def test_enforce_rejects_duplicate(self) -> None:
        e = BlastRadiusEnforcer()
        e.enforce_blast_radius("p1", _FakeProposal())
        with pytest.raises(RuntimeError, match="already exists"):
            e.enforce_blast_radius("p1", _FakeProposal())

    def test_get_unknown_returns_none(self) -> None:
        assert BlastRadiusEnforcer().get_proposal_metrics("ghost") is None

    def test_clear_removes(self) -> None:
        e = BlastRadiusEnforcer()
        e.enforce_blast_radius("p1", _FakeProposal())
        e.clear_proposal("p1")
        assert e.get_proposal_metrics("p1") is None

    def test_clear_unknown_is_noop(self) -> None:
        BlastRadiusEnforcer().clear_proposal("ghost")  # no raise

    def test_get_total_blast_radius_sums(self) -> None:
        e = BlastRadiusEnforcer()
        e.enforce_blast_radius("p1", {"a": 1, "b": 2})
        e.enforce_blast_radius("p2", [1, 2, 3])
        # dict with 2 items + list with 3 = 5
        assert e.get_total_blast_radius() == 5

    def test_validate_total_impact_ok(self) -> None:
        e = BlastRadiusEnforcer()
        e.enforce_blast_radius("p1", _FakeProposal())
        assert e.validate_total_impact() is True

    def test_validate_total_impact_over_radius(self) -> None:
        e = BlastRadiusEnforcer(BlastRadiusCalculator(max_radius=100))
        e.enforce_blast_radius("p1", list(range(50)))
        e.enforce_blast_radius("p2", list(range(60)))
        with pytest.raises(ValueError, match="Total blast radius"):
            e.validate_total_impact()


# ---- Module-level exports -------------------------------------------


class TestModuleExports:
    def test_enforce_and_get(self) -> None:
        m = enforce_blast_radius("p1", _FakeProposal())
        assert get_proposal_metrics("p1") is m

    def test_clear_module_level(self) -> None:
        enforce_blast_radius("p1", _FakeProposal())
        clear_proposal("p1")
        assert get_proposal_metrics("p1") is None

    def test_validate_total_impact_module_level(self) -> None:
        enforce_blast_radius("p1", _FakeProposal())
        assert validate_total_impact() is True
