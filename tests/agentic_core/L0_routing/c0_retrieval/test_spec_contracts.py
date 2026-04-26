"""Tests for C0.1-C0.5 spec-grade typed contracts (additive surface).

Spec sources: ``docs/reference/03_L0_Routing/C0 - Context Engine/`` —
the C0.1 / C0.2 / C0.4 / C0.5 detailed implementation contracts.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.c0_retrieval.spec_contracts import (
    CitationPrecision,
    CitationSupportMap,
    EvidenceFingerprint,
    EvidenceGapReportV2,
    ExcludedEvidenceItem,
    ExclusionReason,
    LaneFailureBehavior,
    LaneTimeoutStatus,
    RawHit,
    RetrievalLaneResult,
    RetrievalModePlan,
    SourceAuthorityClass,
    SourceClassDecision,
    SourceDecision,
    SupportScoreBreakdownV2,
    SupportTargetProfile,
    UnsupportedInferencePolicy,
    compute_pool_manifest_hash,
    compute_profile_hash,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    GraphRelation,
    RetrievalLane,
    SourceClass,
    SupportTarget,
)


# ---------------------------------------------------------------------------
# C0.1 — SupportTargetProfile.
# ---------------------------------------------------------------------------
class TestSupportTargetProfile:
    def test_minimal_profile_constructs(self):
        p = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        assert p.support_target_id == "t-1"
        assert p.requires_dense_support
        assert p.unsupported_inference_policy is UnsupportedInferencePolicy.CAVEAT

    def test_exact_quote_requires_direct_quote_required(self):
        with pytest.raises(ValueError, match="direct_quote_required=True"):
            SupportTargetProfile(
                support_target_id="t-q",
                support_target_type=SupportTarget.EXACT_QUOTE,
                direct_quote_required=False,
                requires_sparse_support=True,
            )

    def test_exact_quote_requires_sparse_support(self):
        with pytest.raises(ValueError, match="requires_sparse_support=True"):
            SupportTargetProfile(
                support_target_id="t-q",
                support_target_type=SupportTarget.EXACT_QUOTE,
                direct_quote_required=True,
                requires_sparse_support=False,
            )

    def test_exact_quote_valid_combination(self):
        p = SupportTargetProfile(
            support_target_id="t-q",
            support_target_type=SupportTarget.EXACT_QUOTE,
            direct_quote_required=True,
            requires_sparse_support=True,
            required_citation_precision=CitationPrecision.SPAN_EXACT,
        )
        assert p.required_citation_precision is CitationPrecision.SPAN_EXACT

    def test_policy_clause_requires_section_or_better_precision(self):
        with pytest.raises(ValueError, match="POLICY_CLAUSE.*section"):
            SupportTargetProfile(
                support_target_id="t-p",
                support_target_type=SupportTarget.POLICY_CLAUSE,
                required_citation_precision=CitationPrecision.NONE,
            )

    def test_code_location_requires_exact_symbol(self):
        with pytest.raises(ValueError, match="CODE_LOCATION.*exact_symbol_required"):
            SupportTargetProfile(
                support_target_id="t-c",
                support_target_type=SupportTarget.CODE_LOCATION,
                exact_symbol_required=False,
            )

    def test_min_independent_sources_must_be_positive(self):
        with pytest.raises(ValueError, match="min_independent_sources"):
            SupportTargetProfile(
                support_target_id="t-1",
                support_target_type=SupportTarget.SOURCE_SUMMARY,
                min_independent_sources=0,
            )

    def test_profile_hash_deterministic(self):
        p1 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        p2 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        assert compute_profile_hash(p1) == compute_profile_hash(p2)

    def test_profile_hash_changes_with_id(self):
        p1 = SupportTargetProfile(
            support_target_id="t-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        p2 = SupportTargetProfile(
            support_target_id="t-2",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
        )
        assert compute_profile_hash(p1) != compute_profile_hash(p2)


# ---------------------------------------------------------------------------
# C0.1 — SourceClassDecision.
# ---------------------------------------------------------------------------
class TestSourceClassDecision:
    def test_include_decision_no_reason_required(self):
        d = SourceClassDecision(
            source_class=SourceClass.DOCS,
            decision=SourceDecision.INCLUDE,
        )
        assert d.decision is SourceDecision.INCLUDE

    def test_exclude_requires_reason_codes(self):
        with pytest.raises(ValueError, match="EXCLUDE requires reason_codes"):
            SourceClassDecision(
                source_class=SourceClass.LOGS,
                decision=SourceDecision.EXCLUDE,
            )

    def test_exclude_with_reason_constructs(self):
        d = SourceClassDecision(
            source_class=SourceClass.LOGS,
            decision=SourceDecision.EXCLUDE,
            reason_codes=("acl_blocked",),
            risk_notes=("audit-only data class",),
        )
        assert "acl_blocked" in d.reason_codes


# ---------------------------------------------------------------------------
# C0.1 — RetrievalModePlan.
# ---------------------------------------------------------------------------
class TestRetrievalModePlan:
    def test_minimal_plan_constructs(self):
        plan = RetrievalModePlan(
            lane_id="dense-1",
            lane_type=RetrievalLane.DENSE,
            enabled=True,
        )
        assert plan.failure_behavior is LaneFailureBehavior.SKIP_LANE

    def test_empty_lane_id_rejected(self):
        with pytest.raises(ValueError, match="lane_id required"):
            RetrievalModePlan(
                lane_id="",
                lane_type=RetrievalLane.DENSE,
                enabled=True,
            )

    def test_invalid_top_k_rejected(self):
        with pytest.raises(ValueError, match="top_k must be positive"):
            RetrievalModePlan(
                lane_id="x",
                lane_type=RetrievalLane.DENSE,
                enabled=True,
                top_k=0,
            )

    def test_invalid_score_floor_rejected(self):
        with pytest.raises(ValueError, match="score_floor"):
            RetrievalModePlan(
                lane_id="x",
                lane_type=RetrievalLane.DENSE,
                enabled=True,
                score_floor=1.5,
            )

    def test_graph_seed_with_exactness_required_rejected(self):
        with pytest.raises(ValueError, match="graph_seed.*exactness_required"):
            RetrievalModePlan(
                lane_id="g-1",
                lane_type=RetrievalLane.GRAPH_SEED,
                enabled=True,
                exactness_required=True,
            )


# ---------------------------------------------------------------------------
# C0.2 — RetrievalLaneResult + RawHit.
# ---------------------------------------------------------------------------
class TestRawHit:
    def test_minimal_hit_constructs(self):
        h = RawHit(
            raw_hit_id="rh-1",
            source_id="src-1",
            source_type=SourceClass.DOCS,
        )
        assert h.retrieval_lane is RetrievalLane.DENSE  # default

    def test_invalid_line_range_rejected(self):
        with pytest.raises(ValueError, match="invalid line_range"):
            RawHit(
                raw_hit_id="rh-1",
                source_id="src-1",
                source_type=SourceClass.DOCS,
                line_range=(10, 5),  # hi < lo
            )

    def test_negative_line_range_rejected(self):
        with pytest.raises(ValueError, match="invalid line_range"):
            RawHit(
                raw_hit_id="rh-1",
                source_id="src-1",
                source_type=SourceClass.DOCS,
                line_range=(-1, 5),
            )


class TestRetrievalLaneResult:
    def test_lane_result_manifest_hash_deterministic(self):
        hits = (
            RawHit(raw_hit_id="rh-1", source_id="s1", source_type=SourceClass.DOCS),
            RawHit(raw_hit_id="rh-2", source_id="s2", source_type=SourceClass.DOCS),
        )
        r1 = RetrievalLaneResult(
            lane_id="dense-1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q-1",
            adapter_id="dense-adapter",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
            raw_hits=hits,
        )
        r2 = RetrievalLaneResult(
            lane_id="dense-1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q-1",
            adapter_id="dense-adapter",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
            raw_hits=hits,
        )
        assert r1.compute_manifest_hash() == r2.compute_manifest_hash()

    def test_lane_result_hash_changes_with_adapter(self):
        r1 = RetrievalLaneResult(
            lane_id="d-1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q",
            adapter_id="a-1",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
        )
        r2 = RetrievalLaneResult(
            lane_id="d-1",
            lane_type=RetrievalLane.DENSE,
            query_ref="q",
            adapter_id="a-2",
            adapter_version="v1",
            source_class=SourceClass.DOCS,
        )
        assert r1.compute_manifest_hash() != r2.compute_manifest_hash()

    def test_negative_latency_rejected(self):
        with pytest.raises(ValueError, match="latency_ms"):
            RetrievalLaneResult(
                lane_id="x",
                lane_type=RetrievalLane.DENSE,
                query_ref="q",
                adapter_id="a",
                adapter_version="v",
                source_class=SourceClass.DOCS,
                latency_ms=-1,
            )


def test_pool_manifest_hash_deterministic():
    h1 = compute_pool_manifest_hash(
        plan_hash="p1",
        raw_hit_ids=("rh-2", "rh-1"),  # unordered
        lane_manifest_hashes=("l-2", "l-1"),
    )
    h2 = compute_pool_manifest_hash(
        plan_hash="p1",
        raw_hit_ids=("rh-1", "rh-2"),  # ordered
        lane_manifest_hashes=("l-1", "l-2"),
    )
    assert h1 == h2  # sort-invariance


# ---------------------------------------------------------------------------
# C0.4 — EvidenceFingerprint.
# ---------------------------------------------------------------------------
class TestEvidenceFingerprint:
    def test_fingerprint_key_independent_of_lane(self):
        f1 = EvidenceFingerprint(
            source_id="s1",
            source_version="v1",
            span_ref="span-A",
            content_hash="h1",
            retrieval_lane_set=(RetrievalLane.DENSE,),
        )
        f2 = EvidenceFingerprint(
            source_id="s1",
            source_version="v1",
            span_ref="span-A",
            content_hash="h1",
            retrieval_lane_set=(RetrievalLane.SPARSE,),  # different lane
        )
        assert f1.fingerprint_key == f2.fingerprint_key

    def test_fingerprint_key_changes_with_span(self):
        f1 = EvidenceFingerprint(
            source_id="s1",
            span_ref="span-A",
            content_hash="h1",
        )
        f2 = EvidenceFingerprint(
            source_id="s1",
            span_ref="span-B",
            content_hash="h1",
        )
        assert f1.fingerprint_key != f2.fingerprint_key

    def test_empty_source_id_rejected(self):
        with pytest.raises(ValueError, match="source_id required"):
            EvidenceFingerprint(source_id="")

    def test_graph_relation_refs_preserved(self):
        f = EvidenceFingerprint(
            source_id="s1",
            span_ref="span",
            graph_relation_refs=(GraphRelation.DEFINES, GraphRelation.REFERENCES),
        )
        assert GraphRelation.DEFINES in f.graph_relation_refs


# ---------------------------------------------------------------------------
# C0.4 — ExcludedEvidenceItem.
# ---------------------------------------------------------------------------
class TestExcludedEvidenceItem:
    def test_minimal_exclusion_constructs(self):
        e = ExcludedEvidenceItem(
            excluded_evidence_id="ex-1",
            original_evidence_ref="ev-1",
            exclusion_reason=ExclusionReason.STALE,
        )
        assert e.exclusion_reason is ExclusionReason.STALE

    def test_empty_excluded_id_rejected(self):
        with pytest.raises(ValueError, match="excluded_evidence_id required"):
            ExcludedEvidenceItem(
                excluded_evidence_id="",
                original_evidence_ref="ev-1",
                exclusion_reason=ExclusionReason.STALE,
            )

    def test_empty_original_ref_rejected(self):
        with pytest.raises(ValueError, match="original_evidence_ref required"):
            ExcludedEvidenceItem(
                excluded_evidence_id="ex-1",
                original_evidence_ref="",
                exclusion_reason=ExclusionReason.STALE,
            )


# ---------------------------------------------------------------------------
# C0.5 — CitationSupportMap.
# ---------------------------------------------------------------------------
class TestCitationSupportMap:
    def test_minimal_map_constructs(self):
        m = CitationSupportMap(
            claim_target_id="claim-1",
            support_target_type=SupportTarget.SOURCE_SUMMARY,
            required_support_level="direct",
        )
        assert m.claim_target_id == "claim-1"

    def test_score_out_of_range_rejected(self):
        with pytest.raises(ValueError, match="citation_precision_score"):
            CitationSupportMap(
                claim_target_id="claim-1",
                support_target_type=SupportTarget.SOURCE_SUMMARY,
                required_support_level="direct",
                citation_precision_score=1.5,
            )

    def test_quote_eligibility_requires_direct_span(self):
        with pytest.raises(ValueError, match="EXACT_QUOTE.*direct_span_refs"):
            CitationSupportMap(
                claim_target_id="claim-q",
                support_target_type=SupportTarget.EXACT_QUOTE,
                required_support_level="direct",
                quote_eligibility=True,
                direct_span_refs=(),  # empty
            )

    def test_quote_eligibility_with_span_refs_ok(self):
        m = CitationSupportMap(
            claim_target_id="claim-q",
            support_target_type=SupportTarget.EXACT_QUOTE,
            required_support_level="direct",
            quote_eligibility=True,
            direct_span_refs=("span-1",),
        )
        assert m.quote_eligibility


# ---------------------------------------------------------------------------
# C0.5 — SupportScoreBreakdownV2.
# ---------------------------------------------------------------------------
class TestSupportScoreBreakdownV2:
    def test_minimal_breakdown_constructs(self):
        b = SupportScoreBreakdownV2(support_score=0.7)
        assert b.confidence_band == "medium"

    def test_score_out_of_range_rejected(self):
        with pytest.raises(ValueError, match="support_score"):
            SupportScoreBreakdownV2(support_score=2.0)

    def test_negative_contradiction_penalty_rejected(self):
        with pytest.raises(ValueError, match="contradiction_penalty"):
            SupportScoreBreakdownV2(
                support_score=0.5, contradiction_penalty=-0.1
            )

    def test_invalid_confidence_band_rejected(self):
        with pytest.raises(ValueError, match="confidence_band"):
            SupportScoreBreakdownV2(
                support_score=0.5, confidence_band="extreme"
            )


# ---------------------------------------------------------------------------
# C0.5 — EvidenceGapReportV2.
# ---------------------------------------------------------------------------
class TestEvidenceGapReportV2:
    def test_empty_report_is_empty(self):
        r = EvidenceGapReportV2()
        assert r.is_empty

    def test_report_with_one_field_not_empty(self):
        r = EvidenceGapReportV2(stale_sources=("doc-1",))
        assert not r.is_empty

    def test_recommended_targets_preserved(self):
        r = EvidenceGapReportV2(
            recommended_refinement_targets=("query_rewrite", "broaden_top_k"),
        )
        assert "query_rewrite" in r.recommended_refinement_targets
