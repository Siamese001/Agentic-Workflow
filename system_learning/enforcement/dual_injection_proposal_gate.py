from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Placeholders for complex external types
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
    requested_proposal_only: bool,
    version_store: VersionStore | None,
    approval_gate: ApprovalGate | None,
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
    # 1. The sovereign rule: If either dependency is missing, we are in proposal-only mode.
    #    This overrides any caller request.
    if not version_store or not approval_gate:
        return MetaLearningActivationDecision(
            is_active=False,
            proposal_only=True,
            reason_code="FORCED_PROPOSAL_ONLY_MISSING_DEPENDENCY",
        )

    # 2. If dual injection is satisfied, respect the caller's request.
    #    However, a real implementation would also require the approval_gate
    #    to make a positive decision, e.g., `approval_gate.decide() == "APPROVE"`.
    if requested_proposal_only:
        return MetaLearningActivationDecision(
            is_active=False,
            proposal_only=True,
            reason_code="PROPOSAL_ONLY_BY_REQUEST",
        )
    else:
        # Activation requires a successful decision from the approval gate.
        # Placeholder for the actual decision logic.
        # if approval_gate.decide() != "APPROVE":
        #     return MetaLearningActivationDecision(
        #         is_active=False,
        #         proposal_only=True,
        #         reason_code="ACTIVATION_DENIED_BY_APPROVAL_GATE",
        #     )

        return MetaLearningActivationDecision(
            is_active=True,
            proposal_only=False,
            reason_code="ACTIVATION_GRANTED_DUAL_INJECTION_SATISFIED",
        )
