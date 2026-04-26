"""Generated L5 contract dataclasses for ``00A.8_L5_Runtime_Certification_Binding.md``.

Source doctrine: ``docs/reference/00_L5_Policy_Plane/00A.8_L5_Runtime_Certification_Binding.md``
Module: ``agentic_core.L5_safety.contracts.runtime_binding``
Generated count: 19 contracts

Every class below is an evidence-only frozen dataclass. L5 contracts must
not emit runtime dispositions. See ``_base.py`` for the kind hierarchy,
``_vocab.py`` for the controlled vocabularies, and ``_status_enums.py``
for per-status field value sets.

Re-run ``python tools/l5_contracts/generate_contracts.py`` to regenerate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
from ._status_enums import (
    MatchStatus,
)


@dataclass(frozen=True, slots=True)
class BlueprintEvidenceRef(L5Ref):
    """L5 doctrine output ``blueprint_evidence_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: blueprint_evidence_ref.
    """

    output_name: ClassVar[str] = "blueprint_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("blueprint_evidence_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class CapabilityScopeRef(L5Ref):
    """L5 doctrine output ``capability_scope_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: capability_scope_ref.
    """

    output_name: ClassVar[str] = "capability_scope_ref"
    output_names: ClassVar[tuple[str, ...]] = ("capability_scope_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class EgressCertRef(L5Ref):
    """L5 doctrine output ``egress_cert_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: egress_cert_ref.
    """

    output_name: ClassVar[str] = "egress_cert_ref"
    output_names: ClassVar[tuple[str, ...]] = ("egress_cert_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class HitlReclearanceRef(L5Ref):
    """L5 doctrine output ``hitl_reclearance_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: hitl_reclearance_ref.
    """

    output_name: ClassVar[str] = "hitl_reclearance_ref"
    output_names: ClassVar[tuple[str, ...]] = ("hitl_reclearance_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class L5SnapshotVerificationReceipt(L5Receipt):
    """L5 doctrine output ``L5SnapshotVerificationReceipt`` (kind=receipt).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: L5SnapshotVerificationReceipt.
    """

    output_name: ClassVar[str] = "L5SnapshotVerificationReceipt"
    output_names: ClassVar[tuple[str, ...]] = ("L5SnapshotVerificationReceipt",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "receipt"


@dataclass(frozen=True, slots=True)
class LiveSnapshotRef(L5Ref):
    """L5 doctrine output ``live_snapshot_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: live_snapshot_ref.
    """

    output_name: ClassVar[str] = "live_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("live_snapshot_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class MatchStatus(L5Status):
    """L5 doctrine output ``match_status`` (kind=status).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: match_status.
    """

    output_name: ClassVar[str] = "match_status"
    output_names: ClassVar[tuple[str, ...]] = ("match_status",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "status"

    allowed_values: ClassVar[tuple[str, ...]] = (
        "MATCH",
        "MISMATCH",
        "STALE",
        "UNKNOWN",
    )
    value_enum: ClassVar[type] = MatchStatus

    def __post_init__(self) -> None:
        if self.status_value and self.status_value not in self.allowed_values:
            raise ValueError(
                f"{type(self).__name__}.status_value={self.status_value!r} "
                f"not in doctrine value set {self.allowed_values!r}"
            )


@dataclass(frozen=True, slots=True)
class OriginTrustRef(L5Ref):
    """L5 doctrine output ``origin_trust_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: origin_trust_ref.
    """

    output_name: ClassVar[str] = "origin_trust_ref"
    output_names: ClassVar[tuple[str, ...]] = ("origin_trust_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PacketRef(L5Ref):
    """L5 doctrine output ``packet_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: packet_ref.
    """

    output_name: ClassVar[str] = "packet_ref"
    output_names: ClassVar[tuple[str, ...]] = ("packet_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PolicyEvidenceRef(L5Ref):
    """L5 doctrine output ``policy_evidence_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: policy_evidence_ref.
    """

    output_name: ClassVar[str] = "policy_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("policy_evidence_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PrincipalRef(L5Ref):
    """L5 doctrine output ``principal_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: principal_ref.
    """

    output_name: ClassVar[str] = "principal_ref"
    output_names: ClassVar[tuple[str, ...]] = ("principal_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class PromptEnvelope(L5Envelope):
    """L5 doctrine output ``PromptEnvelope`` (kind=envelope).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: PromptEnvelope.
    """

    output_name: ClassVar[str] = "PromptEnvelope"
    output_names: ClassVar[tuple[str, ...]] = ("PromptEnvelope",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "envelope"


@dataclass(frozen=True, slots=True)
class RegistryEvidenceRef(L5Ref):
    """L5 doctrine output ``registry_evidence_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: registry_evidence_ref.
    """

    output_name: ClassVar[str] = "registry_evidence_ref"
    output_names: ClassVar[tuple[str, ...]] = ("registry_evidence_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReplayAuditRef(L5Ref):
    """L5 doctrine output ``replay_audit_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: replay_audit_ref.
    """

    output_name: ClassVar[str] = "replay_audit_ref"
    output_names: ClassVar[tuple[str, ...]] = ("replay_audit_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class ReplaySnapshotRef(L5Ref):
    """L5 doctrine output ``replay_snapshot_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: replay_snapshot_ref.
    """

    output_name: ClassVar[str] = "replay_snapshot_ref"
    output_names: ClassVar[tuple[str, ...]] = ("replay_snapshot_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class SandboxScopeRef(L5Ref):
    """L5 doctrine output ``sandbox_scope_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: sandbox_scope_ref.
    """

    output_name: ClassVar[str] = "sandbox_scope_ref"
    output_names: ClassVar[tuple[str, ...]] = ("sandbox_scope_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class StaticGovernanceRef(L5Ref):
    """L5 doctrine output ``static_governance_ref`` (kind=ref).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: static_governance_ref.
    """

    output_name: ClassVar[str] = "static_governance_ref"
    output_names: ClassVar[tuple[str, ...]] = ("static_governance_ref",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "ref"


@dataclass(frozen=True, slots=True)
class TestExitRequiresL5ReclearanceForHumanModifiedPacket(L5Packet):
    """L5 doctrine output ``test_exit_requires_l5_reclearance_for_human_modified_packet`` (kind=packet).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: test_exit_requires_l5_reclearance_for_human_modified_packet.
    """

    output_name: ClassVar[str] = "test_exit_requires_l5_reclearance_for_human_modified_packet"
    output_names: ClassVar[tuple[str, ...]] = ("test_exit_requires_l5_reclearance_for_human_modified_packet",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "packet"


@dataclass(frozen=True, slots=True)
class TestL2E2RejectsMissingL5BindingForGovernedPacket(L5Packet):
    """L5 doctrine output ``test_l2_e2_rejects_missing_l5_binding_for_governed_packet`` (kind=packet).

    Source doctrine: ``00A.8_L5_Runtime_Certification_Binding.md``.
    Canonical doctrine names: test_l2_e2_rejects_missing_l5_binding_for_governed_packet.
    """

    output_name: ClassVar[str] = "test_l2_e2_rejects_missing_l5_binding_for_governed_packet"
    output_names: ClassVar[tuple[str, ...]] = ("test_l2_e2_rejects_missing_l5_binding_for_governed_packet",)
    source_doc: ClassVar[str] = "00A.8_L5_Runtime_Certification_Binding.md"
    output_kind: ClassVar[str] = "packet"


__all__ = [
    "BlueprintEvidenceRef",
    "CapabilityScopeRef",
    "EgressCertRef",
    "HitlReclearanceRef",
    "L5SnapshotVerificationReceipt",
    "LiveSnapshotRef",
    "MatchStatus",
    "OriginTrustRef",
    "PacketRef",
    "PolicyEvidenceRef",
    "PrincipalRef",
    "PromptEnvelope",
    "RegistryEvidenceRef",
    "ReplayAuditRef",
    "ReplaySnapshotRef",
    "SandboxScopeRef",
    "StaticGovernanceRef",
    "TestExitRequiresL5ReclearanceForHumanModifiedPacket",
    "TestL2E2RejectsMissingL5BindingForGovernedPacket",
]
