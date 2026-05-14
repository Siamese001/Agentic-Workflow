"""L5 Certification Packet producer contracts — W1 contract dataclasses.

Defines the three frozen dataclasses required by the L5CertificationPacket
producer (W2) and EgressCertifier interface (W3):

    ChildCertifierReceipt   — one per child certifier domain
    EgressCertificationReceipt — provider-governance evidence (symbolic refs)
    L5CertificationPacket   — top-level L5Result subclass (evidence-only)

Boundary invariants (enforced by GOV-3 and tests):
  - No app-specific literals (forbidden by GOV-3 scan)
  - No provider SDK imports (forbidden by GOV-3 scan)
  - No live runtime disposition tokens, gate-verdict, or disposition writes
  - No network, filesystem, or provider calls
  - Packet status restricted to L5_CERTIFIED | L5_NOT_CERTIFIED
  - No runtime dispositions (see _vocab.FORBIDDEN_RUNTIME_DISPOSITIONS)

L5_CERTIFIED semantics:
  Evidence-only certification. Does not emit live runtime decisions, gate
  verdicts, disposition writes, or commit approvals. Downstream systems make
  those decisions independently from the evidence packet.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

from agentic_core.L5_safety.contracts._base import L5Result
from agentic_core.L5_safety.contracts._vocab import FORBIDDEN_RUNTIME_DISPOSITIONS

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PACKET_ALLOWED_STATUSES: frozenset[str] = frozenset(
    {"L5_CERTIFIED", "L5_NOT_CERTIFIED"}
)

_CHILD_APPLICABILITY_VALUES: frozenset[str] = frozenset(
    {"REQUIRED", "OPTIONAL", "NOT_APPLICABLE"}
)

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def _is_hex64(value: str) -> bool:
    return bool(_HEX64_RE.match(value))


# ---------------------------------------------------------------------------
# ChildCertifierReceipt
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ChildCertifierReceipt:
    """Evidence receipt from one child certifier domain.

    Each app-owned certifier produces one of these; the L5PacketProducer
    (W2) assembles them into L5CertificationPacket.child_receipts.

    ``applicability`` must be one of REQUIRED | OPTIONAL | NOT_APPLICABLE.
    When NOT_APPLICABLE all three justification fields are required.
    """

    domain: str
    applicability: str
    certified: bool

    evidence_digest: str = ""
    evidence_ref: str = ""
    reason_codes: tuple[str, ...] = ()
    notes: str = ""

    not_applicable_reason: str = ""
    deciding_policy_ref: str = ""
    deciding_stage: str = ""

    def __post_init__(self) -> None:
        if not self.domain:
            raise ValueError("ChildCertifierReceipt.domain must be non-empty.")

        if self.applicability not in _CHILD_APPLICABILITY_VALUES:
            raise ValueError(
                f"ChildCertifierReceipt.applicability {self.applicability!r} is not "
                f"one of {sorted(_CHILD_APPLICABILITY_VALUES)}."
            )

        if self.applicability == "NOT_APPLICABLE":
            missing = [
                field_name
                for field_name, val in (
                    ("not_applicable_reason", self.not_applicable_reason),
                    ("deciding_policy_ref", self.deciding_policy_ref),
                    ("deciding_stage", self.deciding_stage),
                )
                if not val
            ]
            if missing:
                raise ValueError(
                    f"ChildCertifierReceipt with applicability=NOT_APPLICABLE "
                    f"requires non-empty: {missing}. "
                    "AG-4 invariant: NOT_APPLICABLE requires full justification."
                )

        if self.evidence_digest and not _is_hex64(self.evidence_digest):
            raise ValueError(
                "ChildCertifierReceipt.evidence_digest must be 64 lowercase hex chars "
                f"when present, got {self.evidence_digest!r}."
            )


# ---------------------------------------------------------------------------
# EgressCertificationReceipt
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EgressCertificationReceipt:
    """Provider-governance evidence receipt (symbolic refs only).

    Carries no raw prompt text, no raw response text.
    ``response_digest`` must represent a redacted canonical response.
    ``redaction_policy_ref`` is required to prove redaction was applied.

    ``provider_ref`` is a symbolic identifier (e.g. a registry key or URN)
    — never a live SDK client, URL, or credentials object.
    """

    provider_ref: str
    response_digest: str
    redaction_policy_ref: str

    prompt_artifact_ref: str = ""
    egress_policy_ref: str = ""
    schema_version: str = ""
    certified: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.provider_ref:
            raise ValueError(
                "EgressCertificationReceipt.provider_ref must be non-empty "
                "symbolic identifier."
            )

        if not self.redaction_policy_ref:
            raise ValueError(
                "EgressCertificationReceipt.redaction_policy_ref must be non-empty. "
                "Egress receipts require explicit proof that redaction was applied."
            )

        if not self.response_digest:
            raise ValueError(
                "EgressCertificationReceipt.response_digest must be non-empty."
            )

        if not _is_hex64(self.response_digest):
            raise ValueError(
                "EgressCertificationReceipt.response_digest must be 64 lowercase "
                f"hex chars (sha256 of redacted canonical response), "
                f"got {self.response_digest!r}."
            )


# ---------------------------------------------------------------------------
# L5CertificationPacket
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class L5CertificationPacket(L5Result):
    """Top-level L5 certification evidence packet.

    Subclasses L5Result (evidence-only, never carries runtime disposition).
    ``is_evidence_only()`` returns True by inheritance.
    ``output_kind`` is inherited as "result".

    ``certification_status`` (inherited from L5Result) is restricted to:
        L5_CERTIFIED      — evidence certification passed
        L5_NOT_CERTIFIED  — evidence certification failed

    L5_CERTIFIED is evidence-only. It does not authorize live runtime
    decisions, gate verdicts, disposition writes, or commit approvals.
    Downstream systems make those decisions independently from the evidence.

    Packet-level partial and not-applicable statuses are forbidden at packet level.
    Use ``child_receipts`` to record per-domain not-applicable decisions.
    """

    child_receipts: tuple[ChildCertifierReceipt, ...] = ()
    egress_receipts: tuple[EgressCertificationReceipt, ...] = ()
    producer_ref: str = ""
    policy_ref: str = ""
    certifier_version: str = ""

    output_name: ClassVar[str] = "l5_certification_packet"
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"

    def __post_init__(self) -> None:
        status = self.certification_status

        if status not in _PACKET_ALLOWED_STATUSES:
            raise ValueError(
                f"L5CertificationPacket.certification_status {status!r} is not "
                f"one of {sorted(_PACKET_ALLOWED_STATUSES)}. "
                "Partial and not-applicable statuses are forbidden at packet level. "
                "Do not reintroduce the certification-ready sentinel."
            )

        for token in FORBIDDEN_RUNTIME_DISPOSITIONS:
            if token in (self.producer_ref or ""):
                raise ValueError(
                    f"L5CertificationPacket.producer_ref contains forbidden "
                    f"runtime disposition token {token!r}."
                )

        if self.digest_sha256 and not _is_hex64(self.digest_sha256):
            raise ValueError(
                "L5CertificationPacket.digest_sha256 must be 64 lowercase hex chars "
                f"when present, got {self.digest_sha256!r}."
            )


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------

__all__ = [
    "ChildCertifierReceipt",
    "EgressCertificationReceipt",
    "L5CertificationPacket",
    "_PACKET_ALLOWED_STATUSES",
    "_CHILD_APPLICABILITY_VALUES",
]
