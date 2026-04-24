"""C0 producer hook for :class:`ClaimGroundingConfidence` — W5.P3 deposit.

Plan: ``.windsurf/plans/l0-routing-calibration-gap-audit-b3c9d4.md`` §W5.P3.

Helpers that turn C0 retrieval output (cited spans + per-claim
relevance signals) into populated
:class:`~agentic_core.L3_orchestration.types.c0_evidence_contract_types.ClaimGroundingConfidence`
entries.

Two entry points:

* :func:`confidence_from_span_relevance` — straight mapping from a set
  of supporting :class:`CitedSpan` objects to a single claim's
  confidence, using the max of the span relevance scores.

* :func:`enrich_contract_with_claim_confidences` — given an existing
  :class:`C0EvidenceContract` and a caller-supplied claim map
  ``claim_id -> supporting_span_ids``, rebuild the contract with
  ``claim_confidences`` populated.

Back-compat: additive module. No existing C0 call site is required to
import it. New C0 producers call the helpers to populate the optional
``claim_confidences`` field introduced in W1b.P1.
"""

from __future__ import annotations

from typing import Mapping

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0ContractViolation,
    C0EvidenceContract,
    CitedSpan,
    ClaimGroundingConfidence,
)


def confidence_from_span_relevance(
    claim_id: str,
    supporting_spans: tuple[CitedSpan, ...],
    *,
    claim_text_snippet: str = "",
    aggregation: str = "max",
) -> ClaimGroundingConfidence:
    """Build one :class:`ClaimGroundingConfidence` from cited spans.

    Args:
        claim_id: Stable id for the claim within the response.
        supporting_spans: Tuple of :class:`CitedSpan` objects that back
            this claim. When empty, the claim is recorded with
            ``confidence=0.0`` (explicit no-support marker).
        claim_text_snippet: Optional short snippet for telemetry.
        aggregation: How to aggregate span ``relevance_score`` into a
            claim-level confidence. One of:

            * ``"max"``  (default, Vertex-style "strongest-support wins")
            * ``"mean"`` (arithmetic mean of span scores)
            * ``"min"``  (conservative — "weakest-link")

    Returns:
        A validated :class:`ClaimGroundingConfidence`.

    Raises:
        ValueError: ``aggregation`` is not a known strategy.
        C0ContractViolation: propagated from
            :class:`ClaimGroundingConfidence` validation.
    """
    if aggregation not in ("max", "mean", "min"):
        raise ValueError(
            f"aggregation must be 'max' | 'mean' | 'min', got {aggregation!r}",
        )

    if not supporting_spans:
        return ClaimGroundingConfidence(
            claim_id=claim_id,
            confidence=0.0,
            supporting_span_ids=(),
            claim_text_snippet=claim_text_snippet,
        )

    scores = [float(s.relevance_score) for s in supporting_spans]
    # Clip into [0, 1] — some retrieval engines emit mildly over-range scores.
    scores = [min(1.0, max(0.0, s)) for s in scores]
    if aggregation == "max":
        aggregated = max(scores)
    elif aggregation == "mean":
        aggregated = sum(scores) / len(scores)
    else:  # min
        aggregated = min(scores)

    return ClaimGroundingConfidence(
        claim_id=claim_id,
        confidence=aggregated,
        supporting_span_ids=tuple(s.span_id for s in supporting_spans),
        claim_text_snippet=claim_text_snippet,
    )


def enrich_contract_with_claim_confidences(
    contract: C0EvidenceContract,
    claim_to_span_ids: Mapping[str, tuple[str, ...]],
    *,
    claim_text_snippets: Mapping[str, str] | None = None,
    aggregation: str = "max",
) -> C0EvidenceContract:
    """Rebuild ``contract`` with ``claim_confidences`` populated.

    Args:
        contract: Existing contract (typically from C0.5).
        claim_to_span_ids: Mapping ``claim_id -> (span_id, span_id, ...)``
            where each span_id MUST exist in ``contract.cited_spans``.
            Keys with empty value tuples produce a ``confidence=0.0``
            "no support" marker for that claim.
        claim_text_snippets: Optional per-claim snippets for telemetry.
        aggregation: Passed through to :func:`confidence_from_span_relevance`.

    Returns:
        A NEW :class:`C0EvidenceContract` — the original is not mutated
        (both dataclasses are frozen).

    Raises:
        C0ContractViolation: any referenced span_id is missing from
            ``contract.cited_spans``, or per-claim validation fails.
    """
    span_index: dict[str, CitedSpan] = {s.span_id: s for s in contract.cited_spans}
    snippets = dict(claim_text_snippets or {})

    claim_confidences: list[ClaimGroundingConfidence] = []
    for claim_id, span_ids in claim_to_span_ids.items():
        resolved_spans: list[CitedSpan] = []
        for span_id in span_ids:
            if span_id not in span_index:
                raise C0ContractViolation(
                    f"claim {claim_id!r} references unknown span_id {span_id!r}; "
                    f"span must be present in contract.cited_spans",
                )
            resolved_spans.append(span_index[span_id])
        claim_confidences.append(
            confidence_from_span_relevance(
                claim_id,
                tuple(resolved_spans),
                claim_text_snippet=snippets.get(claim_id, ""),
                aggregation=aggregation,
            ),
        )

    # Rebuild to preserve HMAC + hash invariants.
    return C0EvidenceContract.build(
        retrieval_id=contract.retrieval_id,
        request_id=contract.request_id,
        coverage_score=contract.coverage_score,
        cited_spans=contract.cited_spans,
        claim_confidences=tuple(claim_confidences),
    )


__all__ = [
    "confidence_from_span_relevance",
    "enrich_contract_with_claim_confidences",
]
