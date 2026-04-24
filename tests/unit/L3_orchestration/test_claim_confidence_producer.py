"""W5.P3 tests — C0 producer hook for ClaimGroundingConfidence."""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.reasoning.claim_confidence_producer import (
    confidence_from_span_relevance,
    enrich_contract_with_claim_confidences,
)
from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0ContractViolation,
    C0EvidenceContract,
    CitedSpan,
)


def _span(span_id: str, relevance: float = 0.9) -> CitedSpan:
    return CitedSpan(
        span_id=span_id,
        source_ref=f"doc://{span_id}",
        text_snippet="evidence text",
        relevance_score=relevance,
        chunk_hash="a" * 64,
    )


class TestConfidenceFromSpanRelevance:
    def test_max_aggregation_default(self) -> None:
        claim = confidence_from_span_relevance(
            "c-1",
            (_span("s1", 0.7), _span("s2", 0.95), _span("s3", 0.4)),
        )
        assert claim.confidence == pytest.approx(0.95)
        assert set(claim.supporting_span_ids) == {"s1", "s2", "s3"}

    def test_mean_aggregation(self) -> None:
        claim = confidence_from_span_relevance(
            "c-1",
            (_span("s1", 0.6), _span("s2", 0.8)),
            aggregation="mean",
        )
        assert claim.confidence == pytest.approx(0.7)

    def test_min_aggregation(self) -> None:
        claim = confidence_from_span_relevance(
            "c-1",
            (_span("s1", 0.9), _span("s2", 0.3)),
            aggregation="min",
        )
        assert claim.confidence == pytest.approx(0.3)

    def test_empty_spans_produces_zero_support(self) -> None:
        # Valid per W1b ClaimGroundingConfidence semantics: confidence=0
        # + no spans is the explicit "no support" marker.
        claim = confidence_from_span_relevance("c-1", ())
        assert claim.confidence == 0.0
        assert claim.supporting_span_ids == ()

    def test_out_of_range_relevance_clipped(self) -> None:
        # Some retrievers emit scores slightly over 1.0; clip into [0, 1].
        claim = confidence_from_span_relevance(
            "c-1", (_span("s1", 1.2),),
        )
        assert claim.confidence == pytest.approx(1.0)

    def test_unknown_aggregation_rejected(self) -> None:
        with pytest.raises(ValueError, match="aggregation"):
            confidence_from_span_relevance(
                "c-1", (_span("s1"),), aggregation="mode",
            )

    def test_snippet_passthrough(self) -> None:
        claim = confidence_from_span_relevance(
            "c-1", (_span("s1"),), claim_text_snippet="test claim",
        )
        assert claim.claim_text_snippet == "test claim"


class TestEnrichContract:
    def _base_contract(self) -> C0EvidenceContract:
        return C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.8,
            cited_spans=(_span("s1", 0.9), _span("s2", 0.7), _span("s3", 0.5)),
        )

    def test_enrich_adds_claim_confidences(self) -> None:
        base = self._base_contract()
        assert base.claim_confidences == ()

        enriched = enrich_contract_with_claim_confidences(
            base,
            {"c-1": ("s1", "s2"), "c-2": ("s3",)},
        )
        assert len(enriched.claim_confidences) == 2
        # Default aggregation is max.
        c1 = next(c for c in enriched.claim_confidences if c.claim_id == "c-1")
        assert c1.confidence == pytest.approx(0.9)

    def test_enrich_returns_new_instance_not_mutation(self) -> None:
        base = self._base_contract()
        enriched = enrich_contract_with_claim_confidences(
            base, {"c-1": ("s1",)},
        )
        assert enriched is not base
        assert base.claim_confidences == ()  # originale untouched

    def test_dangling_span_rejected(self) -> None:
        base = self._base_contract()
        with pytest.raises(C0ContractViolation, match="unknown span_id"):
            enrich_contract_with_claim_confidences(
                base, {"c-1": ("ghost",)},
            )

    def test_snippet_map_passthrough(self) -> None:
        base = self._base_contract()
        enriched = enrich_contract_with_claim_confidences(
            base,
            {"c-1": ("s1",)},
            claim_text_snippets={"c-1": "snippet for c-1"},
        )
        c1 = enriched.claim_confidences[0]
        assert c1.claim_text_snippet == "snippet for c-1"

    def test_aggregation_strategy_used(self) -> None:
        base = self._base_contract()
        enriched = enrich_contract_with_claim_confidences(
            base,
            {"c-1": ("s1", "s2", "s3")},
            aggregation="min",
        )
        c1 = enriched.claim_confidences[0]
        # Min of {0.9, 0.7, 0.5} = 0.5.
        assert c1.confidence == pytest.approx(0.5)

    def test_empty_claim_map_produces_empty_confidences(self) -> None:
        base = self._base_contract()
        enriched = enrich_contract_with_claim_confidences(base, {})
        assert enriched.claim_confidences == ()
