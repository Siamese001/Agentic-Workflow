"""Tests for C0.5 EvidenceContract — verify_and_score + status decision."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval import (
    GraphBounds,
    SupportStatus,
    SupportTarget,
    expand_graph,
    normalize_pool,
    scan_conflicts_and_gaps,
    shape_pool,
    verify_and_score,
)
from agentic_core.L0_routing.c0_retrieval.evidence_contract import (
    EvidenceContract,
    ScoreBreakdown,
)
from tests.agentic_core.L0_routing.c0_retrieval._factories import make_chunk, make_pool


def _pipeline(chunks, target=SupportTarget.SOURCE_SUMMARY):
    h = normalize_pool(make_pool(chunks), tenant="tenantA")
    ex = expand_graph(h, bounds=GraphBounds(max_hops=0), adjacency=lambda n, r: ())
    cg = scan_conflicts_and_gaps(ex, target=target)
    shaped = shape_pool(
        ex, target=target, max_token_context=4000,
        contradiction_chunk_ids=cg.contradiction_chunk_ids(),
    )
    return shaped, cg


class TestScoreBreakdown:
    def test_all_zero_default(self):
        # Default acl_confidence=1.0 contributes 0.10 to aggregate; everything
        # else defaults to 0.0. So a fully-default ScoreBreakdown aggregates
        # to ~0.10, not 0.0.
        sb = ScoreBreakdown()
        assert sb.aggregate() == pytest.approx(0.10, abs=1e-6)

    def test_range_validation(self):
        with pytest.raises(ValueError):
            ScoreBreakdown(direct_support_score=1.5)

    def test_aggregate_clamped(self):
        sb = ScoreBreakdown(
            direct_support_score=1.0, coverage_score=1.0, source_authority_score=1.0,
            freshness_score=1.0, citation_stability_score=1.0, lineage_quality_score=1.0,
            exactness_score=1.0, source_diversity_score=1.0, acl_confidence=1.0,
            contradiction_risk=0.0, unsupported_inference_risk=0.0,
        )
        agg = sb.aggregate()
        assert 0.0 <= agg <= 1.0

    def test_risk_penalizes(self):
        sb_low = ScoreBreakdown(direct_support_score=0.8, coverage_score=0.8)
        sb_high = ScoreBreakdown(
            direct_support_score=0.8, coverage_score=0.8,
            contradiction_risk=1.0, unsupported_inference_risk=1.0,
        )
        assert sb_low.aggregate() > sb_high.aggregate()


class TestEvidenceContractValidation:
    def _base_kwargs(self, **over):
        kw = {
            "plan_id": "p1",
            "request_id": "r1",
            "status": SupportStatus.PASS,
            "support_score": 0.5,
            "score_breakdown": ScoreBreakdown(),
            "verified_chunk_ids": ("c1",),
            "cited_span_refs": ("docs/x.md#line:1-3",),
            "source_ids": ("docs/x.md",),
            "evidence_hmac": "abc",
        }
        kw.update(over)
        return kw

    def test_valid(self):
        ec = EvidenceContract(**self._base_kwargs())
        assert ec.status == SupportStatus.PASS

    def test_empty_plan_id_rejected(self):
        with pytest.raises(ValueError):
            EvidenceContract(**self._base_kwargs(plan_id="  "))

    def test_score_range(self):
        with pytest.raises(ValueError):
            EvidenceContract(**self._base_kwargs(support_score=2.0))

    def test_pass_requires_verified_chunks(self):
        with pytest.raises(ValueError):
            EvidenceContract(**self._base_kwargs(verified_chunk_ids=()))

    def test_missing_hmac_rejected(self):
        with pytest.raises(ValueError):
            EvidenceContract(**self._base_kwargs(evidence_hmac=""))

    def test_pass_cannot_carry_abstain_hint(self):
        with pytest.raises(ValueError):
            EvidenceContract(**self._base_kwargs(abstain_hint=True))


class TestHmacStability:
    def test_same_inputs_same_hmac(self):
        a = EvidenceContract.compute_hmac("p1", "r1", ["c1"], ScoreBreakdown())
        b = EvidenceContract.compute_hmac("p1", "r1", ["c1"], ScoreBreakdown())
        assert a == b

    def test_different_chunks_different_hmac(self):
        a = EvidenceContract.compute_hmac("p1", "r1", ["c1"], ScoreBreakdown())
        b = EvidenceContract.compute_hmac("p1", "r1", ["c2"], ScoreBreakdown())
        assert a != b


class TestVerifyAndScore:
    def test_empty_pool_emits_empty_status(self):
        shaped, cg = _pipeline(())
        ec = verify_and_score(
            shaped, request_id="r1",
            target=SupportTarget.SOURCE_SUMMARY, conflict_report=cg,
        )
        assert ec.status == SupportStatus.EMPTY

    def test_single_chunk_yields_some_support(self):
        c = make_chunk()
        shaped, cg = _pipeline((c,))
        ec = verify_and_score(
            shaped, request_id="r1",
            target=SupportTarget.SOURCE_SUMMARY, conflict_report=cg,
        )
        assert ec.status in (
            SupportStatus.PASS, SupportStatus.WEAK,
            SupportStatus.WEAK_WITH_CAVEATS,
        )
        assert ec.evidence_hmac

    def test_disposition_set(self):
        c = make_chunk()
        shaped, cg = _pipeline((c,))
        ec = verify_and_score(
            shaped, request_id="r1",
            target=SupportTarget.SOURCE_SUMMARY, conflict_report=cg,
        )
        # Disposition is a valid enum value
        from agentic_core.L0_routing.c0_retrieval import RecommendedDisposition
        assert isinstance(ec.recommended_disposition, RecommendedDisposition)
