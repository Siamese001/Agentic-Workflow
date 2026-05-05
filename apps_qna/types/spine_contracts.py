"""apps_qna spine contracts — app-owned types distinct from canonical agentic_core.

W0 thin-slice: defines the contract shapes that flow through the spine pipeline.
These are app-owned (not canonical agentic_core) because they describe
apps_qna-specific evidence and output shapes.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BriefingValidationState(str, Enum):
    """Outcome of uploaded briefing validation."""
    SUFFICIENT = "SUFFICIENT"
    STALE = "STALE"
    INCOMPLETE = "INCOMPLETE"
    MISMATCH = "MISMATCH"


class EvidenceSufficiency(str, Enum):
    """How well the evidence contract satisfies grounding requirements."""
    GROUNDED = "grounded"
    TEMPLATE_ONLY = "template_only"
    EMPTY = "empty"


@dataclass(frozen=True)
class UploadedBriefingEvidenceContract:
    """Evidence contract derived from a validated uploaded briefing.

    Distinct from the canonical C0 FinalEvidenceContract — this is
    app-owned and describes briefing-sourced evidence, not retrieval-
    sourced evidence.
    """

    schema_version: str = "1.0"
    producer: str = "apps_qna.briefing_validator"
    grounded: bool = False
    retrieval_sources: tuple[str, ...] = ()
    briefing_hash: str = ""
    validation_state: BriefingValidationState = BriefingValidationState.SUFFICIENT
    evidence_sufficiency: EvidenceSufficiency = EvidenceSufficiency.TEMPLATE_ONLY

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "grounded": self.grounded,
            "retrieval_sources": list(self.retrieval_sources),
            "briefing_hash": self.briefing_hash,
            "validation_state": self.validation_state.value,
            "evidence_sufficiency": self.evidence_sufficiency.value,
        }


@dataclass(frozen=True)
class CardPackManifestExtended:
    """Extended card pack manifest with evidence refs, tiering, and hashes.

    Extends the existing CardPackManifest (qna_types.py) with spine-
    required fields for audit trail and evidence provenance.
    """

    interview_slug: str = ""
    built_at: str = ""
    builder_version: str = ""
    template_set_version: str = ""
    cards: tuple[str, ...] = ()
    routes_covered: tuple[str, ...] = ()
    interviewers: tuple[str, ...] = ()
    pasted_cards: tuple[str, ...] = ()
    paste_exceeds_chatgpt_limit: bool = False
    evidence_refs: tuple[str, ...] = ()
    tiering: dict[str, str] = field(default_factory=dict)
    card_hashes: dict[str, str] = field(default_factory=dict)
    source_register: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "interview_slug": self.interview_slug,
            "built_at": self.built_at,
            "builder_version": self.builder_version,
            "template_set_version": self.template_set_version,
            "cards": list(self.cards),
            "routes_covered": list(self.routes_covered),
            "interviewers": list(self.interviewers),
            "pasted_cards": list(self.pasted_cards),
            "paste_exceeds_chatgpt_limit": self.paste_exceeds_chatgpt_limit,
            "evidence_refs": list(self.evidence_refs),
            "tiering": dict(self.tiering),
            "card_hashes": dict(self.card_hashes),
            "source_register": list(self.source_register),
        }


class X3Disposition(str, Enum):
    """Exit X3 disposition — exactly one per run."""
    ALLOW_FINISH = "ALLOW_FINISH"
    SAFE_ABSTAIN = "SAFE_ABSTAIN"
    REROUTE = "REROUTE"
    ESCALATE_HITL = "ESCALATE_HITL"
    SAFE_FALLBACK = "SAFE_FALLBACK"


@dataclass(frozen=True)
class ExitReviewPacket:
    """Minimal exit review packet for W0 thin-slice.

    Full shape lands in W4.2 with FEC producer integration.
    """

    x3_disposition: X3Disposition = X3Disposition.ALLOW_FINISH
    final_evidence_contract: dict[str, Any] = field(default_factory=dict)
    manifest: CardPackManifestExtended | None = None
    reason_codes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "x3_disposition": self.x3_disposition.value,
            "final_evidence_contract": dict(self.final_evidence_contract),
            "manifest": self.manifest.to_dict() if self.manifest else None,
            "reason_codes": list(self.reason_codes),
        }


__all__ = [
    "BriefingValidationState",
    "CardPackManifestExtended",
    "EvidenceSufficiency",
    "ExitReviewPacket",
    "UploadedBriefingEvidenceContract",
    "X3Disposition",
]
