"""V7 6C.S3E Proposal Admission Gate.

Decides whether a draft proposal is ready to enter the 6D gauntlet. No
proposal may bypass this gate.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6C S3E "PROPOSAL ADMISSION GATE".

KPI surface
-----------
``PROPOSAL_EVIDENCE_COMPLETENESS`` — ratio of admitted proposals (of any
verdict) that linked all required artifacts (eval + RCA + evidence).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AdmissionVerdict(str, Enum):
    """Per v7 S3E "DECIDES"."""

    ADMIT_TO_GAUNTLET = "ADMIT_TO_GAUNTLET"
    HOLD_FOR_MORE_EVIDENCE = "HOLD_FOR_MORE_EVIDENCE"
    REJECT_WEAK_PROPOSAL = "REJECT_WEAK_PROPOSAL"
    REQUIRE_SME_REVIEW = "REQUIRE_SME_REVIEW"


# v7 S3E "REQUIRED" list — every field must be non-empty (truthy) for
# admission to ADMIT_TO_GAUNTLET.
_REQUIRED_FIELDS: tuple[str, ...] = (
    "eval_record_id",
    "rca_packet_id",
    "target_surface",
    "proposed_diff",
    "blast_radius",
    "rollback_plan",
    "test_plan",
    "owner",
)


@dataclass(frozen=True)
class AdmissionDecision:
    """Output of the admission gate."""

    proposal_id: str
    verdict: AdmissionVerdict
    missing_fields: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class ProposalDraft:
    """Minimal proposal shape consumed by the gate."""

    proposal_id: str
    eval_record_id: str
    rca_packet_id: str
    target_surface: str
    proposed_diff: str
    blast_radius: str
    rollback_plan: str
    test_plan: str
    owner: str
    freshness_age_seconds: float
    has_open_blocker: bool
    confidence_band: str  # "low" | "medium" | "high"
    requires_sme_review: bool


# Max age before a proposal's underlying eval is considered stale at
# admission time. Default 7 days to match held-proposal aging KPI.
_FRESHNESS_TTL_SECONDS: float = 7.0 * 86400.0


class ProposalAdmissionGate:
    """Decide whether a proposal may enter the 6D gauntlet."""

    def __init__(self) -> None:
        self._total_decisions: int = 0
        self._evidence_complete_decisions: int = 0

    def decide(self, draft: ProposalDraft) -> AdmissionDecision:
        self._total_decisions += 1
        missing: list[str] = []
        for fname in _REQUIRED_FIELDS:
            value = getattr(draft, fname, None)
            if not value:
                missing.append(fname)

        evidence_complete = not missing
        if evidence_complete:
            self._evidence_complete_decisions += 1

        if missing:
            return AdmissionDecision(
                proposal_id=draft.proposal_id,
                verdict=AdmissionVerdict.HOLD_FOR_MORE_EVIDENCE,
                missing_fields=tuple(missing),
                notes=f"missing required fields: {missing}",
            )
        if draft.has_open_blocker:
            return AdmissionDecision(
                proposal_id=draft.proposal_id,
                verdict=AdmissionVerdict.HOLD_FOR_MORE_EVIDENCE,
                missing_fields=(),
                notes="open blocker prevents admission",
            )
        if draft.freshness_age_seconds > _FRESHNESS_TTL_SECONDS:
            return AdmissionDecision(
                proposal_id=draft.proposal_id,
                verdict=AdmissionVerdict.HOLD_FOR_MORE_EVIDENCE,
                missing_fields=(),
                notes="evidence past freshness TTL",
            )
        if draft.confidence_band == "low":
            return AdmissionDecision(
                proposal_id=draft.proposal_id,
                verdict=AdmissionVerdict.REJECT_WEAK_PROPOSAL,
                missing_fields=(),
                notes="confidence band too low",
            )
        if draft.requires_sme_review:
            return AdmissionDecision(
                proposal_id=draft.proposal_id,
                verdict=AdmissionVerdict.REQUIRE_SME_REVIEW,
                missing_fields=(),
                notes="proposal flagged for SME review",
            )
        return AdmissionDecision(
            proposal_id=draft.proposal_id,
            verdict=AdmissionVerdict.ADMIT_TO_GAUNTLET,
            missing_fields=(),
            notes="all admission requirements satisfied",
        )

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(evidence_complete, total)`` decision counters."""
        return (self._evidence_complete_decisions, self._total_decisions)

    def reset(self) -> None:
        self._total_decisions = 0
        self._evidence_complete_decisions = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._evidence_complete_decisions / self._total_decisions
                if self._total_decisions > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.PROPOSAL_EVIDENCE_COMPLETENESS,
                value=ratio,
                timestamp=time.time(),
                source="proposal_admission_gate",
                metadata={"evidence_complete": self._evidence_complete_decisions,
                          "total": self._total_decisions},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break gate
            logger.warning(
                "v7_kpi_proposal_evidence_completeness_failed: %s", exc
            )


__all__ = [
    "AdmissionVerdict",
    "AdmissionDecision",
    "ProposalDraft",
    "ProposalAdmissionGate",
]
