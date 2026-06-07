"""
G06 — Graduated Permission Ladder.

Per ADR-070 L5 Guardrail Family Catalog (2026-04-29).
Phase: W4 P8 W5/P8.06 — `docs/archive/windsurf/legacy-tree/plans/w4-p8-guardrail-family-e93f8a.md`

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


def _now_iso() -> str:
    """Wall-clock UTC ISO-8601 (Z-suffixed)."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class InMemoryPermissionLadder:
    """Production-grade in-memory ladder.

    A grant is keyed by (agent_id, target_resource). Granting a higher rung
    overwrites a lower rung for the same key. Higher rungs implicitly
    confer all lower rungs (READ < SUGGEST < MUTATE < EXECUTE).

    Expiry is enforced by string-comparing ``expires_at_iso`` against
    the current ISO timestamp — both are UTC Z-suffixed so lexicographic
    order matches chronological order. Expired grants behave as if absent.

    Thread-safe: a single lock guards all reads/writes. The grant set is
    expected to be small (≤10⁴ entries) so a single lock is fine; switch
    to per-shard locks if scale demands.
    """

    def __init__(self) -> None:
        import threading
        self._lock = threading.Lock()
        self._grants: dict[tuple[str, str], PermissionGrant] = {}

    def grant(self, grant: PermissionGrant) -> None:
        """Record a grant; overwrites any prior grant for the same (agent, target)."""
        key = (grant.agent_id, grant.target_resource)
        with self._lock:
            self._grants[key] = grant

    def revoke(self, agent_id: str, target_resource: str) -> bool:
        """Remove a grant. Returns True if a grant was removed."""
        with self._lock:
            return self._grants.pop((agent_id, target_resource), None) is not None

    def check(
        self,
        agent_id: str,
        target: str,
        requested: PermissionRung,
    ) -> PermissionVerdict:
        with self._lock:
            grant = self._grants.get((agent_id, target))

        if grant is None:
            return PermissionVerdict(
                allowed=False, held_rung=None, requested_rung=requested,
                reason="no grant exists for (agent, target)",
            )
        if grant.expires_at_iso <= _now_iso():
            return PermissionVerdict(
                allowed=False, held_rung=grant.rung, requested_rung=requested,
                reason=f"grant expired at {grant.expires_at_iso}",
            )
        if grant.rung >= requested:
            return PermissionVerdict(
                allowed=True, held_rung=grant.rung, requested_rung=requested,
                reason=f"held {grant.rung.name} ≥ requested {requested.name}",
            )
        return PermissionVerdict(
            allowed=False, held_rung=grant.rung, requested_rung=requested,
            reason=f"held {grant.rung.name} < requested {requested.name}",
        )


def default_ladder() -> PermissionLadder:
    """Return a fresh in-memory ladder. Production wires this to a durable backend later."""
    return InMemoryPermissionLadder()


__all__ = [
    "PermissionRung",
    "PermissionGrant",
    "PermissionVerdict",
    "PermissionLadder",
    "InMemoryPermissionLadder",
    "default_ladder",
]
