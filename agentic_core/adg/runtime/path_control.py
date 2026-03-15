"""G15 (gap): Execution-path control runtime.

Models the dynamic path topology with Path A/B/C/D, stall forcing to Path D,
safety re-entry, and immediate vigilance reroute from L6 to L0/L1.

Data structures only — no side-effects on import.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ExecutionPath(str, Enum):
    PATH_A = "path_a"  # Normal execution
    PATH_B = "path_b"  # Degraded / limited capability
    PATH_C = "path_c"  # Safety-supervised execution
    PATH_D = "path_d"  # Stall / human-review required
    SAFETY_REENTRY = "safety_reentry"  # Re-entering L5 safety gate
    VIGILANCE_REROUTE = "vigilance_reroute"  # L6→L0/L1 emergency reroute


class PathTransitionReason(str, Enum):
    NORMAL_ROUTING = "normal_routing"
    LOW_CONFIDENCE = "low_confidence"
    SAFETY_TRIGGER = "safety_trigger"
    STALL_FORCED = "stall_forced"
    L6_VIGILANCE = "l6_vigilance"
    HUMAN_OVERRIDE = "human_override"
    BUDGET_EXHAUSTED = "budget_exhausted"
    BOUNDARY_REJECTED = "boundary_rejected"


@dataclass
class PathTransition:
    """A single path transition event."""

    transition_id: str = field(default_factory=lambda: f"pt-{uuid.uuid4().hex[:8]}")
    run_id: str = ""
    agent_id: str = ""
    from_path: ExecutionPath = ExecutionPath.PATH_A
    to_path: ExecutionPath = ExecutionPath.PATH_A
    reason: PathTransitionReason = PathTransitionReason.NORMAL_ROUTING
    ts: float = field(default_factory=time.time)
    detail: str = ""
    triggered_by: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "from_path": self.from_path.value,
            "to_path": self.to_path.value,
            "reason": self.reason.value,
            "ts": self.ts,
            "detail": self.detail,
            "triggered_by": self.triggered_by,
        }


@dataclass
class PathControlReport:
    """Aggregated report of path control transitions for one session."""

    agent_id: str = ""
    run_id: str = ""
    transitions: list[PathTransition] = field(default_factory=list)
    current_path: ExecutionPath = ExecutionPath.PATH_A

    @property
    def stall_count(self) -> int:
        return sum(1 for t in self.transitions if t.to_path == ExecutionPath.PATH_D)

    @property
    def vigilance_reroute_count(self) -> int:
        return sum(1 for t in self.transitions if t.to_path == ExecutionPath.VIGILANCE_REROUTE)

    @property
    def safety_reentry_count(self) -> int:
        return sum(1 for t in self.transitions if t.to_path == ExecutionPath.SAFETY_REENTRY)

    @property
    def total_transitions(self) -> int:
        return len(self.transitions)

    def path_visit_counts(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PathControlReport.path_visit_counts")

        counts: dict[str, int] = {}
        for t in self.transitions:
            key = t.to_path.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "current_path": self.current_path.value,
            "total_transitions": self.total_transitions,
            "stall_count": self.stall_count,
            "vigilance_reroute_count": self.vigilance_reroute_count,
            "safety_reentry_count": self.safety_reentry_count,
            "path_visit_counts": self.path_visit_counts(),
        }

    @property
    def summary(self) -> str:
        return (
            f"PathControl [{self.agent_id}] — "
            f"current={self.current_path.value}, "
            f"{self.total_transitions} transitions, "
            f"{self.stall_count} stalls, "
            f"{self.vigilance_reroute_count} vigilance reroutes"
        )


class ExecutionPathController:
    """Runtime controller for execution path topology."""

    def __init__(self, agent_id: str, run_id: str) -> None:
        self.report = PathControlReport(agent_id=agent_id, run_id=run_id)

    def _transition(
        self,
        to_path: ExecutionPath,
        reason: PathTransitionReason,
        detail: str = "",
        triggered_by: str = "",
    ) -> PathTransition:
        t = PathTransition(
            run_id=self.report.run_id,
            agent_id=self.report.agent_id,
            from_path=self.report.current_path,
            to_path=to_path,
            reason=reason,
            detail=detail,
            triggered_by=triggered_by,
        )
        self.report.transitions.append(t)
        self.report.current_path = to_path
        return t

    def route_path(
        self,
        path: ExecutionPath = ExecutionPath.PATH_A,
        detail: str = "",
    ) -> PathTransition:
        return self._transition(path, PathTransitionReason.NORMAL_ROUTING, detail)

    def force_stall(self, reason: str = "", triggered_by: str = "") -> PathTransition:
        return self._transition(
            ExecutionPath.PATH_D,
            PathTransitionReason.STALL_FORCED,
            detail=reason,
            triggered_by=triggered_by,
        )

    def force_path_d(self, reason: str = "") -> PathTransition:
        return self.force_stall(reason=reason)

    def reenter_safety(self, reason: str = "", triggered_by: str = "") -> PathTransition:
        return self._transition(
            ExecutionPath.SAFETY_REENTRY,
            PathTransitionReason.SAFETY_TRIGGER,
            detail=reason,
            triggered_by=triggered_by,
        )

    def vigilance_reroute(self, triggered_by: str = "L6", detail: str = "") -> PathTransition:
        return self._transition(
            ExecutionPath.VIGILANCE_REROUTE,
            PathTransitionReason.L6_VIGILANCE,
            detail=detail,
            triggered_by=triggered_by,
        )

    def reroute_to_l0(self, detail: str = "") -> PathTransition:
        return self.vigilance_reroute(triggered_by="L6→L0", detail=detail)

    def reroute_to_l1(self, detail: str = "") -> PathTransition:
        return self.vigilance_reroute(triggered_by="L6→L1", detail=detail)

    @property
    def current_path(self) -> ExecutionPath:
        return self.report.current_path
