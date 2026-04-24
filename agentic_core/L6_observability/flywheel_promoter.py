"""Flywheel trace→dataset promoter (ADR-040).

Reads an ``EvalEvent`` dict and returns a staged TriageRecord when the event
matches one or more promotion signals. Candidate events are written to
``data/eval/triage/<event_id>.json`` awaiting human curation.

Observer posture only — never mutates runtime state; never writes directly
to ``data/eval/golden/`` (that step requires human review per §6D).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

_TRIAGE_ROOT = Path("data/eval/triage")


@dataclass(frozen=True)
class TriageRecord:
    """Staged record awaiting human curation into ``data/eval/golden/``."""

    event_id: str
    target_dataset: str
    candidate_reasons: tuple[str, ...]
    payload: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "target_dataset": self.target_dataset,
            "candidate_reasons": list(self.candidate_reasons),
            "payload": dict(self.payload),
        }


def _is_escalation(event: Mapping[str, Any]) -> bool:
    exit_decision = event.get("exit_decision") or {}
    return exit_decision.get("disposition") == "escalate_hitl"


def _is_deny(event: Mapping[str, Any]) -> bool:
    exit_decision = event.get("exit_decision") or {}
    return exit_decision.get("disposition") == "deny_reroute"


def _is_quality_fail(event: Mapping[str, Any]) -> bool:
    exit_decision = event.get("exit_decision") or {}
    return (exit_decision.get("quality") or {}).get("verdict") == "fail"


def _is_safety_violation(event: Mapping[str, Any]) -> bool:
    exit_decision = event.get("exit_decision") or {}
    safety = exit_decision.get("safety") or {}
    return bool(safety.get("policy_violation"))


def _is_non_determinism_hotspot(event: Mapping[str, Any]) -> bool:
    replication = event.get("replication") or {}
    if not replication.get("is_replicate"):
        return False
    pass_rate = replication.get("pass_rate_0_1")
    return isinstance(pass_rate, (int, float)) and pass_rate < 0.9


def _is_trajectory_regression(event: Mapping[str, Any]) -> bool:
    exit_decision = event.get("exit_decision") or {}
    trajectory = exit_decision.get("trajectory") or {}
    exact = trajectory.get("exact_match")
    return exact == 0


def _route_dataset(reasons: tuple[str, ...]) -> str:
    if "safety_violation" in reasons:
        return "data/eval/golden/safety"
    if "trajectory_regression" in reasons:
        return "data/eval/golden/trajectory"
    if "quality_fail" in reasons or "escalation" in reasons:
        return "data/eval/golden/quality"
    return "data/eval/golden/triage"


def analyze(event: Mapping[str, Any]) -> TriageRecord | None:
    """Return a TriageRecord if ``event`` is a promotion candidate, else None."""
    reasons: list[str] = []
    if _is_escalation(event):
        reasons.append("escalation")
    if _is_deny(event):
        reasons.append("deny_reroute")
    if _is_quality_fail(event):
        reasons.append("quality_fail")
    if _is_safety_violation(event):
        reasons.append("safety_violation")
    if _is_non_determinism_hotspot(event):
        reasons.append("non_determinism_hotspot")
    if _is_trajectory_regression(event):
        reasons.append("trajectory_regression")

    # Operator-tagged manual flag.
    flywheel = event.get("flywheel") or {}
    if flywheel.get("promote_candidate"):
        reasons.append(flywheel.get("candidate_reason") or "operator_tagged")

    if not reasons:
        return None

    event_id = event.get("event_id") or event.get("trace_id") or "unknown"
    target = _route_dataset(tuple(reasons))
    return TriageRecord(
        event_id=str(event_id),
        target_dataset=target,
        candidate_reasons=tuple(reasons),
        payload={
            "request_id": event.get("request_id"),
            "trace_id": event.get("trace_id"),
            "disposition": (event.get("exit_decision") or {}).get("disposition"),
            "reason_code": (event.get("exit_decision") or {}).get("reason_code"),
            "cost": event.get("cost"),
            "replication": event.get("replication"),
        },
    )


def stage(record: TriageRecord, *, triage_root: Path | None = None) -> Path:
    """Write ``record`` to the triage staging directory and return the path."""
    root = triage_root or _TRIAGE_ROOT
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{record.event_id}.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(record.as_dict(), handle, ensure_ascii=False, indent=2)
    return path


def promote_candidate(
    event: Mapping[str, Any],
    *,
    triage_root: Path | None = None,
    stage_to_disk: bool = False,
) -> TriageRecord | None:
    """End-to-end: analyze + optionally stage to triage directory."""
    record = analyze(event)
    if record is None:
        return None
    if stage_to_disk:
        stage(record, triage_root=triage_root)
    return record


__all__ = [
    "TriageRecord",
    "analyze",
    "promote_candidate",
    "stage",
]
