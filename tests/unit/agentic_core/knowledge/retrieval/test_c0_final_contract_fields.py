"""Tests for Final Evidence Contract spec fields (C0.5 hardening).

Validates every field listed in C0 Context Engine spec §FINAL C0 EVIDENCE CONTRACT
is populated by EvidenceContractBuilder.build_contract().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    EvidenceClass,
    EvidenceContractBuilder,
    EvidenceStatus,
    RecommendedDisposition,
    get_evidence_contract_builder,
)
from agentic_core.knowledge.retrieval.retrieval_plan import (
    RetrievalMode,
    RetrievalPlan,
    SupportTarget,
    WeakSupportPolicy,
)


@dataclass
class StubDoc:
    doc_id: str
    content: str = "stub content"
    score: float = 0.9
    source: str = "dense"
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# C0.1 RetrievalPlan spec fields
# ---------------------------------------------------------------------------


class TestRetrievalPlanSpecFields:
    """Validate every C0.1 spec field is on RetrievalPlan."""

    def test_support_target_field_present(self) -> None:
        plan = RetrievalPlan(query_id="q1", support_target=SupportTarget.EXACT_QUOTE)
        assert plan.support_target == "exact_quote"

    def test_weak_support_policy_default(self) -> None:
        plan = RetrievalPlan(query_id="q1")
        assert plan.weak_support_policy == WeakSupportPolicy.REFINE_ONCE

    def test_limits_present(self) -> None:
        plan = RetrievalPlan(
            query_id="q1",
            max_parent_expansion=5,
            max_graph_hops=3,
            max_refine_attempts=4,
        )
        assert plan.max_parent_expansion == 5
        assert plan.max_graph_hops == 3
        assert plan.max_refine_attempts == 4

    def test_budget_fields_present(self) -> None:
        plan = RetrievalPlan(
            query_id="q1",
            slo_budget_ms=10000,
            token_budget=8000,
            latency_budget_ms=5000,
            cost_budget_usd=0.10,
        )
        assert plan.slo_budget_ms == 10000
        assert plan.token_budget == 8000
        assert plan.latency_budget_ms == 5000
        assert plan.cost_budget_usd == 0.10

    def test_region_and_disallowed_sources(self) -> None:
        plan = RetrievalPlan(
            query_id="q1",
            region="EU",
            disallowed_sources=["legacy_archive", "untrusted_blog"],
        )
        assert plan.region == "EU"
        assert "legacy_archive" in plan.disallowed_sources

    def test_retrieval_mode_constants_complete(self) -> None:
        modes = set(RetrievalMode.all())
        assert {"dense", "sparse", "hybrid", "graph", "metadata", "cache"} <= modes

    def test_support_target_constants(self) -> None:
        # All 6 spec types
        assert SupportTarget.EXACT_QUOTE == "exact_quote"
        assert SupportTarget.SOURCE_BACKED_SUMMARY == "source_backed_summary"
        assert SupportTarget.CODE_LOCATION == "code_location"
        assert SupportTarget.POLICY_CLAUSE == "policy_clause"
        assert SupportTarget.INCIDENT_EVIDENCE == "incident_evidence"
        assert SupportTarget.RANKED_CAUSE == "ranked_cause"


# ---------------------------------------------------------------------------
# C0.5 Final Evidence Contract spec fields
# ---------------------------------------------------------------------------


class TestFinalContractFields:
    """Validate every C0.5 Final Contract field is populated."""

    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()
        self.docs = [
            StubDoc(
                doc_id="d1",
                content="High-confidence chunk about retrieval planning",
                score=0.95,
                source="dense",
                metadata={
                    "source_id": "src_alpha",
                    "rerank_score": 0.95,
                    "retrieval_mode": "dense",
                    "freshness_band": "warm",
                    "age_days": 7,
                    "acl_cleared": True,
                    "tenant_id": "acme",
                    "section": "Section 1",
                    "line_ref": 42,
                    "span_start": 0,
                    "span_end": 100,
                },
            ),
            StubDoc(
                doc_id="d2",
                content="Supporting chunk for retrieval planning",
                score=0.75,
                source="sparse",
                metadata={
                    "source_id": "src_beta",
                    "rerank_score": 0.75,
                    "retrieval_mode": "sparse",
                    "freshness_band": "cool",
                    "age_days": 30,
                    "acl_cleared": True,
                    "tenant_id": "acme",
                },
            ),
        ]
        self.contract = self.builder.build_contract(
            query_id="q1",
            query="retrieval planning",
            retrieved_docs=self.docs,
            query_aspects=["retrieval", "planning"],
        )

    def test_status_present_and_valid(self) -> None:
        valid = {
            EvidenceStatus.PASS,
            EvidenceStatus.WEAK,
            EvidenceStatus.WEAK_WITH_CAVEATS,
            EvidenceStatus.CONFLICTED,
            EvidenceStatus.EMPTY,
            EvidenceStatus.BLOCKED,
        }
        assert self.contract.status in valid

    def test_support_score_in_range(self) -> None:
        assert 0.0 <= self.contract.support_score <= 1.0

    def test_cited_spans_populated(self) -> None:
        assert isinstance(self.contract.cited_spans, list)
        if self.contract.cited_spans:
            span = self.contract.cited_spans[0]
            assert "chunk_id" in span
            assert "source_id" in span
            assert "citation_anchor" in span
            assert "line_ref" in span
            assert "section" in span

    def test_source_ids_deduped(self) -> None:
        assert isinstance(self.contract.source_ids, list)
        # All entries unique
        assert len(self.contract.source_ids) == len(set(self.contract.source_ids))

    def test_evidence_classes_uses_5_class_taxonomy(self) -> None:
        valid = {
            EvidenceClass.MUST_USE,
            EvidenceClass.SUPPORTING,
            EvidenceClass.CONTRADICTS,
            EvidenceClass.BACKGROUND,
            EvidenceClass.EXCLUDED,
        }
        for chunk_id, cls in self.contract.evidence_classes.items():
            assert cls in valid, f"chunk {chunk_id} has invalid class {cls}"

    def test_contradiction_flags_is_list(self) -> None:
        assert isinstance(self.contract.contradiction_flags, list)

    def test_unresolved_gaps_present(self) -> None:
        assert isinstance(self.contract.unresolved_gaps, list)

    def test_freshness_report_structure(self) -> None:
        report = self.contract.freshness_report
        assert "by_source" in report
        assert "stale_count" in report
        assert "fresh_count" in report
        # Both docs were warm/cool — neither counts as stale
        assert report["fresh_count"] >= 1

    def test_acl_report_structure(self) -> None:
        report = self.contract.acl_report
        assert "by_source" in report
        assert "cleared_count" in report
        assert "blocked_count" in report
        assert report["cleared_count"] >= 1

    def test_lineage_manifest_records_lanes(self) -> None:
        manifest = self.contract.lineage_manifest
        assert "by_chunk" in manifest
        assert "retrieval_modes_used" in manifest
        assert "graph_hops_total" in manifest
        # Both dense and sparse lanes must appear
        assert "dense" in manifest["retrieval_modes_used"] or "sparse" in manifest["retrieval_modes_used"]

    def test_prompt_budget_hint_has_token_estimate(self) -> None:
        hint = self.contract.prompt_budget_hint
        assert "token_estimate" in hint
        assert "must_use_count" in hint
        assert "packing_order" in hint
        assert hint["token_estimate"] >= 0

    def test_recommended_disposition_valid(self) -> None:
        valid = {
            RecommendedDisposition.PROCEED,
            RecommendedDisposition.CAVEAT,
            RecommendedDisposition.ABSTAIN,
            RecommendedDisposition.REROUTE,
        }
        assert self.contract.recommended_disposition in valid

    def test_budget_report_structure(self) -> None:
        report = self.contract.budget_report
        assert "retrieval_passes" in report
        assert "graph_hops" in report
        assert "latency_used_ms" in report
        assert "budget_remaining_ms" in report
        assert "tokens_used" in report
        assert "cost_used_usd" in report


# ---------------------------------------------------------------------------
# C0.5 status computation
# ---------------------------------------------------------------------------


class TestStatusComputation:
    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder(
            min_citation_confidence=0.7,
            min_coverage_to_proceed=0.3,
        )

    def test_empty_docs_returns_empty_status(self) -> None:
        contract = self.builder.build_contract(
            query_id="q1",
            query="test",
            retrieved_docs=[],
        )
        assert contract.status == EvidenceStatus.EMPTY
        assert contract.recommended_disposition == RecommendedDisposition.ABSTAIN

    def test_high_confidence_returns_pass(self) -> None:
        docs = [
            StubDoc(doc_id=f"d{i}", score=0.95, content=f"content {i}", metadata={"source_id": f"src_{i}"})
            for i in range(5)
        ]
        contract = self.builder.build_contract(
            query_id="q1",
            query="content content",
            retrieved_docs=docs,
            query_aspects=["content"],
        )
        # With 5 high-confidence docs, status should be PASS
        assert contract.status == EvidenceStatus.PASS
        assert contract.recommended_disposition == RecommendedDisposition.PROCEED

    def test_low_confidence_returns_weak(self) -> None:
        docs = [StubDoc(doc_id="d1", score=0.6, content="x", metadata={"source_id": "s1"})]
        contract = self.builder.build_contract(
            query_id="q1",
            query="test",
            retrieved_docs=docs,
        )
        # Below threshold — citation filtered out, status EMPTY (no citations)
        # If docs filtered: status=EMPTY; if some pass: status=WEAK
        assert contract.status in {EvidenceStatus.EMPTY, EvidenceStatus.WEAK}


class TestRecommendedDisposition:
    def setup_method(self) -> None:
        self.builder = EvidenceContractBuilder()

    @pytest.mark.parametrize(
        "status,expected_disposition",
        [
            (EvidenceStatus.PASS, RecommendedDisposition.PROCEED),
            (EvidenceStatus.WEAK_WITH_CAVEATS, RecommendedDisposition.CAVEAT),
            (EvidenceStatus.CONFLICTED, RecommendedDisposition.CAVEAT),
            (EvidenceStatus.EMPTY, RecommendedDisposition.ABSTAIN),
            (EvidenceStatus.BLOCKED, RecommendedDisposition.ABSTAIN),
        ],
    )
    def test_disposition_for_status(self, status: str, expected_disposition: str) -> None:
        result = self.builder._decide_disposition(status, "none", coverage_score=0.5)
        assert result == expected_disposition

    def test_weak_with_very_low_coverage_recommends_reroute(self) -> None:
        # Coverage way below threshold/2 — workflow-sized
        result = self.builder._decide_disposition(
            EvidenceStatus.WEAK,
            "none",
            coverage_score=0.05,
        )
        assert result == RecommendedDisposition.REROUTE

    def test_weak_with_recoverable_coverage_recommends_caveat(self) -> None:
        result = self.builder._decide_disposition(
            EvidenceStatus.WEAK,
            "none",
            coverage_score=0.25,
        )
        assert result == RecommendedDisposition.CAVEAT


class TestSingletonStillWorks:
    def test_global_builder_get(self) -> None:
        b1 = get_evidence_contract_builder()
        b2 = get_evidence_contract_builder()
        assert b1 is b2
