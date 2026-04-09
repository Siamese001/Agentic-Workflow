"""C0EvidenceContract — mandatory typed output of the C0 retrieval pipeline (B05 — GAP-007, REQ-007/REQ-008).

The C0 Context Engine MUST produce this contract after every retrieval pass.
The Prompt Assembler MUST validate it before building a PromptEnvelope.
abstain_hint=True forces the Prompt Assembler to emit an ABSTAIN disposition.

Layer authority: L3_orchestration (C0 context engine / retrieval plane).
Prompt assembler (prompt_governance) imports this type; C0 must never import from PA.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from typing import Any, Optional

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_pulls_context,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

emit_replay_key("p0", "c0_evidence_contract_types")
emit_determinism_digest("p0", "c0_evidence_contract_types")
_emit_reads_policy_state("p1", "c0_evidence_contract_types", "L3_C0")
_emit_verifies_policy("p1", "c0_evidence_contract_types", "c0_policy_check")
_emit_verifies_boundary("p1", "c0_evidence_contract_types", "c0_boundary_check")
_emit_hard_fails_untranscripted("p1", "c0_evidence_contract_types")
_emit_gated_by_confidence("p1", "c0_evidence_contract_types", "c0_confidence_gate")
_emit_pulls_context("p1", "c0_evidence_contract_types", "c0_context_pull")

_ABSTAIN_COVERAGE_THRESHOLD = 0.30


class C0ContractViolation(ValueError):
    """Raised when C0EvidenceContract validation fails.

    Prompt assembler must not build an envelope if this is raised.
    """


@dataclass(frozen=True)
class CitedSpan:
    """A single piece of evidence cited in the retrieval result."""

    span_id: str
    source_ref: str
    text_snippet: str
    relevance_score: float
    chunk_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_id": self.span_id,
            "source_ref": self.source_ref,
            "text_snippet": self.text_snippet,
            "relevance_score": self.relevance_score,
            "chunk_hash": self.chunk_hash,
        }


@dataclass(frozen=True)
class C0EvidenceContract:
    """Mandatory typed output of the C0 retrieval pipeline (REQ-007, REQ-008).

    All six fields are required.  abstain_hint=True means the prompt assembler
    MUST emit an ABSTAIN disposition — not hallucinate evidence.

    Fields:
        retrieval_id        — unique identifier for this retrieval pass
        request_id          — the upstream request this evidence serves
        coverage_score      — 0.0–1.0; below ABSTAIN threshold → abstain_hint=True
        abstain_hint        — if True, PA must emit ABSTAIN; must not be overridden
        cited_spans         — tuple of CitedSpan objects (may be empty only if abstain_hint=True)
        evidence_hmac       — HMAC-SHA256 of the canonical evidence payload
    """

    retrieval_id: str
    request_id: str
    coverage_score: float
    abstain_hint: bool
    cited_spans: tuple
    evidence_hmac: str

    def validate(self) -> None:
        """Raise C0ContractViolation if contract is invalid.

        Called by hybrid search engine before returning to prompt assembler.
        """
        if not self.retrieval_id or not self.retrieval_id.strip():
            raise C0ContractViolation("retrieval_id must be a non-empty string.")
        if not self.request_id or not self.request_id.strip():
            raise C0ContractViolation("request_id must be a non-empty string.")
        if not (0.0 <= self.coverage_score <= 1.0):
            raise C0ContractViolation(f"coverage_score must be in [0.0, 1.0], got {self.coverage_score}")
        if not self.abstain_hint and not self.cited_spans:
            raise C0ContractViolation(
                "cited_spans must be non-empty when abstain_hint=False. "
                "C0 must not produce an empty evidence contract without setting abstain_hint=True."
            )
        if not self.evidence_hmac or not self.evidence_hmac.strip():
            raise C0ContractViolation("evidence_hmac must be a non-empty string.")
        for i, span in enumerate(self.cited_spans):
            if not isinstance(span, CitedSpan):
                raise C0ContractViolation(f"cited_spans[{i}] must be a CitedSpan, got {type(span).__name__}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "retrieval_id": self.retrieval_id,
            "request_id": self.request_id,
            "coverage_score": self.coverage_score,
            "abstain_hint": self.abstain_hint,
            "cited_spans": [s.to_dict() for s in self.cited_spans],
            "evidence_hmac": self.evidence_hmac,
        }

    @classmethod
    def compute_hmac(cls, spans: tuple, request_id: str, secret: bytes = b"c0-hmac-key") -> str:
        """Compute deterministic HMAC-SHA256 over the canonical evidence payload."""
        canonical = request_id + "|" + "|".join(sorted(s.chunk_hash for s in spans))
        return hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()

    @classmethod
    def build(
        cls,
        retrieval_id: str,
        request_id: str,
        coverage_score: float,
        cited_spans: tuple,
        hmac_secret: bytes = b"c0-hmac-key",
    ) -> "C0EvidenceContract":
        """Factory: build a validated C0EvidenceContract, setting abstain_hint automatically."""
        abstain_hint = coverage_score < _ABSTAIN_COVERAGE_THRESHOLD or not cited_spans
        evidence_hmac = cls.compute_hmac(cited_spans, request_id, secret=hmac_secret)
        contract = cls(
            retrieval_id=retrieval_id,
            request_id=request_id,
            coverage_score=coverage_score,
            abstain_hint=abstain_hint,
            cited_spans=cited_spans,
            evidence_hmac=evidence_hmac,
        )
        contract.validate()
        return contract
