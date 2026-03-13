"""Concrete ApprovalGate — decides whether to approve change packages.

Provides configurable auto-approve thresholds and manual review flagging
for high-risk changes.

All logic is pure and deterministic — no wall-clock reads, no randomness.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    """Result of an approval gate decision."""

    approved: bool
    reason: str
    requires_manual_review: bool = False


class AutoApprovalGate:
    """Approval gate that auto-approves low-risk changes.

    Parameters
    ----------
    max_auto_approve_delta : float
        Maximum delta magnitude for auto-approval.
    auto_approve_surfaces : frozenset[str]
        Set of surface names eligible for auto-approval.
    """

    # guardian: allow-magic-config
    def __init__(
        self, max_auto_approve_delta: float = 0.03, auto_approve_surfaces: frozenset[str] | None = None
    ) -> None:
        self._max_delta = max_auto_approve_delta
        self._auto_surfaces = auto_approve_surfaces or frozenset({"escalation_threshold"})

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        """Decide whether to approve a change package.

        Auto-approves if:
        - The package surface is in the auto-approve set
        - The delta magnitude is within the auto-approve threshold

        Otherwise flags for manual review.
        """
        surface = getattr(pkg, "surface_name", None)
        if surface is None:
            surface = getattr(pkg, "component", "unknown")
        delta = 0.0
        if hasattr(pkg, "new_value") and hasattr(pkg, "old_value"):
            delta = abs(pkg.new_value - pkg.old_value)
        elif hasattr(pkg, "delta"):
            delta = abs(pkg.delta)
        if surface in self._auto_surfaces and delta <= self._max_delta:
            return ApprovalDecision(
                approved=True,
                reason=f"Auto-approved: surface='{surface}' delta={delta:.4f} <= {self._max_delta}",
            )
        return ApprovalDecision(
            approved=False,
            reason=f"Requires manual review: surface='{surface}' delta={delta:.4f} > {self._max_delta}",
            requires_manual_review=True,
        )


class AlwaysApproveGate:
    """Test gate that always approves."""

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        return ApprovalDecision(approved=True, reason="Always-approve gate (test mode)")


class NeverApproveGate:
    """Safety gate that never approves (proposal-only mode)."""

    def decide(self, pkg: Any, rca: Any, snapshot: Any) -> ApprovalDecision:
        return ApprovalDecision(
            approved=False, reason="Never-approve gate (proposal-only mode)", requires_manual_review=True
        )


__all__ = ["ApprovalDecision", "AutoApprovalGate", "AlwaysApproveGate", "NeverApproveGate"]
