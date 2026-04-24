"""
Runtime behavior monitor — W5-P5.2 (gap plan b7c4e2 G13).

Flags "workflow starts behaving in ways that appear unsafe, wasteful, or
misaligned with the task" (codebridge 2026 guardrails doctrine) locally
at L2 before L6 aggregates it post-run. Detectors:

1. **tool-sequence anomaly** — the same tool invoked >N times in a row.
2. **retry storm** — retry_count per step exceeds a ceiling.
3. **cost drift** — cumulative tokens or wall-clock exceed a budget.

All detectors are pure functions over an append-only
``WorkflowTrace`` — no side effects, no exceptions, just findings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

__all__ = [
    "TraceEvent",
    "WorkflowTrace",
    "BehaviorFinding",
    "BehaviorMonitor",
]


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """Minimal per-step trace event."""

    step_id: str
    tool_name: str
    retry_count: int = 0
    tokens: int = 0
    wall_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowTrace:
    events: list[TraceEvent] = field(default_factory=list)

    def record(self, event: TraceEvent) -> None:
        self.events.append(event)

    def extend(self, events: Iterable[TraceEvent]) -> None:
        self.events.extend(events)


@dataclass(frozen=True, slots=True)
class BehaviorFinding:
    kind: str  # "tool_sequence_anomaly" | "retry_storm" | "cost_drift"
    severity: str  # "info" | "warning" | "critical"
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BehaviorMonitor:
    """Thresholds tunable per deployment."""

    same_tool_streak_warn: int = 3
    same_tool_streak_critical: int = 6
    retry_warn: int = 2
    retry_critical: int = 5
    token_budget_warn: int = 50_000
    token_budget_critical: int = 200_000
    wall_ms_budget_warn: float = 30_000.0
    wall_ms_budget_critical: float = 120_000.0

    def evaluate(self, trace: WorkflowTrace) -> list[BehaviorFinding]:
        findings: list[BehaviorFinding] = []
        findings.extend(self._tool_sequence(trace))
        findings.extend(self._retry_storm(trace))
        findings.extend(self._cost_drift(trace))
        return findings

    def _tool_sequence(self, trace: WorkflowTrace) -> list[BehaviorFinding]:
        out: list[BehaviorFinding] = []
        if not trace.events:
            return out
        current = trace.events[0].tool_name
        streak = 1
        worst_streak = 1
        worst_tool = current
        for ev in trace.events[1:]:
            if ev.tool_name == current:
                streak += 1
                if streak > worst_streak:
                    worst_streak = streak
                    worst_tool = current
            else:
                current = ev.tool_name
                streak = 1
        if worst_streak >= self.same_tool_streak_critical:
            out.append(
                BehaviorFinding(
                    kind="tool_sequence_anomaly",
                    severity="critical",
                    reason=f"tool {worst_tool!r} invoked {worst_streak} times in a row",
                    evidence={"tool": worst_tool, "streak": worst_streak},
                )
            )
        elif worst_streak >= self.same_tool_streak_warn:
            out.append(
                BehaviorFinding(
                    kind="tool_sequence_anomaly",
                    severity="warning",
                    reason=f"tool {worst_tool!r} invoked {worst_streak} times in a row",
                    evidence={"tool": worst_tool, "streak": worst_streak},
                )
            )
        return out

    def _retry_storm(self, trace: WorkflowTrace) -> list[BehaviorFinding]:
        out: list[BehaviorFinding] = []
        for ev in trace.events:
            if ev.retry_count >= self.retry_critical:
                out.append(
                    BehaviorFinding(
                        kind="retry_storm",
                        severity="critical",
                        reason=(
                            f"step {ev.step_id!r} tool {ev.tool_name!r} "
                            f"retry_count={ev.retry_count}"
                        ),
                        evidence={"step_id": ev.step_id, "retries": ev.retry_count},
                    )
                )
            elif ev.retry_count >= self.retry_warn:
                out.append(
                    BehaviorFinding(
                        kind="retry_storm",
                        severity="warning",
                        reason=(
                            f"step {ev.step_id!r} tool {ev.tool_name!r} "
                            f"retry_count={ev.retry_count}"
                        ),
                        evidence={"step_id": ev.step_id, "retries": ev.retry_count},
                    )
                )
        return out

    def _cost_drift(self, trace: WorkflowTrace) -> list[BehaviorFinding]:
        out: list[BehaviorFinding] = []
        total_tokens = sum(ev.tokens for ev in trace.events)
        total_wall = sum(ev.wall_ms for ev in trace.events)
        if total_tokens >= self.token_budget_critical:
            out.append(
                BehaviorFinding(
                    kind="cost_drift",
                    severity="critical",
                    reason=f"total tokens {total_tokens} >= critical budget {self.token_budget_critical}",
                    evidence={"total_tokens": total_tokens},
                )
            )
        elif total_tokens >= self.token_budget_warn:
            out.append(
                BehaviorFinding(
                    kind="cost_drift",
                    severity="warning",
                    reason=f"total tokens {total_tokens} >= warn budget {self.token_budget_warn}",
                    evidence={"total_tokens": total_tokens},
                )
            )
        if total_wall >= self.wall_ms_budget_critical:
            out.append(
                BehaviorFinding(
                    kind="cost_drift",
                    severity="critical",
                    reason=f"total wall_ms {total_wall:.0f} >= critical budget {self.wall_ms_budget_critical:.0f}",
                    evidence={"total_wall_ms": total_wall},
                )
            )
        elif total_wall >= self.wall_ms_budget_warn:
            out.append(
                BehaviorFinding(
                    kind="cost_drift",
                    severity="warning",
                    reason=f"total wall_ms {total_wall:.0f} >= warn budget {self.wall_ms_budget_warn:.0f}",
                    evidence={"total_wall_ms": total_wall},
                )
            )
        return out
