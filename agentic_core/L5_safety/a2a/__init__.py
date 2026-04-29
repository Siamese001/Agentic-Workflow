"""
G05 — A2A Handoff Validation Sub-lane.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W5/P8.05 — `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`

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


def default_validator() -> A2AHandoffValidator:
    """Return the production validator. Implementation is W4 P8 W5 work."""
    raise NotImplementedError(
        "G05 A2A handoff validator implementation pending — see ADR-070 + "
        ".windsurf/plans/w4-p8-guardrail-family-e93f8a.md W5 P8.05"
    )


__all__ = ["HandoffContext", "HandoffVerdict", "A2AHandoffValidator", "default_validator"]
