"""Capability-token rotation policy (v6 §S4D ledger proof / governance plane).

The L2 ``CapabilityTokenV4Artifact`` carries TTL + ``single_use`` + risk-tier
TTL caps as immutable token fields. This module owns the **policy** layer
on top of those fields: given a live token and observed usage, decide
whether the caller must rotate before the next external action.

Rationale (v6 §1 OBSERVER LAW + §6 UWG SOLE INK PATH):
- Token rotation decisions belong on the L5 policy plane, not embedded in
  the L2 token type, so that policy evolution does not change historical
  ``trace_id`` digests.
- Decisions are deterministic functions of (token, age_seconds,
  usage_count, policy) — no clock reads, no side effects, no I/O. The
  caller is responsible for measuring elapsed semantic time and tracking
  usage; this module only judges.
- The contract returns an explicit reason code so §S4D ledger proof can
  attribute every rotation event.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)


class RotationDecision(str, Enum):
    """Rotation outcome.

    Values are machine-stable strings so ledger entries persist across
    schema revisions.
    """

    KEEP = "KEEP"
    ROTATE_DUE_EXPIRY = "ROTATE_DUE_EXPIRY"
    ROTATE_DUE_USAGE = "ROTATE_DUE_USAGE"
    ROTATE_DUE_THRESHOLD = "ROTATE_DUE_THRESHOLD"


@dataclass(frozen=True)
class RotationPolicy:
    """Site-tunable rotation thresholds.

    Defaults: rotate proactively once 80% of TTL has elapsed. Sites with
    short-lived tokens (LOW band, 3600 s cap) often relax this to 0.9;
    sites with HIGH-band tokens often tighten it to 0.5 because the
    blast-radius cost of an over-aged HIGH-band token dominates the cost
    of issuing a fresh one.
    """

    rotation_threshold_pct: float = 0.8

    def __post_init__(self) -> None:
        if not 0.0 < self.rotation_threshold_pct <= 1.0:
            raise ValueError(
                "rotation_threshold_pct must be in (0, 1]; "
                "use evaluate_rotation directly with usage_count to skip "
                "the threshold path entirely."
            )


def evaluate_rotation(
    token: CapabilityTokenV4Artifact,
    *,
    age_seconds: int,
    usage_count: int,
    policy: RotationPolicy | None = None,
) -> RotationDecision:
    """Decide whether ``token`` must rotate.

    Decision precedence (most-decisive first; matches the order an
    auditor expects to read in a §S4D ledger row):

    1. ``ROTATE_DUE_EXPIRY``  — ``age_seconds >= token.ttl_seconds``.
    2. ``ROTATE_DUE_USAGE``   — ``token.single_use and usage_count >= 1``.
    3. ``ROTATE_DUE_THRESHOLD`` — ``age_seconds`` has crossed
       ``policy.rotation_threshold_pct`` of the TTL.
    4. ``KEEP`` otherwise.

    Args:
        token: The active capability token under evaluation.
        age_seconds: Elapsed time since token issue, in seconds. Must be
            non-negative; callers are responsible for clamping clock
            skew.
        usage_count: Number of times this token has been used to authorize
            an external action. Must be non-negative.
        policy: Site rotation policy. Defaults to ``RotationPolicy()``.

    Returns:
        A ``RotationDecision``.

    Raises:
        ValueError: if inputs are negative or otherwise non-physical.
    """
    if age_seconds < 0:
        raise ValueError(f"age_seconds must be >= 0, got {age_seconds}")
    if usage_count < 0:
        raise ValueError(f"usage_count must be >= 0, got {usage_count}")

    pol = policy or RotationPolicy()

    # 1. Expiry — strictly hard.
    if age_seconds >= token.ttl_seconds:
        return RotationDecision.ROTATE_DUE_EXPIRY

    # 2. Single-use exhaustion — strictly hard.
    if token.single_use and usage_count >= 1:
        return RotationDecision.ROTATE_DUE_USAGE

    # 3. Proactive threshold.
    threshold = int(token.ttl_seconds * pol.rotation_threshold_pct)
    if age_seconds >= threshold:
        return RotationDecision.ROTATE_DUE_THRESHOLD

    return RotationDecision.KEEP


def must_rotate(
    token: CapabilityTokenV4Artifact,
    *,
    age_seconds: int,
    usage_count: int,
    policy: RotationPolicy | None = None,
) -> bool:
    """Convenience: True iff ``evaluate_rotation`` returns any ROTATE_*."""
    return evaluate_rotation(
        token,
        age_seconds=age_seconds,
        usage_count=usage_count,
        policy=policy,
    ) is not RotationDecision.KEEP


__all__ = [
    "RotationDecision",
    "RotationPolicy",
    "evaluate_rotation",
    "must_rotate",
]
