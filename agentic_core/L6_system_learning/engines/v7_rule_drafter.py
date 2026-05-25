"""S3D Rule Drafting v7 wrapper — enforces 12-field draft contract.

Spec (lines 786-838) requires every ``DraftProposalPacket`` to include 12
mandatory fields. The legacy ``rule_drafting_engine`` does not enforce this;
this v7 wrapper validates and produces the canonical packet.

10 ``DraftType`` values (spec lines 820-830).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class DraftType(str, Enum):
    """10 draft types from spec lines 820-830."""

    LOCAL_PATCH = "LOCAL_PATCH"
    THRESHOLD_CHANGE = "THRESHOLD_CHANGE"
    RUBRIC_UPDATE = "RUBRIC_UPDATE"
    PROMPT_UPDATE = "PROMPT_UPDATE"
    RETRIEVAL_PROFILE_UPDATE = "RETRIEVAL_PROFILE_UPDATE"
    POLICY_CLARIFICATION = "POLICY_CLARIFICATION"
    EXEMPLAR_ADDITION = "EXEMPLAR_ADDITION"
    GOLDEN_SET_ADDITION = "GOLDEN_SET_ADDITION"
    TOOL_CONTRACT_TIGHTENING = "TOOL_CONTRACT_TIGHTENING"
    HOLD_FOR_MORE_EVIDENCE = "HOLD_FOR_MORE_EVIDENCE"


REQUIRED_DRAFT_FIELDS: tuple[str, ...] = (
    "target_surface",
    "problem_statement",
    "evidence_link",
    "completed_eval_record_id",
    "rca_packet_id",
    "expected_effect",
    "rollback_plan",
    "blast_radius_statement",
    "affected_tests",
    "migration_notes",
    "owner_signer_identity",
    "expiration_review_ttl",
)


class IncompleteDraftError(ValueError):
    """Raised when a v7 draft is missing one of the 12 required fields."""


@dataclass(frozen=True)
class DraftProposalPacket:
    """Canonical v7 draft proposal packet (spec 836-838)."""

    draft_id: str
    draft_type: DraftType
    target_surface: str
    problem_statement: str
    evidence_link: str
    completed_eval_record_id: str
    rca_packet_id: str
    expected_effect: str
    rollback_plan: str
    blast_radius_statement: str
    affected_tests: tuple[str, ...]
    migration_notes: str
    owner_signer_identity: str
    expiration_review_ttl_epoch: float
    created_at_epoch: float = field(default_factory=time.time)


class V7RuleDrafter:
    """v7 rule drafter — validates and packages a 12-field draft.

    Floor staff propose only (spec line 833). This engine never commits;
    it only produces a ``DraftProposalPacket`` ready for S3E admission.
    """

    def __init__(self) -> None:
        self._drafts_built: int = 0
        self._drafts_rejected: int = 0

    def draft(
        self,
        *,
        draft_id: str,
        draft_type: DraftType,
        fields_payload: Mapping[str, Any],
    ) -> DraftProposalPacket:
        """Construct a packet, validating all 12 required fields are present.

        Raises :class:`IncompleteDraftError` listing every missing field if
        the payload omits any required key. Floor-staff drafters can catch
        this exception and retry with a more complete payload.
        """
        missing = [
            f for f in REQUIRED_DRAFT_FIELDS
            if f not in fields_payload or fields_payload[f] in (None, "", [])
        ]
        if missing:
            self._drafts_rejected += 1
            raise IncompleteDraftError(
                f"draft missing required fields: {missing}"
            )

        affected_raw = fields_payload["affected_tests"]
        affected: tuple[str, ...]
        if isinstance(affected_raw, str):
            affected = (affected_raw,)
        else:
            affected = tuple(str(a) for a in affected_raw)

        try:
            ttl_epoch = float(fields_payload["expiration_review_ttl"])
        except (TypeError, ValueError):
            ttl_epoch = time.time() + 30 * 86400.0  # default 30-day review

        self._drafts_built += 1
        return DraftProposalPacket(
            draft_id=draft_id,
            draft_type=draft_type,
            target_surface=str(fields_payload["target_surface"]),
            problem_statement=str(fields_payload["problem_statement"]),
            evidence_link=str(fields_payload["evidence_link"]),
            completed_eval_record_id=str(
                fields_payload["completed_eval_record_id"]
            ),
            rca_packet_id=str(fields_payload["rca_packet_id"]),
            expected_effect=str(fields_payload["expected_effect"]),
            rollback_plan=str(fields_payload["rollback_plan"]),
            blast_radius_statement=str(
                fields_payload["blast_radius_statement"]
            ),
            affected_tests=affected,
            migration_notes=str(fields_payload["migration_notes"]),
            owner_signer_identity=str(
                fields_payload["owner_signer_identity"]
            ),
            expiration_review_ttl_epoch=ttl_epoch,
        )

    @property
    def counters(self) -> tuple[int, int]:
        return (self._drafts_built, self._drafts_rejected)

    def reset(self) -> None:
        self._drafts_built = 0
        self._drafts_rejected = 0


__all__ = [
    "DraftType",
    "REQUIRED_DRAFT_FIELDS",
    "IncompleteDraftError",
    "DraftProposalPacket",
    "V7RuleDrafter",
]
