from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import hmac
import json
from typing import Iterable

_ABSTAIN_COVERAGE_THRESHOLD = 0.20
_HMAC_KEY = b"agentic-core-c0-contract"


class C0ContractViolation(ValueError):
    pass


@dataclass(frozen=True)
class CitedSpan:
    span_id: str
    source_ref: str
    text_snippet: str
    relevance_score: float
    chunk_hash: str


# =============================================================================
# W1b.P1 — Per-claim grounding confidence (Vertex AI grounded-answer pattern).
#
# Plan: docs/archive/windsurf/legacy-tree/plans/l0-routing-calibration-gap-audit-b3c9d4.md §W1b.P1.
#
# Vertex AI emits a confidence_score in [0,1] for each sentence/claim in a
# grounded answer. This dataclass is the analog.
#
# Additive: :class:`C0EvidenceContract.claim_confidences` defaults to an
# empty tuple, so all existing producers continue to work unchanged.
# =============================================================================


@dataclass(frozen=True)
class ClaimGroundingConfidence:
    """Per-claim grounding confidence (Vertex-style).

    Fields:
        claim_id: Stable identifier for the claim within the response.
        confidence: Score in ``[0.0, 1.0]`` — 1.0 fully supported by
            cited evidence, 0.0 unsupported / hallucination risk.
        supporting_span_ids: Tuple of :attr:`CitedSpan.span_id` strings
            that back this claim. Empty tuple legal ONLY when
            ``confidence == 0.0`` (explicit "no support" marker).
        claim_text_snippet: Optional short snippet for telemetry / review.
    """

    claim_id: str
    confidence: float
    supporting_span_ids: tuple[str, ...] = ()
    claim_text_snippet: str = ""

    def __post_init__(self) -> None:
        if not self.claim_id or not self.claim_id.strip():
            raise C0ContractViolation("claim_id is required")
        if not isinstance(self.confidence, (int, float)):
            raise C0ContractViolation(
                f"confidence must be numeric, got {type(self.confidence).__name__}",
            )
        if self.confidence != self.confidence:  # NaN
            raise C0ContractViolation("confidence must not be NaN")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise C0ContractViolation(
                f"confidence must be in [0,1], got {self.confidence!r}",
            )
        # Guard against "claim with 0.8 confidence but no supporting spans".
        if not self.supporting_span_ids and float(self.confidence) > 0.0:
            raise C0ContractViolation(
                f"claim {self.claim_id!r} has confidence={self.confidence} "
                f"but no supporting_span_ids; set confidence=0.0 for "
                f"explicit no-support or provide at least one span id",
            )


@dataclass(frozen=True)
class C0EvidenceContract:
    retrieval_id: str
    request_id: str
    coverage_score: float
    abstain_hint: bool
    cited_spans: tuple[CitedSpan, ...]
    evidence_hmac: str
    # W1b.P1 additive: per-claim grounding confidences. Empty tuple when
    # not computed (default, back-compat) — consumers treat absence as
    # "no per-claim signal available" and fall back to ``coverage_score``.
    claim_confidences: tuple[ClaimGroundingConfidence, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.retrieval_id or not self.retrieval_id.strip():
            raise C0ContractViolation("retrieval_id is required")
        if not self.request_id or not self.request_id.strip():
            raise C0ContractViolation("request_id is required")
        if not 0.0 <= self.coverage_score <= 1.0:
            raise C0ContractViolation("coverage_score must be between 0 and 1")
        if not self.abstain_hint and len(self.cited_spans) == 0:
            raise C0ContractViolation("non-abstain contract requires cited spans")
        if any(not isinstance(span, CitedSpan) for span in self.cited_spans):
            raise C0ContractViolation("all cited_spans must be CitedSpan instances")
        if not self.evidence_hmac:
            raise C0ContractViolation("evidence_hmac is required")
        # W1b.P1: validate per-claim confidences when present.
        if any(not isinstance(c, ClaimGroundingConfidence) for c in self.claim_confidences):
            raise C0ContractViolation(
                "all claim_confidences must be ClaimGroundingConfidence instances",
            )
        # Every supporting_span_id MUST exist in cited_spans.
        known_span_ids = {span.span_id for span in self.cited_spans}
        for claim in self.claim_confidences:
            for span_id in claim.supporting_span_ids:
                if span_id not in known_span_ids:
                    raise C0ContractViolation(
                        f"claim {claim.claim_id!r} references unknown span_id "
                        f"{span_id!r}; cited_spans does not contain it",
                    )

    @staticmethod
    def compute_hmac(cited_spans: Iterable[CitedSpan], request_id: str) -> str:
        payload = {
            "request_id": request_id,
            "spans": [asdict(span) for span in cited_spans],
        }
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hmac.new(_HMAC_KEY, blob, hashlib.sha256).hexdigest()

    @classmethod
    def build(
        cls,
        *,
        retrieval_id: str,
        request_id: str,
        coverage_score: float,
        cited_spans: tuple[CitedSpan, ...],
        claim_confidences: tuple[ClaimGroundingConfidence, ...] = (),
    ) -> "C0EvidenceContract":
        normalized_spans = tuple(cited_spans)
        abstain_hint = coverage_score < _ABSTAIN_COVERAGE_THRESHOLD or len(normalized_spans) == 0
        contract = cls(
            retrieval_id=retrieval_id,
            request_id=request_id,
            coverage_score=coverage_score,
            abstain_hint=abstain_hint,
            cited_spans=normalized_spans,
            evidence_hmac=cls.compute_hmac(normalized_spans, request_id),
            claim_confidences=tuple(claim_confidences),
        )
        contract.validate()
        return contract

    def mean_claim_confidence(self) -> float:
        """Arithmetic mean of per-claim confidences (0.0 if none present)."""
        if not self.claim_confidences:
            return 0.0
        return sum(c.confidence for c in self.claim_confidences) / len(self.claim_confidences)

    def min_claim_confidence(self) -> float:
        """Minimum per-claim confidence — the Vertex conservative reading."""
        if not self.claim_confidences:
            return 0.0
        return min(c.confidence for c in self.claim_confidences)

    def to_dict(self) -> dict:
        return {
            "retrieval_id": self.retrieval_id,
            "request_id": self.request_id,
            "coverage_score": self.coverage_score,
            "abstain_hint": self.abstain_hint,
            "cited_spans": [asdict(span) for span in self.cited_spans],
            "evidence_hmac": self.evidence_hmac,
            "claim_confidences": [asdict(c) for c in self.claim_confidences],
        }
