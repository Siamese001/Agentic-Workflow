"""
IntakeStatus — terminal status enum for U0 / Request Intake.

Spec source: 01_Request_Intake_detailed.md "CANONICAL OUTPUT VOCABULARY"
and 01.6_Validated_Request_Handoff_detailed.md "Rejection statuses".

These statuses are emitted by the U0 layer ONLY. They are NOT runtime gate
verdicts (G01..G29) and they are NOT exit dispositions. Downstream layers
must never adopt this enum to make their own decisions.
"""

from __future__ import annotations

from enum import Enum


class IntakeStatus(str, Enum):
    """Terminal Intake status. Exactly one of these is set on any
    IntakeAuditReceipt or final handoff outcome."""

    VALIDATED_FOR_L1 = "VALIDATED_FOR_L1"
    REJECTED_AT_TRANSPORT = "REJECTED_AT_TRANSPORT"
    REJECTED_AT_IDENTITY_BASELINE = "REJECTED_AT_IDENTITY_BASELINE"
    REJECTED_AT_QUOTA = "REJECTED_AT_QUOTA"
    REJECTED_AT_SCHEMA = "REJECTED_AT_SCHEMA"
    REJECTED_AT_SECURITY_PRECHECK = "REJECTED_AT_SECURITY_PRECHECK"
    REJECTED_AT_CORRELATION_BINDING = "REJECTED_AT_CORRELATION_BINDING"
    REJECTED_AT_HANDOFF_COMPLETENESS = "REJECTED_AT_HANDOFF_COMPLETENESS"


# Map E1..E6 stage labels to a rejection status. Used by the handoff layer
# to translate stage-level failure into the canonical Intake vocabulary.
STAGE_TO_REJECTION_STATUS: dict[str, IntakeStatus] = {
    "E1": IntakeStatus.REJECTED_AT_TRANSPORT,
    "E2": IntakeStatus.REJECTED_AT_IDENTITY_BASELINE,
    "E3": IntakeStatus.REJECTED_AT_QUOTA,
    "E4": IntakeStatus.REJECTED_AT_SCHEMA,
    "E5": IntakeStatus.REJECTED_AT_SECURITY_PRECHECK,
    "01.5": IntakeStatus.REJECTED_AT_CORRELATION_BINDING,
    "01.6": IntakeStatus.REJECTED_AT_HANDOFF_COMPLETENESS,
}


REJECTED_STATUSES: frozenset[IntakeStatus] = frozenset(
    s for s in IntakeStatus if s is not IntakeStatus.VALIDATED_FOR_L1
)


__all__ = [
    "REJECTED_STATUSES",
    "STAGE_TO_REJECTION_STATUS",
    "IntakeStatus",
]
