from __future__ import annotations

from dataclasses import dataclass
from typing import Any

VersionStore = Any
ApprovalGate = Any


class ActivationBypassViolation(Exception):
    """Raised when an attempt is made to activate meta-learning without dual injection."""


@dataclass(frozen=True)
class MetaLearningActivationDecision:
    """The result of the dual-injection gate's decision."""

    is_active: bool
    proposal_only: bool
    reason_code: str


def decide_activation_mode(
    requested_proposal_only: bool, version_store: VersionStore | None, approval_gate: ApprovalGate | None,
) -> MetaLearningActivationDecision:
    """
    Enforces the dual-injection requirement for meta-learning activation.

    This function enforces Guarantee #22 by ensuring the meta-learning pipeline
    defaults to a safe, proposal-only mode. It can only be fully activated if
    both a version_store (to persist the new model) and an approval_gate (to
    certify it) are explicitly provided. This cannot be overridden by a caller.

    Args:
        requested_proposal_only: The mode requested by the caller.
        version_store: The injected version store dependency.
        approval_gate: The injected approval gate dependency.

    Returns:
        A decision indicating the actual, enforced operational mode.
    """
    if not version_store or not approval_gate:
        return MetaLearningActivationDecision(
            is_active=False, proposal_only=True, reason_code="FALLBACK_PROPOSAL_ONLY_MISSING_DEPENDENCY",
        )
    if requested_proposal_only:
        return MetaLearningActivationDecision(
            is_active=False, proposal_only=True, reason_code="PROPOSAL_ONLY_BY_EXPLICIT_REQUEST",
        )
    return MetaLearningActivationDecision(
        is_active=True, proposal_only=False, reason_code="ACTIVATION_GRANTED_MANDATORY_APPLICATION",
    )
