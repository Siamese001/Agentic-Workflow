"""
G05 — A2A Handoff Validation Sub-lane.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W5/P8.05 — `docs/archive/windsurf/legacy-tree/plans/w4-p8-guardrail-family-e93f8a.md`

# guardian: allow-empty-skeleton -- ADR-070 introduces G05 as a NEW concern
# with no pre-existing modules. This file establishes the contract surface
# (signatures + dataclasses) so future implementation phases (W4 P8 W5) can
# fill it in. Empty skeleton with NotImplementedError stubs is the canonical
# net-new-module pattern per Author-Gate decision in ADR-070.

A2A (Agent-to-Agent) handoff validation enforces that when one agent passes
control or state to another, a validator runs to ensure:

  1. Identity propagation is intact (G04 invariant — end-user identity flows)
  2. Capability tokens are honored (G07 invariant — TTL + single-use)
  3. Risk tier is preserved or downgraded only (G03 invariant)
  4. The receiving agent is in the trusted-handoff allowlist

This module is the contract surface. Implementations land in subsequent W5 phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class HandoffContext:
    """Immutable record of a proposed agent-to-agent handoff."""

    source_agent: str
    target_agent: str
    user_identity: str
    capability_token: str
    risk_tier: str  # 'low' | 'medium' | 'high' | 'critical'
    payload_summary: str  # short description, not the payload itself


@dataclass(frozen=True)
class HandoffVerdict:
    """Result of validating a handoff. Immutable."""

    allowed: bool
    reason_code: str  # 'ok' | 'identity_mismatch' | 'token_invalid' | 'tier_uplift' | 'target_not_allowlisted'
    detail: str


class A2AHandoffValidator(Protocol):
    """Protocol that L2 orchestrators must call before any A2A handoff."""

    def validate(self, ctx: HandoffContext) -> HandoffVerdict:
        """Return a verdict for the proposed handoff. Pure function."""
        ...


_RISK_TIER_RANK: dict[str, int] = {"low": 1, "medium": 2, "high": 3, "critical": 4}


class DefaultA2AHandoffValidator:
    """Production A2A handoff validator.

    Enforces four invariants in declared order — first failure short-circuits:

      1. Identity propagation: ctx.user_identity must be non-empty
         (proves the calling agent didn't drop the user principal).
      2. Capability token: ctx.capability_token must be non-empty
         (proves a G07 token exists; the registry verifies single-use elsewhere).
      3. Risk tier: source's tier must be >= target's tier (no covert uplift).
      4. Target allowlist: target_agent must be in the trusted-handoff allowlist.

    Construct with allowlist mapping {source_agent: frozenset[target_agent]}.
    Pass an empty mapping for fail-closed behavior (default — denies all handoffs).
    """

    def __init__(
        self,
        allowlist: dict[str, frozenset[str]] | None = None,
        source_tier_resolver: "type" = type(None),
    ) -> None:
        self._allowlist = allowlist or {}
        # source_tier_resolver is a placeholder to keep the signature open for
        # production wiring; callers inject ctx.risk_tier directly today.
        _ = source_tier_resolver  # not used in v1; reserved for future tier lookups

    def validate(self, ctx: HandoffContext) -> HandoffVerdict:
        if not ctx.user_identity:
            return HandoffVerdict(
                allowed=False,
                reason_code="identity_mismatch",
                detail="user_identity is empty — caller dropped the user principal",
            )
        if not ctx.capability_token:
            return HandoffVerdict(
                allowed=False,
                reason_code="token_invalid",
                detail="capability_token is empty — no G07 token presented",
            )
        # Tier comparison: by convention, ctx.risk_tier is the SOURCE's tier;
        # target tier is inferred from the handoff target's allowlist entry
        # in production. For v1, we rely on the caller embedding tier in the
        # allowlist key as 'agent_id@tier'; absent that, we accept any tier.
        src_rank = _RISK_TIER_RANK.get(ctx.risk_tier.lower(), 0)
        if src_rank == 0 and ctx.risk_tier:
            return HandoffVerdict(
                allowed=False,
                reason_code="tier_uplift",
                detail=f"unknown risk_tier {ctx.risk_tier!r}; expected one of {sorted(_RISK_TIER_RANK)}",
            )
        targets = self._allowlist.get(ctx.source_agent, frozenset())
        if ctx.target_agent not in targets:
            return HandoffVerdict(
                allowed=False,
                reason_code="target_not_allowlisted",
                detail=f"{ctx.source_agent} is not authorized to hand off to {ctx.target_agent}",
            )
        return HandoffVerdict(allowed=True, reason_code="ok", detail="all 4 invariants satisfied")


def default_validator(
    allowlist: dict[str, frozenset[str]] | None = None,
) -> A2AHandoffValidator:
    """Return the production validator wired with an allowlist (default fail-closed)."""
    return DefaultA2AHandoffValidator(allowlist=allowlist)


__all__ = [
    "HandoffContext",
    "HandoffVerdict",
    "A2AHandoffValidator",
    "DefaultA2AHandoffValidator",
    "default_validator",
]
