"""Principal Chain Types — L5 v4 Identity Propagation (G-04).

Defines the identity chain carried through every certified run: the invoking
principal, the currently-executing agent, any parent agents reached via A2A
handoff, and the scope compartment.

Location: `agentic_core/interfaces/` (L_SHARED) — consumed by BOTH L2
(capability_token_v4) and L5 (exit-control, audit emitter). Placing this in
L5_safety/types/ would invert layer gravity (L2 importing from L5). Placing
it in L2_execution/types/ would couple L5 semantics to execution-layer types.
L_SHARED interfaces are the correct home.

Reference: docs/contracts/identity_propagation.md
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
ADR: ADR-049 (§7.3 ratified: full principal_chain from day one, env-seeded)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class InvokingUserKind(str, Enum):
    """Classification of the front-door invoking principal.

    - HUMAN: an authenticated human operator at the front door
    - AUTOMATION: a named automation principal (CI runner, scheduled job)
    - SYSTEM: an internal system principal (healing loop, background task)
    """

    HUMAN = "human"
    AUTOMATION = "automation"
    SYSTEM = "system"


@dataclass(frozen=True)
class HandoffRecord:
    """Single append-only entry in a PrincipalChain's handoff_history.

    Recorded when an agent hands off to another agent (A2A transfer).
    Immutable once added to the chain.
    """

    from_agent_id: str
    to_agent_id: str
    handoff_description: str
    at_semantic_clock: str  # caller passes a stable deterministic tick
    reason: str = ""
    scope_added: tuple[str, ...] = field(default_factory=tuple)
    scope_removed: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.from_agent_id:
            raise ValueError("HandoffRecord: from_agent_id required")
        if not self.to_agent_id:
            raise ValueError("HandoffRecord: to_agent_id required")
        if not self.handoff_description:
            raise ValueError("HandoffRecord: handoff_description required")
        if not self.at_semantic_clock:
            raise ValueError("HandoffRecord: at_semantic_clock required")

    def to_dict(self) -> dict[str, object]:
        return {
            "at_semantic_clock": self.at_semantic_clock,
            "from_agent_id": self.from_agent_id,
            "handoff_description": self.handoff_description,
            "reason": self.reason,
            "scope_added": sorted(self.scope_added),
            "scope_removed": sorted(self.scope_removed),
            "to_agent_id": self.to_agent_id,
        }


@dataclass(frozen=True)
class PrincipalChain:
    """Immutable identity chain threaded through every L5 v4 capability_token.

    Invariants (enforced in __post_init__):
      - invoking_user is non-empty
      - agent_id is non-empty
      - delegation_depth == len(handoff_history)
      - scope_tag is non-empty
      - parent_agent_id is None iff handoff_history is empty
      - handoff_history is a tuple (hashable, immutable)

    Semantics:
      - invoking_user is IMMUTABLE once the chain is created. Downstream
        agents can narrow scopes, append handoff records, and drop scopes,
        but they CANNOT substitute a new invoking_user.
      - delegation_depth caps are enforced by risk_tier_band (see
        risk_tier_bands.md §3): LOW=3, MODERATE=2, HIGH=1.
      - An empty handoff_history means direct invocation; delegation_depth=0.

    SAIF Principle 3 compliance: every action taken under this chain is
    attributable to `invoking_user`. Downstream tools and MCP connectors
    must propagate the chain verbatim (append-only on handoff).
    """

    invoking_user: str
    invoking_user_kind: InvokingUserKind
    auth_method: str
    agent_id: str
    scope_tag: str
    parent_agent_id: str | None = None
    handoff_history: tuple[HandoffRecord, ...] = field(default_factory=tuple)
    scopes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.invoking_user:
            raise ValueError("PrincipalChain: invoking_user required")
        if not isinstance(self.invoking_user_kind, InvokingUserKind):
            raise ValueError(
                f"PrincipalChain: invoking_user_kind must be InvokingUserKind, "
                f"got {type(self.invoking_user_kind).__name__}",
            )
        if not self.agent_id:
            raise ValueError("PrincipalChain: agent_id required")
        if not self.scope_tag:
            raise ValueError("PrincipalChain: scope_tag required")
        if not self.auth_method:
            raise ValueError("PrincipalChain: auth_method required")

        handoffs_len = len(self.handoff_history)
        has_parent = self.parent_agent_id is not None
        if handoffs_len == 0 and has_parent:
            raise ValueError(
                "PrincipalChain: parent_agent_id must be None when handoff_history is empty",
            )
        if handoffs_len > 0 and not has_parent:
            raise ValueError(
                "PrincipalChain: parent_agent_id required when handoff_history is non-empty",
            )

        # Enforce sorted scopes invariant (deterministic serialization)
        if list(self.scopes) != sorted(self.scopes):
            object.__setattr__(self, "scopes", tuple(sorted(self.scopes)))

    @property
    def delegation_depth(self) -> int:
        """Number of A2A handoffs traversed to reach the current agent."""
        return len(self.handoff_history)

    def with_handoff(
        self,
        *,
        to_agent_id: str,
        handoff_description: str,
        at_semantic_clock: str,
        reason: str = "",
        scope_added: tuple[str, ...] = (),
        scope_removed: tuple[str, ...] = (),
    ) -> PrincipalChain:
        """Return a new chain representing an A2A handoff to `to_agent_id`.

        Append-only: original chain is unchanged. delegation_depth on the
        returned chain is +1. scopes on the returned chain = (scopes ∪
        scope_added) \\ scope_removed — widening is allowed only via
        scope_added on the handoff record (which itself must be validated
        against the target agent's registry-declared scope ceiling by the
        L5 Handoff Validation sub-lane).
        """
        record = HandoffRecord(
            from_agent_id=self.agent_id,
            to_agent_id=to_agent_id,
            handoff_description=handoff_description,
            at_semantic_clock=at_semantic_clock,
            reason=reason,
            scope_added=tuple(sorted(scope_added)),
            scope_removed=tuple(sorted(scope_removed)),
        )
        new_scopes = (set(self.scopes) | set(scope_added)) - set(scope_removed)
        return PrincipalChain(
            invoking_user=self.invoking_user,
            invoking_user_kind=self.invoking_user_kind,
            auth_method=self.auth_method,
            agent_id=to_agent_id,
            scope_tag=self.scope_tag,
            parent_agent_id=self.agent_id,
            handoff_history=(*self.handoff_history, record),
            scopes=tuple(sorted(new_scopes)),
        )

    def with_narrowed_scopes(self, drop: tuple[str, ...]) -> PrincipalChain:
        """Return a new chain with `drop` scopes removed. Cannot widen."""
        remaining = tuple(sorted(set(self.scopes) - set(drop)))
        return PrincipalChain(
            invoking_user=self.invoking_user,
            invoking_user_kind=self.invoking_user_kind,
            auth_method=self.auth_method,
            agent_id=self.agent_id,
            scope_tag=self.scope_tag,
            parent_agent_id=self.parent_agent_id,
            handoff_history=self.handoff_history,
            scopes=remaining,
        )

    def to_dict(self) -> dict[str, object]:
        """Deterministic dict representation for canonical JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "auth_method": self.auth_method,
            "delegation_depth": self.delegation_depth,
            "handoff_history": [h.to_dict() for h in self.handoff_history],
            "invoking_user": self.invoking_user,
            "invoking_user_kind": self.invoking_user_kind.value,
            "parent_agent_id": self.parent_agent_id,
            "scope_tag": self.scope_tag,
            "scopes": list(self.scopes),
        }


# Type aliases used by downstream callers for clarity
PermissionLadderRung = Literal["read", "suggest", "mutate", "external"]
RiskTierBand = Literal["LOW", "MODERATE", "HIGH"]
GrantMode = Literal["one_time", "permanent", "sessioned"]


__all__ = [
    "GrantMode",
    "HandoffRecord",
    "InvokingUserKind",
    "PermissionLadderRung",
    "PrincipalChain",
    "RiskTierBand",
]
