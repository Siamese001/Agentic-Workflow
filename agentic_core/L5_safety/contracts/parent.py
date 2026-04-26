"""Generated L5 contract dataclasses for ``00_L5_Governance_Safety_detailed.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00_L5_Governance_Safety_detailed.md``
Module: ``agentic_core.L5_safety.contracts.parent``
Generated count: 7 contracts

Every class below is an evidence-only frozen dataclass. L5 contracts must
not emit runtime dispositions. See ``_base.py`` for the kind hierarchy
and ``_vocab.py`` for the controlled vocabularies.

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ._base import (
    L5OutputBase,
    L5Packet,
    L5Receipt,
    L5Report,
    L5Manifest,
    L5Log,
    L5Diff,
    L5Envelope,
    L5Result,
    L5Map,
    L5Status,
    L5Ref,
    L5Context,
    L5Token,
)


@dataclass(frozen=True, slots=True)
class AuthorityContextEvidenceRef(L5Ref):
    """L5 doctrine output ``authority_context_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: authority_context_evidence_ref.
    """

    output_name: ClassVar[str] = "authority_context_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("authority_context_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class CertificationGapEvidenceRef(L5Ref):
    """L5 doctrine output ``certification_gap_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: certification_gap_evidence_ref.
    """

    output_name: ClassVar[str] = "certification_gap_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("certification_gap_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class EgressCertificationEvidenceRef(L5Ref):
    """L5 doctrine output ``egress_certification_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: egress_certification_evidence_ref.
    """

    output_name: ClassVar[str] = "egress_certification_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("egress_certification_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HumanReclearanceEvidenceRef(L5Ref):
    """L5 doctrine output ``human_reclearance_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: human_reclearance_evidence_ref.
    """

    output_name: ClassVar[str] = "human_reclearance_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("human_reclearance_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class OriginTrustEvidenceRef(L5Ref):
    """L5 doctrine output ``origin_trust_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: origin_trust_evidence_ref.
    """

    output_name: ClassVar[str] = "origin_trust_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("origin_trust_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReplayAuditEvidenceRef(L5Ref):
    """L5 doctrine output ``replay_audit_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: replay_audit_evidence_ref.
    """

    output_name: ClassVar[str] = "replay_audit_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("replay_audit_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class StaticGovernanceEvidenceRef(L5Ref):
    """L5 doctrine output ``static_governance_evidence_ref`` (kind=ref).

    Source doctrine: ``00_L5_Governance_Safety_detailed.md``.
    Canonical doctrine names: static_governance_evidence_ref.
    """

    output_name: ClassVar[str] = "static_governance_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("static_governance_evidence_ref",)
    source_doc: ClassVar[str] = "00_L5_Governance_Safety_detailed.md"
    output_kind: ClassVar[str] = "ref"


__all__ = [
    "AuthorityContextEvidenceRef",
    "CertificationGapEvidenceRef",
    "EgressCertificationEvidenceRef",
    "HumanReclearanceEvidenceRef",
    "OriginTrustEvidenceRef",
    "ReplayAuditEvidenceRef",
    "StaticGovernanceEvidenceRef",
]
