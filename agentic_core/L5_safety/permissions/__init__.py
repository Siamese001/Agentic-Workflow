"""
G06 — Graduated Permission Ladder.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W5/P8.06 — `.windsurf/plans/w4-p8-guardrail-family-e93f8a.md`

# guardian: allow-empty-skeleton -- ADR-070 introduces G06 as a NEW concern
# with no pre-existing modules. This file establishes the contract surface.

Replaces the binary read/write permission model with a 4-rung ladder:

  read    — observe state only, no side effects
  suggest — produce a proposal/draft for human review (no commit)
  mutate  — write to state via UWG.commit() with rollback
  execute — invoke external action (subprocess, network, capability gateway)

Each rung requires explicit authorization at the previous rung. An agent
holding `mutate` automatically holds `suggest` and `read`; it does NOT
automatically hold `execute`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Protocol


class PermissionRung(IntEnum):
    """4-rung graduated permission ladder. Higher rung implies all lower rungs."""

    READ = 1
    SUGGEST = 2
    MUTATE = 3
    EXECUTE = 4


@dataclass(frozen=True)
class PermissionGrant:
    """Immutable record of a permission grant to an agent for a target."""

    agent_id: str
    target_resource: str  # e.g. "uwg:state:user_profile" or "exec:shell:safe-list"
    rung: PermissionRung
    granted_by: str  # principal or rule that issued the grant
    expires_at_iso: str  # ISO-8601 timestamp


@dataclass(frozen=True)
class PermissionVerdict:
    """Result of an admission check at a specific rung."""

    allowed: bool
    held_rung: PermissionRung | None  # None = no grant at all
    requested_rung: PermissionRung
    reason: str


class PermissionLadder(Protocol):
    """Protocol that any execution-side gate must call before acting."""

    def check(self, agent_id: str, target: str, requested: PermissionRung) -> PermissionVerdict:
        """Return verdict for the proposed action. Pure function."""
        ...


def default_ladder() -> PermissionLadder:
    """Production ladder. Implementation is W4 P8 W5 work."""
    raise NotImplementedError(
        "G06 graduated permission ladder implementation pending — see ADR-070 + "
        ".windsurf/plans/w4-p8-guardrail-family-e93f8a.md W5 P8.06"
    )


__all__ = ["PermissionRung", "PermissionGrant", "PermissionVerdict", "PermissionLadder", "default_ladder"]
