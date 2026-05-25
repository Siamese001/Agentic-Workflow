"""Tests for Tier 1 span contract validator."""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    create_runtime_adg_snapshot,
)
from agentic_core.L6_system_learning.span_contracts import (
    Tier1Coverage,
    validate_tier1_coverage,
)


def _node(
    name: str,
    attrs_json: str = "{}",
    kind: str = "test",
    layer: str = "L2",
) -> RuntimeADGNode:
    return RuntimeADGNode(
        node_id=name.replace(".", "_"),
        name=name,
        kind=kind,
        layer=layer,
        component="X",
        started_at_utc=1,
        duration_ms=1.0,
        status="ok",
        attributes_json=attrs_json,
    )


def _snap(nodes: tuple[RuntimeADGNode, ...]):
    return create_runtime_adg_snapshot(
        trace_id="t",
        mission="m",
        started_at_utc=1,
        ended_at_utc=2,
        nodes=nodes,
        edges=(),
    )


class TestTier1Coverage:
    def test_empty_snapshot_has_zero_coverage(self) -> None:
        snap = _snap(())
        cov = validate_tier1_coverage(snap)
        assert cov.coverage_pct == 0.0
        assert not cov.is_complete()
        assert len(cov.missing_categories) == 5

    def test_all_five_categories_complete(self) -> None:
        """Each node must match by attrs OR 3-of-4 signals."""
        nodes = (
            _node("runtime.trace_root", '{"trace_id":"abc"}', layer="L0"),
            _node("L0.route.select", '{"selected_route":"R3"}', kind="router", layer="L0"),
            _node("L2.step.seal", '{"output_hash":"h1"}', layer="L2"),
            _node("L2.model.invoke", kind="model", layer="L2"),  # 3-sig no attrs
            _node("Exit.disposition", '{"exit_disposition":"allow"}', kind="exit", layer="L5"),
        )
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.is_complete(), (
            f"Expected complete, got {cov.coverage_pct}: missing={cov.missing_categories}"
        )

    def test_partial_coverage(self) -> None:
        nodes = (
            _node("runtime.trace_root", '{"trace_id":"abc"}', layer="L0"),
            _node("L2.tool.invoke", kind="tool", layer="L2"),  # 3-sig match
        )
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.coverage_pct == pytest.approx(0.4)
        assert "L0.route.select" in cov.missing_categories
        assert "L2.step.seal" in cov.missing_categories
        assert "Exit.disposition" in cov.missing_categories

    def test_category_present_but_missing_attrs(self) -> None:
        """Node name matches + layer but no attrs + no kind: 2 signals.
        That's present-at-signal-level but not full_hit (need attrs OR 3 sigs)."""
        nodes = (_node("L0.route.select", "{}", kind="test", layer="L0"),)
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.category_present["L0.route.select"] is True
        assert cov.category_with_attrs["L0.route.select"] is False
        assert cov.coverage_pct == 0.0

    def test_malformed_attributes_json_treated_as_missing(self) -> None:
        nodes = (_node("L2.step.seal", "this-is-not-json"),)
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.category_present["L2.step.seal"] is True
        assert cov.category_with_attrs["L2.step.seal"] is False

    def test_to_dict_serializable(self) -> None:
        cov = validate_tier1_coverage(_snap(()))
        d = cov.to_dict()
        assert set(d.keys()) == {
            "category_present",
            "category_with_attrs",
            "coverage_pct",
            "missing_categories",
            "is_complete",
        }

    def test_case_insensitive_name_matching(self) -> None:
        nodes = (_node("RUNTIME.TRACE_ROOT", '{"trace_id":"t"}', layer="L0"),)
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.category_with_attrs["runtime.trace_root"] is True

    def test_fuzzy_pattern_matching(self) -> None:
        """L0.route.select pattern 'router.' should match 'router.main.execute'."""
        nodes = (_node("router.main.execute", '{"selected_route":"R1B"}', kind="router", layer="L0"),)
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.category_with_attrs["L0.route.select"] is True

    def test_production_heal_router_matches_route_select(self) -> None:
        """The actual production span: heal_router.v1.route with routing.* attrs,
        kind=router, layer=L0. Must match L0.route.select via 4-signal hit."""
        nodes = (
            _node(
                "heal_router.v1.route",
                '{"routing.target_model":"gpt-4","routing.tier":"T2"}',
                kind="router",
                layer="L0",
            ),
        )
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.category_with_attrs["L0.route.select"] is True

    def test_production_consensus_matches_invoke(self) -> None:
        """consensus.v1.judge (L1 cognitive) — matches L2.invoke by name+kind+layer+attrs."""
        nodes = (
            _node(
                "consensus.v1.judge",
                '{"consensus.verdict":"pass","consensus.juror_count":5}',
                kind="cognitive",
                layer="L1",
            ),
        )
        cov = validate_tier1_coverage(_snap(nodes))
        assert cov.category_with_attrs["L2.invoke"] is True

    def test_single_signal_does_not_match(self) -> None:
        """A node that only matches by name — no kind, layer, or attrs support —
        falls below the 2-signal threshold and does NOT match."""
        nodes = (_node("exit.disposition", "{}", kind="unknown", layer="L99"),)
        cov = validate_tier1_coverage(_snap(nodes))
        # Only 1 signal (name); threshold=2. So category_present=False.
        assert cov.category_present["Exit.disposition"] is False


class TestCorpusTier1:
    def test_empty_corpus_all_gaps(self) -> None:
        from agentic_core.L6_system_learning.span_contracts import validate_tier1_corpus_coverage

        rep = validate_tier1_corpus_coverage([])
        assert rep.snapshots_scanned == 0
        assert rep.satisfied_pct == 0.0
        assert all(s == "emit_site_gap" for s in rep.category_status.values())

    def test_distinguishes_gap_from_name_mismatch(self) -> None:
        """One snapshot has a signal-hit-but-no-attrs node — should classify as
        name_mismatch, not emit_site_gap."""
        from agentic_core.L6_system_learning.span_contracts import validate_tier1_corpus_coverage

        # Signal hit for L0.route.select: name match + layer match, but no attrs.
        nodes = (_node("route.select", "{}", kind="test", layer="L0"),)
        rep = validate_tier1_corpus_coverage([_snap(nodes)])
        assert rep.category_status["L0.route.select"] == "name_mismatch"
        assert rep.category_status["runtime.trace_root"] == "emit_site_gap"

    def test_corpus_satisfies_with_real_production_shape(self) -> None:
        from agentic_core.L6_system_learning.span_contracts import validate_tier1_corpus_coverage

        nodes = (
            _node(
                "heal_router.v1.route",
                '{"routing.target_model":"x"}',
                kind="router",
                layer="L0",
            ),
        )
        rep = validate_tier1_corpus_coverage([_snap(nodes)])
        assert rep.category_status["L0.route.select"] == "satisfied"
        assert "heal_router.v1.route" in rep.category_example_hits["L0.route.select"]
        # Others remain as emit_site_gap.
        assert rep.category_status["runtime.trace_root"] == "emit_site_gap"
        assert rep.emit_site_gap_count() == 4
        assert rep.satisfied_count() == 1
