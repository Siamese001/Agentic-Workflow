"""
Trace grading hooks — W5-P5.4 (gap plan b7c4e2 G15).

Emits per-step grading slots attached to an execution trace so L6
shadow-eval §6B can consume them without re-deriving. Matches the OpenAI
agent-builder "trace grading" pattern: grading per decision / tool call /
reasoning step.

L2 doesn't *grade* — it only produces structured slots for L6 to fill.
L2 may attach *preliminary* signals (latency, retries, whether a tripwire
fired) that L6 can use as features.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "GradingTarget",
    "GradingSlot",
    "GradingBundle",
]


class GradingTarget:
    """Enum-like string constants so consumers can filter by stage."""

    DECISION = "decision"
    TOOL_CALL = "tool_call"
    REASONING_STEP = "reasoning_step"
    E2_GATE = "e2_gate"
    E3_EXECUTE = "e3_execute"
    E4_HEAL = "e4_heal"
    E5_SEAL = "e5_seal"


@dataclass(frozen=True, slots=True)
class GradingSlot:
    """One gradable artifact to be consumed by L6 §6B."""

    slot_id: str
    target: str  # one of GradingTarget
    trace_id: str
    created_at: float = field(default_factory=time.time)
    preliminary_signals: dict[str, Any] = field(default_factory=dict)
    grade: float | None = None  # None = ungraded; L6 fills this in
    rationale: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_grade(self, grade: float, rationale: str = "") -> "GradingSlot":
        """Return a new slot with a grade attached (slots are frozen)."""
        return GradingSlot(
            slot_id=self.slot_id,
            target=self.target,
            trace_id=self.trace_id,
            created_at=self.created_at,
            preliminary_signals=dict(self.preliminary_signals),
            grade=grade,
            rationale=rationale,
            metadata=dict(self.metadata),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "slot_id": self.slot_id,
            "target": self.target,
            "trace_id": self.trace_id,
            "created_at": self.created_at,
            "preliminary_signals": dict(self.preliminary_signals),
            "grade": self.grade,
            "rationale": self.rationale,
            "metadata": dict(self.metadata),
        }


@dataclass(slots=True)
class GradingBundle:
    """Append-only collection of grading slots for a single run."""

    trace_id: str
    slots: list[GradingSlot] = field(default_factory=list)

    def add(
        self,
        *,
        slot_id: str,
        target: str,
        preliminary_signals: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> GradingSlot:
        slot = GradingSlot(
            slot_id=slot_id,
            target=target,
            trace_id=self.trace_id,
            preliminary_signals=dict(preliminary_signals or {}),
            metadata=dict(metadata or {}),
        )
        self.slots.append(slot)
        return slot

    def by_target(self, target: str) -> list[GradingSlot]:
        return [s for s in self.slots if s.target == target]

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "slots": [s.to_dict() for s in self.slots],
        }
