"""Tests for C0 evidence-packet hardening (plan c0-evidence-packet-hardening-7d4f1a).

Covers all 12 hardening primitives across 5 waves:

W1 — Citation-grade anchors + verbatim quote echo + retrieval-recipe HMAC
W2 — Spotlighting transform + injection-risk scoring
W3 — chunk_context (Anthropic Contextual Retrieval) + per-stage scores
W4 — Per-claim support map + structured disposition
W5 — Lineage detail + tiered budget envelope + just-in-time expansion handles

Sources: Anthropic Citations API, Anthropic Contextual Retrieval, Anthropic
Context Engineering, OpenAI File Search, Microsoft Spotlighting (arXiv 2403.14720).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    BudgetEnvelope,
    C0ContractViolation,
    C0EvidenceContract,
    CitationAnchor,
    CitedSpan,
    ExpansionHandle,
    PerClaimSupport,
    RecommendedDisposition,
    RetrievalRecipe,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _legacy_span(span_id: str = "sp-1") -> CitedSpan:
    """A span that uses ONLY the original 5 fields. Must remain valid for back-compat."""
    return CitedSpan(
        span_id=span_id,
        source_ref="doc://test.md",
        text_snippet="The river bank was muddy.",
        relevance_score=0.9,
        chunk_hash="abc123",
    )


def _quote_sha(quote: str) -> str:
    return CitedSpan.compute_quote_sha256(quote)


# ---------------------------------------------------------------------------
# W1.P1 — CitationAnchor
# ---------------------------------------------------------------------------


class TestCitationAnchor:
    def test_char_anchor_valid(self):
        a = CitationAnchor(kind="char", source_id="doc://a.md", start=0, end=42)
        assert a.kind == "char"
        assert a.end >= a.start

    def test_page_anchor_valid(self):
        a = CitationAnchor(kind="page", source_id="doc://a.pdf", start=1, end=3)
        assert a.kind == "page"

    def test_block_anchor_valid(self):
        a = CitationAnchor(kind="block", source_id="custom://blob", start=0, end=2)
        assert a.kind == "block"

    def test_invalid_kind_raises(self):
        with pytest.raises(C0ContractViolation):
            CitationAnchor(kind="line", source_id="x", start=0, end=1)  # type: ignore[arg-type]

    def test_empty_source_id_raises(self):
        with pytest.raises(C0ContractViolation):
            CitationAnchor(kind="char", source_id="   ", start=0, end=1)

    def test_negative_start_raises(self):
        with pytest.raises(C0ContractViolation):
            CitationAnchor(kind="char", source_id="x", start=-1, end=1)

    def test_end_before_start_raises(self):
        with pytest.raises(C0ContractViolation):
            CitationAnchor(kind="char", source_id="x", start=10, end=5)

    def test_compute_digest_deterministic(self):
        d1 = CitationAnchor.compute_digest("x", "char", 0, 10)
        d2 = CitationAnchor.compute_digest("x", "char", 0, 10)
        assert d1 == d2

    def test_compute_digest_differs_on_input(self):
        d1 = CitationAnchor.compute_digest("x", "char", 0, 10)
        d2 = CitationAnchor.compute_digest("x", "char", 0, 11)
        assert d1 != d2

    def test_anchor_is_frozen(self):
        a = CitationAnchor(kind="char", source_id="x", start=0, end=1)
        with pytest.raises(FrozenInstanceError):
            a.start = 5  # type: ignore[misc]


# ---------------------------------------------------------------------------
# W1.P2 — CitedSpan verbatim quote
# ---------------------------------------------------------------------------


class TestCitedQuote:
    def test_legacy_span_still_works(self):
        # Critical back-compat: existing call sites that pass only the original
        # 5 fields must continue to construct and validate cleanly.
        span = _legacy_span()
        assert span.cited_quote == ""
        assert span.cited_quote_sha256 == ""
        assert span.anchors == ()

    def test_quote_with_correct_hash_passes(self):
        q = "exact quote bytes"
        CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            cited_quote=q,
            cited_quote_sha256=_quote_sha(q),
        )

    def test_quote_without_hash_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                cited_quote="some text",
                cited_quote_sha256="",
            )

    def test_quote_with_wrong_hash_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                cited_quote="abc",
                cited_quote_sha256="0" * 64,
            )

    def test_anchors_must_be_citation_anchor(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                anchors=("not-an-anchor",),  # type: ignore[arg-type]
            )

    def test_anchors_attached(self):
        a = CitationAnchor(kind="char", source_id="x", start=0, end=10)
        span = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            anchors=(a,),
        )
        assert len(span.anchors) == 1


# ---------------------------------------------------------------------------
# W1.P3 — RetrievalRecipe + recipe_hmac
# ---------------------------------------------------------------------------


class TestRetrievalRecipe:
    def test_minimal_recipe_valid(self):
        r = RetrievalRecipe(plan_hash="abc")
        assert r.plan_hash == "abc"

    def test_empty_plan_hash_raises(self):
        with pytest.raises(C0ContractViolation):
            RetrievalRecipe(plan_hash="  ")

    def test_threshold_out_of_range_raises(self):
        with pytest.raises(C0ContractViolation):
            RetrievalRecipe(plan_hash="x", rerank_score_threshold=1.5)

    def test_negative_max_k_raises(self):
        with pytest.raises(C0ContractViolation):
            RetrievalRecipe(plan_hash="x", max_k=-1)

    def test_hmac_deterministic(self):
        r1 = RetrievalRecipe(plan_hash="abc", embed_model="bge-m3")
        r2 = RetrievalRecipe(plan_hash="abc", embed_model="bge-m3")
        assert r1.compute_hmac() == r2.compute_hmac()

    def test_hmac_changes_on_different_input(self):
        r1 = RetrievalRecipe(plan_hash="abc", embed_model="bge-m3")
        r2 = RetrievalRecipe(plan_hash="abc", embed_model="other-model")
        assert r1.compute_hmac() != r2.compute_hmac()

    def test_contract_with_recipe_validates(self):
        recipe = RetrievalRecipe(plan_hash="ph", embed_model="bge-m3", max_k=20)
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span(),),
            retrieval_recipe=recipe,
        )
        assert c.retrieval_recipe is recipe
        assert c.recipe_hmac == recipe.compute_hmac()

    def test_recipe_hmac_without_recipe_raises(self):
        # If recipe_hmac is set but recipe is None, validate() must reject.
        with pytest.raises(C0ContractViolation):
            C0EvidenceContract(
                retrieval_id="r",
                request_id="req",
                coverage_score=0.9,
                abstain_hint=False,
                cited_spans=(_legacy_span(),),
                evidence_hmac="x",
                recipe_hmac="forged-hmac",
            ).validate()

    def test_tampered_recipe_hmac_raises(self):
        recipe = RetrievalRecipe(plan_hash="ph")
        with pytest.raises(C0ContractViolation):
            C0EvidenceContract(
                retrieval_id="r",
                request_id="req",
                coverage_score=0.9,
                abstain_hint=False,
                cited_spans=(_legacy_span(),),
                evidence_hmac="x",
                retrieval_recipe=recipe,
                recipe_hmac="0" * 64,
            ).validate()


# ---------------------------------------------------------------------------
# W2.P1 — Spotlighting
# ---------------------------------------------------------------------------


class TestSpotlight:
    def test_default_mode_none_is_legacy(self):
        s = _legacy_span()
        assert s.spotlight_mode == "none"
        assert s.spotlight_token == ""

    def test_datamarked_requires_token(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                spotlight_mode="datamarked",
                spotlight_token="",
            )

    def test_datamarked_with_token_valid(self):
        s = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            spotlight_mode="datamarked",
            spotlight_token="^",
        )
        assert s.spotlight_mode == "datamarked"

    def test_invalid_spotlight_mode_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                spotlight_mode="hex",  # type: ignore[arg-type]
            )

    def test_contract_has_spotlight_aggregator(self):
        clean = _legacy_span()
        marked = CitedSpan(
            span_id="s2",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            spotlight_mode="datamarked",
            spotlight_token="^",
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(clean, marked),
        )
        assert c.has_spotlight() is True


# ---------------------------------------------------------------------------
# W2.P2 — Injection risk
# ---------------------------------------------------------------------------


class TestInjectionRisk:
    def test_default_score_zero(self):
        assert _legacy_span().injection_risk_score == 0.0

    def test_score_out_of_range_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                injection_risk_score=1.5,
            )

    def test_signals_carried(self):
        s = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            injection_risk_score=0.85,
            injection_risk_signals=("imperative_verb", "system_prompt_lookalike"),
        )
        assert "imperative_verb" in s.injection_risk_signals

    def test_max_injection_risk_aggregator(self):
        s1 = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="x",
            relevance_score=0.5,
            chunk_hash="h",
            injection_risk_score=0.2,
        )
        s2 = CitedSpan(
            span_id="s2",
            source_ref="x",
            text_snippet="x",
            relevance_score=0.5,
            chunk_hash="h",
            injection_risk_score=0.95,
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(s1, s2),
        )
        assert c.max_injection_risk() == pytest.approx(0.95)


# ---------------------------------------------------------------------------
# W3.P1 — chunk_context (Anthropic Contextual Retrieval)
# ---------------------------------------------------------------------------


class TestChunkContext:
    def test_default_empty(self):
        assert _legacy_span().chunk_context == ""

    def test_normal_blurb_accepted(self):
        ctx = "Section 4.2 of the report; describes Q4 revenue versus prior year."
        s = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            chunk_context=ctx,
        )
        assert s.chunk_context == ctx

    def test_oversized_blurb_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                chunk_context="A" * 401,
            )


# ---------------------------------------------------------------------------
# W3.P2 — Per-stage scores
# ---------------------------------------------------------------------------


class TestPerStageScores:
    def test_default_scores_zero(self):
        s = _legacy_span()
        assert s.retrieval_score == 0.0
        assert s.rerank_score == 0.0
        assert s.support_score == 0.0

    def test_effective_support_falls_back_to_relevance(self):
        s = _legacy_span()
        assert s.effective_support_score == s.relevance_score

    def test_effective_support_uses_split_when_present(self):
        s = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="snippet",
            relevance_score=0.5,
            chunk_hash="h",
            support_score=0.85,
        )
        assert s.effective_support_score == pytest.approx(0.85)

    def test_score_out_of_range_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="snippet",
                relevance_score=0.9,
                chunk_hash="h",
                rerank_score=2.0,
            )


# ---------------------------------------------------------------------------
# W4.P1 — PerClaimSupport
# ---------------------------------------------------------------------------


class TestPerClaimSupport:
    def test_minimal_pass_requires_citing_spans(self):
        with pytest.raises(C0ContractViolation):
            PerClaimSupport(claim_id="c1", status="PASS", support_score=0.9)

    def test_pass_with_spans_valid(self):
        s = PerClaimSupport(
            claim_id="c1",
            status="PASS",
            support_score=0.9,
            citing_span_ids=("sp-1",),
        )
        assert s.status == "PASS"

    def test_blocked_without_spans_valid(self):
        s = PerClaimSupport(
            claim_id="c1",
            status="BLOCKED",
            support_score=0.0,
            blocking_reason="ACL_BLOCKED",
        )
        assert s.blocking_reason == "ACL_BLOCKED"

    def test_invalid_status_raises(self):
        with pytest.raises(C0ContractViolation):
            PerClaimSupport(
                claim_id="c1",
                status="MAYBE",  # type: ignore[arg-type]
                support_score=0.5,
            )

    def test_contract_validates_citing_span_ids(self):
        # If a per-claim support cites a span_id that isn't in cited_spans, fail.
        unknown = PerClaimSupport(
            claim_id="c1",
            status="PASS",
            support_score=0.9,
            citing_span_ids=("does-not-exist",),
        )
        with pytest.raises(C0ContractViolation):
            C0EvidenceContract.build(
                retrieval_id="r",
                request_id="req",
                coverage_score=0.9,
                cited_spans=(_legacy_span("sp-1"),),
                per_claim_support=(unknown,),
            )

    def test_contract_with_valid_per_claim_support(self):
        sup = PerClaimSupport(
            claim_id="c1",
            status="PASS",
            support_score=0.9,
            citing_span_ids=("sp-1",),
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span("sp-1"),),
            per_claim_support=(sup,),
        )
        assert len(c.per_claim_support) == 1


# ---------------------------------------------------------------------------
# W4.P2 — RecommendedDisposition
# ---------------------------------------------------------------------------


class TestRecommendedDisposition:
    def test_proceed_with_default_reason(self):
        d = RecommendedDisposition(verdict="proceed")
        assert d.primary_reason == "OK"
        assert d.confidence == 1.0

    def test_reroute_requires_route_id(self):
        with pytest.raises(C0ContractViolation):
            RecommendedDisposition(verdict="reroute", suggested_route_id="")

    def test_reroute_with_route_id_valid(self):
        d = RecommendedDisposition(
            verdict="reroute",
            suggested_route_id="R5_FALLBACK",
            primary_reason="LOW_COVERAGE",
        )
        assert d.suggested_route_id == "R5_FALLBACK"

    def test_invalid_verdict_raises(self):
        with pytest.raises(C0ContractViolation):
            RecommendedDisposition(verdict="punt")  # type: ignore[arg-type]

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(C0ContractViolation):
            RecommendedDisposition(verdict="proceed", confidence=1.1)

    def test_contract_carries_disposition(self):
        d = RecommendedDisposition(
            verdict="caveat",
            primary_reason="STALE_AUTHORITY",
            secondary_reasons=("LOW_COVERAGE",),
            blocking_gaps=("section-4.2-missing",),
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span(),),
            recommended_disposition=d,
        )
        assert c.recommended_disposition is d


# ---------------------------------------------------------------------------
# W5.P1 — Lineage detail
# ---------------------------------------------------------------------------


class TestLineageDetail:
    def test_default_lane_dense(self):
        assert _legacy_span().retrieval_lane == "dense"

    def test_invalid_lane_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="x",
                relevance_score=0.9,
                chunk_hash="h",
                retrieval_lane="quantum",  # type: ignore[arg-type]
            )

    def test_negative_lane_rank_raises(self):
        with pytest.raises(C0ContractViolation):
            CitedSpan(
                span_id="s1",
                source_ref="x",
                text_snippet="x",
                relevance_score=0.9,
                chunk_hash="h",
                lane_rank=-1,
            )

    def test_lanes_used_aggregator(self):
        s1 = CitedSpan(
            span_id="s1",
            source_ref="x",
            text_snippet="x",
            relevance_score=0.9,
            chunk_hash="h",
            retrieval_lane="dense",
            lanes_that_recovered_this=("dense", "sparse"),
        )
        s2 = CitedSpan(
            span_id="s2",
            source_ref="x",
            text_snippet="x",
            relevance_score=0.9,
            chunk_hash="h",
            retrieval_lane="graph_hop",
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(s1, s2),
        )
        lanes = c.lanes_used()
        # Order = insertion order: dense, sparse (from s1), graph_hop (from s2)
        assert "dense" in lanes
        assert "sparse" in lanes
        assert "graph_hop" in lanes


# ---------------------------------------------------------------------------
# W5.P2 — BudgetEnvelope
# ---------------------------------------------------------------------------


class TestBudgetEnvelope:
    def test_default_envelope_valid(self):
        b = BudgetEnvelope()
        assert b.overflow_policy == "drop_background_first"

    def test_negative_field_raises(self):
        with pytest.raises(C0ContractViolation):
            BudgetEnvelope(must_use_tokens=-1)

    def test_strata_exceed_cap_raises(self):
        with pytest.raises(C0ContractViolation):
            BudgetEnvelope(
                must_use_tokens=500,
                supporting_tokens=500,
                contradicts_tokens=500,
                background_tokens=500,
                total_cap=1000,  # 2000 > 1000
            )

    def test_strata_within_cap_valid(self):
        b = BudgetEnvelope(
            must_use_tokens=400,
            supporting_tokens=300,
            background_tokens=200,
            total_cap=1000,
            overflow_policy="summarize",
        )
        assert b.overflow_policy == "summarize"

    def test_invalid_overflow_policy_raises(self):
        with pytest.raises(C0ContractViolation):
            BudgetEnvelope(overflow_policy="explode")  # type: ignore[arg-type]

    def test_contract_carries_envelope(self):
        b = BudgetEnvelope(must_use_tokens=100, total_cap=200)
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span(),),
            budget_envelope=b,
        )
        assert c.budget_envelope is b


# ---------------------------------------------------------------------------
# W5.P3 — ExpansionHandle
# ---------------------------------------------------------------------------


class TestExpansionHandle:
    def test_build_helper_produces_valid_handle(self):
        h = ExpansionHandle.build(
            handle_id="h1",
            allowed_op="fetch_neighbor",
            acl_scope="tenant:abc",
            budget_remaining_tokens=500,
        )
        assert h.handle_hmac

    def test_unsigned_handle_raises(self):
        with pytest.raises(C0ContractViolation):
            ExpansionHandle(
                handle_id="h1",
                allowed_op="fetch_neighbor",
                acl_scope="tenant:abc",
                budget_remaining_tokens=0,
                handle_hmac="",
            )

    def test_forged_hmac_raises(self):
        with pytest.raises(C0ContractViolation):
            ExpansionHandle(
                handle_id="h1",
                allowed_op="fetch_neighbor",
                acl_scope="tenant:abc",
                budget_remaining_tokens=0,
                handle_hmac="0" * 64,
            )

    def test_hmac_differs_per_handle(self):
        h1 = ExpansionHandle.build(
            handle_id="h1",
            allowed_op="fetch_neighbor",
            acl_scope="tenant:abc",
        )
        h2 = ExpansionHandle.build(
            handle_id="h2",
            allowed_op="fetch_neighbor",
            acl_scope="tenant:abc",
        )
        assert h1.handle_hmac != h2.handle_hmac

    def test_invalid_op_raises(self):
        with pytest.raises(C0ContractViolation):
            ExpansionHandle.build(
                handle_id="h1",
                allowed_op="rm -rf",  # type: ignore[arg-type]
                acl_scope="tenant:abc",
            )

    def test_empty_acl_scope_raises(self):
        with pytest.raises(C0ContractViolation):
            ExpansionHandle.build(
                handle_id="h1",
                allowed_op="fetch_neighbor",
                acl_scope="  ",
            )

    def test_contract_carries_handles(self):
        h = ExpansionHandle.build(
            handle_id="h1",
            allowed_op="fetch_neighbor",
            acl_scope="tenant:abc",
            budget_remaining_tokens=500,
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span(),),
            expansion_handles=(h,),
        )
        assert len(c.expansion_handles) == 1


# ---------------------------------------------------------------------------
# Cross-cutting — back-compat for legacy callers
# ---------------------------------------------------------------------------


class TestBackCompat:
    def test_legacy_build_signature_still_works(self):
        # All hardening fields are optional; existing call sites must keep working.
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span(),),
        )
        assert c.retrieval_recipe is None
        assert c.recipe_hmac == ""
        assert c.per_claim_support == ()
        assert c.recommended_disposition is None
        assert c.budget_envelope is None
        assert c.expansion_handles == ()

    def test_to_dict_includes_all_new_keys(self):
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.9,
            cited_spans=(_legacy_span(),),
        )
        d = c.to_dict()
        for key in (
            "retrieval_recipe",
            "recipe_hmac",
            "per_claim_support",
            "recommended_disposition",
            "budget_envelope",
            "expansion_handles",
            "retrieval_timestamp",
        ):
            assert key in d, f"to_dict() missing hardening key {key!r}"

    def test_kitchen_sink_construct(self):
        # All 12 hardening primitives populated together — the SVP packet.
        anchor = CitationAnchor(kind="char", source_id="doc://a.md", start=0, end=42)
        quote = "exact source bytes"
        span = CitedSpan(
            span_id="sp-1",
            source_ref="doc://a.md",
            text_snippet="snippet",
            relevance_score=0.9,
            chunk_hash="h",
            cited_quote=quote,
            cited_quote_sha256=_quote_sha(quote),
            anchors=(anchor,),
            spotlight_mode="datamarked",
            spotlight_token="^",
            injection_risk_score=0.05,
            injection_risk_signals=(),
            chunk_context="Section 4.2; Q4 revenue.",
            retrieval_score=0.88,
            rerank_score=0.91,
            support_score=0.93,
            retrieval_lane="dense",
            lane_rank=1,
            lanes_that_recovered_this=("dense", "sparse"),
        )
        recipe = RetrievalRecipe(
            plan_hash="plan-abc",
            embed_model="bge-m3",
            sparse_index_version="v3",
            rerank_model_id="cohere-rerank-v3",
            rerank_score_threshold=0.5,
            max_k=20,
            max_hops=2,
            filter_set_hash="filter-xyz",
            snapshot_ids=("snap-1",),
            query_vec_id="qv-1",
        )
        per_claim = PerClaimSupport(
            claim_id="c1",
            status="PASS",
            support_score=0.93,
            citing_span_ids=("sp-1",),
            citing_anchor_digests=(
                CitationAnchor.compute_digest("doc://a.md", "char", 0, 42),
            ),
        )
        disposition = RecommendedDisposition(
            verdict="proceed",
            primary_reason="OK",
            confidence=0.95,
        )
        envelope = BudgetEnvelope(
            must_use_tokens=400,
            supporting_tokens=200,
            background_tokens=100,
            total_cap=1000,
            overflow_policy="drop_background_first",
        )
        handle = ExpansionHandle.build(
            handle_id="h1",
            allowed_op="fetch_parent_doc",
            acl_scope="tenant:abc",
            budget_remaining_tokens=500,
        )
        c = C0EvidenceContract.build(
            retrieval_id="r",
            request_id="req",
            coverage_score=0.93,
            cited_spans=(span,),
            retrieval_recipe=recipe,
            per_claim_support=(per_claim,),
            recommended_disposition=disposition,
            budget_envelope=envelope,
            expansion_handles=(handle,),
            retrieval_timestamp="2026-04-25T19:00:00Z",
        )
        c.validate()
        assert c.max_injection_risk() == pytest.approx(0.05)
        assert c.has_spotlight() is True
        assert "dense" in c.lanes_used()
        assert c.recipe_hmac == recipe.compute_hmac()
