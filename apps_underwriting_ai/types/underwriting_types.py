"""Frozen dataclass contracts for apps_underwriting_ai.

These are intentionally minimal — enough to drive the 5-stage HOP pipeline
end-to-end with structured inputs and outputs. Real underwriting domain
models (premium calculation, actuarial features, regulatory compliance
fields) live downstream of this skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DecisionVerdict(str, Enum):
    """Final verdict emitted by the assemble_decision stage."""

    APPROVE = "approve"
    DECLINE = "decline"
    REFER = "refer"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class UnderwritingRequest:
    """Input contract for an underwriting run.

    Attributes:
        request_id: Stable identifier for this underwriting request.
        applicant_id: Identifier for the applicant under review.
        product_class: Insurance/credit product class (e.g., 'auto', 'small_business_loan').
        documents: List of document descriptors submitted with the application.
        metadata: Free-form metadata for downstream consumers.
    """

    request_id: str
    applicant_id: str
    product_class: str
    documents: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceRecord:
    """Single evidence entry registered during the run."""

    evidence_id: str
    source: str
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceRegister:
    """Tamper-evident register of evidence collected during the run."""

    request_id: str
    records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReconciliationResult:
    """Output of the reconcile_documents stage."""

    reconciled_count: int = 0
    unresolved_count: int = 0
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RiskFeatures:
    """Output of the derive_features stage."""

    feature_vector: dict[str, float] = field(default_factory=dict)
    derived_at: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DecisionPacket:
    """Output of the assemble_decision stage."""

    request_id: str
    verdict: DecisionVerdict
    rationale: str = ""
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    feature_summary: dict[str, float] = field(default_factory=dict)
    gate_violations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class UnderwritingResult:
    """Top-level result of an UnderwritingEngine.run()."""

    request_id: str
    decision: DecisionPacket
    register: EvidenceRegister
    features: RiskFeatures
    reconciliation: ReconciliationResult
    trace_id: str = ""
