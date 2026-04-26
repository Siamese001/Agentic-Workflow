"""Tests for candidate_pool (C0.2) and hydration (C0.2A)."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval import (
    CandidateChunk,
    CandidateEvidencePool,
    HydrationManifest,
    RetrievalScores,
    SourceClass,
    normalize_pool,
)
from agentic_core.L0_routing.c0_retrieval.hydration import (
    ChunkBoundaryRisk,
    QualityFlags,
    _classify_boundary_risk,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import RetrievalLane
from tests.agentic_core.L0_routing.c0_retrieval._factories import make_chunk, make_pool


class TestRetrievalScores:
    def test_default(self):
        s = RetrievalScores()
        assert s.normalized_score == 0.0

    def test_normalized_range(self):
        with pytest.raises(ValueError):
            RetrievalScores(normalized_score=1.5)

    def test_negative_rank_rejected(self):
        with pytest.raises(ValueError):
            RetrievalScores(rank=-1)


class TestHydrationManifest:
    def test_requires_source_id(self):
        with pytest.raises(ValueError):
            HydrationManifest(source_id="   ")

    def test_invalid_line_range(self):
        with pytest.raises(ValueError):
            HydrationManifest(source_id="x", line_range=(10, 5))

    def test_zero_line_range_ok(self):
        m = HydrationManifest(source_id="x", line_range=(0, 0))
        assert m.line_range == (0, 0)


class TestCandidateChunk:
    def test_lane_provenance_required_C0_I3(self):
        m = HydrationManifest(source_id="x")
        with pytest.raises(ValueError, match="C0.I3"):
            CandidateChunk(
                chunk_id="c1", source_class=SourceClass.DOCS,
                text="x", manifest=m, found_by_lanes=(),
            )

    def test_chunk_id_required(self):
        with pytest.raises(ValueError):
            make_chunk(chunk_id="   ")

    def test_text_required(self):
        with pytest.raises(ValueError):
            make_chunk(text="")


class TestCandidateEvidencePool:
    def test_empty_pool(self):
        p = make_pool()
        assert p.candidates == ()

    def test_lanes_in_lanes_used(self):
        c = make_chunk(found_by_lanes=(RetrievalLane.SPARSE,))
        # Pool with lanes_used not including SPARSE should reject.
        with pytest.raises(ValueError, match="not in pool.lanes_used"):
            CandidateEvidencePool(
                plan_id="p1", candidates=(c,),
                lanes_used=(RetrievalLane.DENSE,),
            )

    def test_by_source_filter(self):
        a = make_chunk(chunk_id="a", source_class=SourceClass.DOCS)
        b = make_chunk(chunk_id="b", source_class=SourceClass.CODE)
        p = make_pool((a, b))
        assert len(p.by_source(SourceClass.DOCS)) == 1
        assert len(p.by_source(SourceClass.CODE)) == 1

    def test_by_lane_filter(self):
        a = make_chunk(chunk_id="a", found_by_lanes=(RetrievalLane.SPARSE,))
        b = make_chunk(chunk_id="b", found_by_lanes=(RetrievalLane.DENSE,))
        p = make_pool((a, b), lanes_used=(RetrievalLane.SPARSE, RetrievalLane.DENSE))
        assert len(p.by_lane(RetrievalLane.SPARSE)) == 1


class TestQualityFlags:
    def test_all_green(self):
        q = QualityFlags(
            span_resolves=True,
            source_version_current=True,
            acl_clear=True,
            parent_context_available=True,
            citation_anchor_stable=True,
            chunk_boundary_risk=ChunkBoundaryRisk.LOW,
        )
        assert q.all_green() is True

    def test_not_all_green_on_high_risk(self):
        q = QualityFlags(
            span_resolves=True, source_version_current=True, acl_clear=True,
            parent_context_available=True, citation_anchor_stable=True,
            chunk_boundary_risk=ChunkBoundaryRisk.HIGH,
        )
        assert q.all_green() is False


class TestBoundaryRiskClassifier:
    def test_terminal_punct_low(self):
        assert _classify_boundary_risk("Hello world.") == ChunkBoundaryRisk.LOW

    def test_comma_medium(self):
        assert _classify_boundary_risk("hello,") == ChunkBoundaryRisk.MEDIUM

    def test_no_terminator_high(self):
        assert _classify_boundary_risk("hello world") == ChunkBoundaryRisk.HIGH

    def test_empty_high(self):
        assert _classify_boundary_risk("") == ChunkBoundaryRisk.HIGH


class TestNormalizePool:
    def test_normal_pool(self):
        c = make_chunk()
        p = make_pool((c,))
        out = normalize_pool(p, tenant="tenantA")
        assert len(out.hydrated) == 1
        assert out.hydration_failures == ()
        assert out.hydrated[0].canonical_source_path == "docs/c0.md"

    def test_chunk_with_no_canonical_path_rejected(self):
        m = HydrationManifest(source_id="x")  # no file_path/url/doc_id
        c = CandidateChunk(
            chunk_id="c1", source_class=SourceClass.DOCS,
            text="hello.", manifest=m,
            found_by_lanes=(RetrievalLane.DENSE,),
        )
        p = CandidateEvidencePool(
            plan_id="p1", candidates=(c,), lanes_used=(RetrievalLane.DENSE,),
        )
        out = normalize_pool(p, tenant="tenantA")
        assert len(out.hydrated) == 0
        assert len(out.hydration_failures) == 1

    def test_acl_clear_when_tenant_match(self):
        c = make_chunk(tenant="tenantA")
        p = make_pool((c,))
        out = normalize_pool(p, tenant="tenantA")
        assert out.hydrated[0].quality.acl_clear is True

    def test_acl_blocked_when_tenant_mismatch(self):
        c = make_chunk(tenant="other")
        p = make_pool((c,))
        out = normalize_pool(p, tenant="tenantA")
        assert out.hydrated[0].quality.acl_clear is False

    def test_all_green_chunks_filter(self):
        c = make_chunk()
        p = make_pool((c,))
        out = normalize_pool(p, tenant="tenantA")
        green = out.all_green_chunks()
        assert isinstance(green, tuple)
