from __future__ import annotations

from dataclasses import asdict, dataclass
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


@dataclass(frozen=True)
class C0EvidenceContract:
    retrieval_id: str
    request_id: str
    coverage_score: float
    abstain_hint: bool
    cited_spans: tuple[CitedSpan, ...]
    evidence_hmac: str

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
        )
        contract.validate()
        return contract

    def to_dict(self) -> dict:
        return {
            "retrieval_id": self.retrieval_id,
            "request_id": self.request_id,
            "coverage_score": self.coverage_score,
            "abstain_hint": self.abstain_hint,
            "cited_spans": [asdict(span) for span in self.cited_spans],
            "evidence_hmac": self.evidence_hmac,
        }
