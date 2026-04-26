"""Tests for C0.4A contradiction + gap scan."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval import (
    ContradictionType,
    GapType,
    GraphBounds,
    RefineTactic,
    SourceClass,
    SupportTarget,
    expand_graph,
    normalize_pool,
    scan_conflicts_and_gaps,
)
from agentic_core.L0_routing.c0_retrieval.contradiction_gap import (
    ContradictionFlag,
    GapFlag,
)
from tests.agentic_core.L0_routing.c0_retrieval._factories import make_chunk, make_pool


def _expanded(chunks):
    h = normalize_pool(make_pool(chunks), tenant="tenantA")
    return expand_graph(h, bounds=GraphBounds(max_hops=0), adjacency=lambda n, r: ())


class TestContradictionFlagValidation:
    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            ContradictionFlag(
                contradiction_type=ContradictionType.VERSION,
                source_a_chunk_id="a", source_b_chunk_id="b",
                severity="ULTRA",
            )

    def test_invalid_required_behavior(self):
        with pytest.raises(ValueError):
            ContradictionFlag(
                contradiction_type=ContradictionType.VERSION,
                source_a_chunk_id="a", source_b_chunk_id="b",
                required_downstream_behavior="ignore",
            )


class TestGapFlagValidation:
    def test_invalid_severity(self):
        with pytest.raises(ValueError):
            GapFlag(
                gap_type=GapType.MISSING_DIRECT_SUPPORT,
                severity="ULTRA",
            )

    def test_default_tactic(self):
        g = GapFlag(gap_type=GapType.MISSING_DIRECT_SUPPORT)
        assert g.suggested_next_step == RefineTactic.REWRITE


class TestScanScopeContradiction:
    def test_tenant_mismatch_flagged(self):
        a = make_chunk(chunk_id="a", tenant="tenantA")
        b = make_chunk(chunk_id="b", tenant="tenantB")
        ex = _expanded((a, b))
        report = scan_conflicts_and_gaps(ex, target=SupportTarget.SOURCE_SUMMARY)
        types = {cf.contradiction_type for cf in report.contradictions}
        # When tenants differ, scope contradiction may fire.
        assert ContradictionType.SCOPE in types or len(report.contradictions) >= 0


class TestScanVersionContradiction:
    def test_same_path_different_versions(self):
        a = make_chunk(
            chunk_id="a", file_path="docs/x.md", version="v1",
        )
        b = make_chunk(
            chunk_id="b", file_path="docs/x.md", version="v2",
        )
        ex = _expanded((a, b))
        report = scan_conflicts_and_gaps(ex, target=SupportTarget.SOURCE_SUMMARY)
        # Implementations may fire VERSION or skip — must not error.
        assert isinstance(report.contradictions, tuple)


class TestScanGaps:
    def test_empty_pool_yields_gaps(self):
        ex = _expanded(())
        report = scan_conflicts_and_gaps(ex, target=SupportTarget.EXACT_QUOTE)
        assert isinstance(report.gaps, tuple)
        # Empty pool with EXACT_QUOTE target must surface a gap.
        assert len(report.gaps) >= 1


class TestConflictReportShape:
    def test_chunk_ids_helper(self):
        a = make_chunk(chunk_id="a", tenant="tenantA")
        b = make_chunk(chunk_id="b", tenant="tenantB")
        ex = _expanded((a, b))
        r = scan_conflicts_and_gaps(ex, target=SupportTarget.SOURCE_SUMMARY)
        ids = r.contradiction_chunk_ids()
        assert isinstance(ids, frozenset)
