"""apps_qna spine contracts — app-owned types distinct from canonical agentic_core.

W2.3: Evidence contract types moved to evidence_contracts.py.
This module re-exports them for backward compatibility and keeps
app-specific pipeline types (CardPackManifestExtended, ExitReviewPacket, X3Disposition).

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W2.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from apps_qna.types.evidence_contracts import (
    BriefingValidationState,
    EvidenceSufficiency,
    UploadedBriefingEvidenceContract,
)


class X3Disposition(str, Enum):
    """Exit X3 disposition — exactly one per run."""
    ALLOW_FINISH = "ALLOW_FINISH"
    SAFE_ABSTAIN = "SAFE_ABSTAIN"
    REROUTE = "REROUTE"
    ESCALATE_HITL = "ESCALATE_HITL"
    SAFE_FALLBACK = "SAFE_FALLBACK"


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
