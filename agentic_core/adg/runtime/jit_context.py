"""G9 (gap): JIT context sync / freeze boundary runtime.

Models the JIT Elevator Shaft sync moment where state, capability token, tool
budget, and C0 context are pulled just before execution, then the environment
is frozen until the execution slot exits.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FreezeState(str, Enum):
    UNFROZEN = "unfrozen"
    PULLING = "pulling"
    FROZEN = "frozen"
    RELEASED = "released"


@dataclass
class ContextSnapshot:
    """Immutable point-in-time snapshot of context pulled at JIT sync."""

    snapshot_id: str = field(default_factory=lambda: f"snap-{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    run_id: str = ""
    pulled_at: float = field(default_factory=time.time)
    c0_context_hash: str = ""
    capability_token_id: str = ""
    budget_id: str = ""
    state_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    frozen: bool = False

    def freeze(self) -> None:
        self.frozen = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "pulled_at": self.pulled_at,
            "c0_context_hash": self.c0_context_hash,
            "capability_token_id": self.capability_token_id,
            "budget_id": self.budget_id,
            "state_hash": self.state_hash,
            "frozen": self.frozen,
        }


@dataclass
class FreezeBoundary:
    """Runtime freeze boundary tracking entry and exit of a frozen context."""

    boundary_id: str = field(default_factory=lambda: f"frz-{uuid.uuid4().hex[:12]}")
    snapshot: ContextSnapshot | None = None
    freeze_state: FreezeState = FreezeState.UNFROZEN
    frozen_at: float = 0.0
    released_at: float = 0.0
    mutations_during_freeze: int = 0

    @property
    def duration_ms(self) -> float:
        if self.frozen_at and self.released_at:
            return (self.released_at - self.frozen_at) * 1000.0
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "boundary_id": self.boundary_id,
            "freeze_state": self.freeze_state.value,
            "frozen_at": self.frozen_at,
            "released_at": self.released_at,
            "duration_ms": self.duration_ms,
            "mutations_during_freeze": self.mutations_during_freeze,
            "snapshot_id": self.snapshot.snapshot_id if self.snapshot else None,
        }


@dataclass
class JITContextSession:
    """Tracks the full JIT context sync lifecycle for one run."""

    run_id: str = ""
    agent_id: str = ""
    snapshots: list[ContextSnapshot] = field(default_factory=list)
    boundaries: list[FreezeBoundary] = field(default_factory=list)

    @property
    def frozen_count(self) -> int:
        return sum(1 for b in self.boundaries if b.freeze_state in (FreezeState.FROZEN, FreezeState.RELEASED))

    @property
    def active_boundary(self) -> FreezeBoundary | None:
        for b in reversed(self.boundaries):
            if b.freeze_state == FreezeState.FROZEN:
                return b
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "snapshot_count": len(self.snapshots),
            "boundary_count": len(self.boundaries),
            "frozen_count": self.frozen_count,
        }


class JITContextSynchronizer:
    """Runtime synchronizer for JIT context pull + freeze operations."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.session = JITContextSession(run_id=run_id, agent_id=agent_id)

    def pull_context(
        self,
        c0_context_hash: str = "",
        capability_token_id: str = "",
        budget_id: str = "",
        state_hash: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ContextSnapshot:
        snap = ContextSnapshot(
            agent_id=self.session.agent_id,
            run_id=self.session.run_id,
            c0_context_hash=c0_context_hash,
            capability_token_id=capability_token_id,
            budget_id=budget_id,
            state_hash=state_hash,
            metadata=metadata or {},
        )
        self.session.snapshots.append(snap)
        return snap

    def freeze_context(self, snapshot: ContextSnapshot) -> FreezeBoundary:
        snapshot.freeze()
        boundary = FreezeBoundary(snapshot=snapshot, freeze_state=FreezeState.FROZEN)
        boundary.frozen_at = time.time()
        self.session.boundaries.append(boundary)
        return boundary

    def sync_context(
        self,
        c0_context_hash: str = "",
        capability_token_id: str = "",
        budget_id: str = "",
        state_hash: str = "",
    ) -> tuple[ContextSnapshot, FreezeBoundary]:
        """Pull + freeze in one atomic operation (canonical JIT elevator pattern)."""
        snap = self.pull_context(
            c0_context_hash=c0_context_hash,
            capability_token_id=capability_token_id,
            budget_id=budget_id,
            state_hash=state_hash,
        )
        boundary = self.freeze_context(snap)
        return snap, boundary

    def unfreeze_context(self, boundary: FreezeBoundary) -> None:
        boundary.freeze_state = FreezeState.RELEASED
        boundary.released_at = time.time()

    def record_mutation_during_freeze(self, boundary: FreezeBoundary) -> None:
        boundary.mutations_during_freeze += 1

    @property
    def session_summary(self) -> dict[str, Any]:
        return self.session.to_dict()
