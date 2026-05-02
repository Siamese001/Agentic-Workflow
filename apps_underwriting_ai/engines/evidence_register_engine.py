"""EvidenceRegisterEngine — initializes the evidence register for a run.

Skeleton implementation. Real evidence registration will hook into
agentic_core's evidence/audit-trail surface. This implementation provides
a stable, deterministic in-memory register suitable for smoke tests and
downstream contract verification.
"""

from __future__ import annotations

from apps_underwriting_ai.types.underwriting_types import (
    EvidenceRecord,
    EvidenceRegister,
    UnderwritingRequest,
)


class EvidenceRegisterEngine:
    """Manages the evidence register across an underwriting run.

    Provides initialization (stage 1) and per-dimension collection methods
    (stage 4): financial, credit, collateral, relationship, policy.

    The register is intentionally a frozen dataclass — collection methods
    return a new register rather than mutating; the call site is expected
    to rebind. The collect_*() methods append a deterministic skeleton
    EvidenceRecord per dimension. Real evidence collection will hook into
    agentic_core data sources.
    """

    def initialize(self, request_id: str) -> EvidenceRegister:
        """Create an empty evidence register for the given request."""
        return EvidenceRegister(request_id=request_id, records=())

    def _append(
        self,
        register: EvidenceRegister,
        record: EvidenceRecord,
    ) -> EvidenceRegister:
        """Return a new register with `record` appended (frozen-safe)."""
        return EvidenceRegister(
            request_id=register.request_id,
            records=(*register.records, record),
        )

    def collect_financial_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> EvidenceRegister:
        """Append a financial-evidence record (skeleton)."""
        record = EvidenceRecord(
            evidence_id=f"{register.request_id}.financial",
            source="skeleton.financial",
            kind="financial",
            payload={"applicant_id": request.applicant_id},
        )
        return self._append(register, record)

    def collect_credit_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> EvidenceRegister:
        """Append a credit-evidence record (skeleton)."""
        record = EvidenceRecord(
            evidence_id=f"{register.request_id}.credit",
            source="skeleton.credit",
            kind="credit",
            payload={"applicant_id": request.applicant_id},
        )
        return self._append(register, record)

    def collect_collateral_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> EvidenceRegister:
        """Append a collateral-evidence record (skeleton)."""
        record = EvidenceRecord(
            evidence_id=f"{register.request_id}.collateral",
            source="skeleton.collateral",
            kind="collateral",
            payload={"applicant_id": request.applicant_id},
        )
        return self._append(register, record)

    def collect_relationship_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
    ) -> EvidenceRegister:
        """Append a relationship-evidence record (skeleton)."""
        record = EvidenceRecord(
            evidence_id=f"{register.request_id}.relationship",
            source="skeleton.relationship",
            kind="relationship",
            payload={"applicant_id": request.applicant_id},
        )
        return self._append(register, record)

    def collect_policy_evidence(
        self,
        register: EvidenceRegister,
        request: UnderwritingRequest,
        policy_exception_count: int = 0,
    ) -> EvidenceRegister:
        """Append a policy-evidence record (skeleton)."""
        record = EvidenceRecord(
            evidence_id=f"{register.request_id}.policy",
            source="skeleton.policy",
            kind="policy",
            payload={
                "applicant_id": request.applicant_id,
                "policy_exception_count": policy_exception_count,
            },
        )
        return self._append(register, record)
