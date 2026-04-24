"""W1b.P1 tests — ClaimGroundingConfidence + C0EvidenceContract.claim_confidences.

Verifies the Vertex-style per-claim grounding confidence extension is
additive: existing producers that don't pass ``claim_confidences`` still
build valid contracts, and new producers are validated correctly.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0ContractViolation,
    C0EvidenceContract,
    CitedSpan,
    ClaimGroundingConfidence,
)


def _span(span_id: str = "span-1") -> CitedSpan:
    return CitedSpan(
        span_id=span_id,
        source_ref=f"doc://{span_id}",
        text_snippet="some text",
        relevance_score=0.9,
        chunk_hash="a" * 64,
    )


class TestBackCompatC0Contract:
    def test_contract_without_claim_confidences_still_builds(self) -> None:
        contract = C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.8,
            cited_spans=(_span(),),
        )
        assert contract.claim_confidences == ()
        contract.validate()  # idempotent

    def test_to_dict_includes_empty_claim_confidences(self) -> None:
        contract = C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.5,
            cited_spans=(_span(),),
        )
        data = contract.to_dict()
        assert data["claim_confidences"] == []


class TestClaimGroundingConfidenceValidation:
    def test_missing_claim_id_rejected(self) -> None:
        with pytest.raises(C0ContractViolation, match="claim_id is required"):
            ClaimGroundingConfidence(claim_id="", confidence=0.5, supporting_span_ids=("span-1",))

    def test_whitespace_claim_id_rejected(self) -> None:
        with pytest.raises(C0ContractViolation, match="claim_id is required"):
            ClaimGroundingConfidence(
                claim_id="   ", confidence=0.5, supporting_span_ids=("span-1",),
            )

    def test_out_of_range_confidence_rejected(self) -> None:
        with pytest.raises(C0ContractViolation, match="must be in"):
            ClaimGroundingConfidence(
                claim_id="c-1", confidence=1.2, supporting_span_ids=("span-1",),
            )

    def test_negative_confidence_rejected(self) -> None:
        with pytest.raises(C0ContractViolation, match="must be in"):
            ClaimGroundingConfidence(
                claim_id="c-1", confidence=-0.1, supporting_span_ids=("span-1",),
            )

    def test_nan_confidence_rejected(self) -> None:
        with pytest.raises(C0ContractViolation, match="must not be NaN"):
            ClaimGroundingConfidence(
                claim_id="c-1",
                confidence=float("nan"),
                supporting_span_ids=("span-1",),
            )

    def test_nonzero_confidence_without_spans_rejected(self) -> None:
        # Prevents "claim with 0.8 confidence but no supporting spans".
        with pytest.raises(C0ContractViolation, match="no supporting_span_ids"):
            ClaimGroundingConfidence(
                claim_id="c-1", confidence=0.8, supporting_span_ids=(),
            )

    def test_zero_confidence_without_spans_allowed(self) -> None:
        # "Explicit no-support" marker — legitimate.
        claim = ClaimGroundingConfidence(
            claim_id="c-1", confidence=0.0, supporting_span_ids=(),
        )
        assert claim.confidence == 0.0

    def test_valid_claim_builds(self) -> None:
        claim = ClaimGroundingConfidence(
            claim_id="c-1",
            confidence=0.85,
            supporting_span_ids=("span-1", "span-2"),
            claim_text_snippet="The capital of France is Paris.",
        )
        assert claim.confidence == pytest.approx(0.85)
        assert len(claim.supporting_span_ids) == 2


class TestContractWithClaimConfidences:
    def test_contract_with_claims_builds_and_validates(self) -> None:
        contract = C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.9,
            cited_spans=(_span("span-1"), _span("span-2")),
            claim_confidences=(
                ClaimGroundingConfidence(
                    claim_id="c-1", confidence=0.9, supporting_span_ids=("span-1",),
                ),
                ClaimGroundingConfidence(
                    claim_id="c-2", confidence=0.75, supporting_span_ids=("span-2",),
                ),
            ),
        )
        assert len(contract.claim_confidences) == 2
        assert contract.mean_claim_confidence() == pytest.approx(0.825)
        assert contract.min_claim_confidence() == pytest.approx(0.75)

    def test_dangling_span_reference_rejected(self) -> None:
        with pytest.raises(C0ContractViolation, match="unknown span_id"):
            C0EvidenceContract.build(
                retrieval_id="ret-1",
                request_id="req-1",
                coverage_score=0.9,
                cited_spans=(_span("span-1"),),
                claim_confidences=(
                    ClaimGroundingConfidence(
                        claim_id="c-1",
                        confidence=0.9,
                        supporting_span_ids=("span-ghost",),
                    ),
                ),
            )

    def test_mean_claim_confidence_empty_returns_zero(self) -> None:
        contract = C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.8,
            cited_spans=(_span(),),
        )
        assert contract.mean_claim_confidence() == 0.0
        assert contract.min_claim_confidence() == 0.0

    def test_min_claim_confidence_identifies_weak_link(self) -> None:
        # Vertex "conservative reading" — one weak claim should dominate.
        contract = C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.9,
            cited_spans=(_span("span-1"), _span("span-2"), _span("span-3")),
            claim_confidences=(
                ClaimGroundingConfidence(
                    claim_id="c-1", confidence=0.95, supporting_span_ids=("span-1",),
                ),
                ClaimGroundingConfidence(
                    claim_id="c-2", confidence=0.20, supporting_span_ids=("span-2",),
                ),
                ClaimGroundingConfidence(
                    claim_id="c-3", confidence=0.88, supporting_span_ids=("span-3",),
                ),
            ),
        )
        assert contract.min_claim_confidence() == pytest.approx(0.20)
        # Mean alone would mask the weak claim.
        assert contract.mean_claim_confidence() > 0.60

    def test_to_dict_serializes_claim_confidences(self) -> None:
        contract = C0EvidenceContract.build(
            retrieval_id="ret-1",
            request_id="req-1",
            coverage_score=0.9,
            cited_spans=(_span("span-1"),),
            claim_confidences=(
                ClaimGroundingConfidence(
                    claim_id="c-1",
                    confidence=0.9,
                    supporting_span_ids=("span-1",),
                    claim_text_snippet="test claim",
                ),
            ),
        )
        import json

        data = contract.to_dict()
        # Must be JSON-safe.
        json.dumps(data)
        assert data["claim_confidences"][0]["claim_id"] == "c-1"
        assert data["claim_confidences"][0]["confidence"] == pytest.approx(0.9)
