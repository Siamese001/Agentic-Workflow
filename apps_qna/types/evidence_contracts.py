"""Evidence contract types — FinalEvidenceContract and UploadedBriefingEvidenceContract.

W2.3: Typed evidence contracts distinct from each other.
- FinalEvidenceContract: produced by canonical C0 (retrieval-backed)
- UploadedBriefingEvidenceContract: produced by briefing validator (file-backed)

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W2.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EvidenceSufficiency(str, Enum):
    GROUNDED = "grounded"
    TEMPLATE_ONLY = "template_only"
    EMPTY = "empty"


class BriefingValidationState(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    STALE = "STALE"
    INCOMPLETE = "INCOMPLETE"
    MISMATCH = "MISMATCH"


@dataclass(frozen=True)
class FinalEvidenceContract:
    """Canonical C0-produced evidence contract — retrieval-backed.

    Produced by agentic_core C0 retrieval. apps_qna consumes this
    unchanged via the thin adapter.

    W3 / bge-m3-deferred-scope-remaining-c4e7a1: ``provider_dispatch`` is
    an optional sidecar dict produced by apps_qna.engines.dispatch. None
    means the dispatch layer was not invoked (e.g. stub mode or pre-W3 runs).
    """

    schema_version: str = "1.0"
    producer: str = "agentic_core.C0"
    grounded: bool = True
    retrieval_sources: tuple[str, ...] = ()
    route_id: str = ""
    evidence_sufficiency: str = "grounded"
    interview_slug: str = ""
    query_text: str = ""
    source_register: tuple[str, ...] = ()
    freshness_assessment: str = "current"
    claim_confidence: float = 0.0
    contradiction_flags: tuple[str, ...] = ()
    provider_dispatch: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "grounded": self.grounded,
            "retrieval_sources": list(self.retrieval_sources),
            "route_id": self.route_id,
            "evidence_sufficiency": self.evidence_sufficiency,
            "interview_slug": self.interview_slug,
            "query_text": self.query_text,
            "source_register": list(self.source_register),
            "freshness_assessment": self.freshness_assessment,
            "claim_confidence": self.claim_confidence,
            "contradiction_flags": list(self.contradiction_flags),
        }
        if self.provider_dispatch is not None:
            d["provider_dispatch"] = self.provider_dispatch
        return d


@dataclass(frozen=True)
class UploadedBriefingEvidenceContract:
    """App-owned evidence contract from a validated uploaded briefing.

    Distinct from FinalEvidenceContract — this is briefing-sourced,
    not retrieval-sourced. Produced by apps_qna.briefing_validator.
    """

    schema_version: str = "1.0"
    producer: str = "apps_qna.briefing_validator"
    grounded: bool = False
    retrieval_sources: tuple[str, ...] = ()
    briefing_hash: str = ""
    validation_state: BriefingValidationState = BriefingValidationState.INCOMPLETE
    evidence_sufficiency: EvidenceSufficiency = EvidenceSufficiency.EMPTY
    company_name: str = ""
    role_title: str = ""
    briefing_size_bytes: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "grounded": self.grounded,
            "retrieval_sources": list(self.retrieval_sources),
            "briefing_hash": self.briefing_hash,
            "validation_state": self.validation_state.value,
            "evidence_sufficiency": self.evidence_sufficiency.value,
            "company_name": self.company_name,
            "role_title": self.role_title,
            "briefing_size_bytes": self.briefing_size_bytes,
        }


__all__ = [
    "BriefingValidationState",
    "EvidenceSufficiency",
    "FinalEvidenceContract",
    "UploadedBriefingEvidenceContract",
]
