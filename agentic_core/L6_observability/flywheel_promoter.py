"""Flywheel trace→dataset promoter (ADR-040).

Reads an ``EvalEvent`` dict and returns a staged TriageRecord when the event
matches one or more promotion signals. Candidate events are written to
``data/eval/triage/<event_id>.json`` awaiting human curation.

Observer posture only — never mutates runtime state; never writes directly
to ``data/eval/golden/`` (that step requires human review per §6D).

W8 live wire-up (2026-04-26): ``promote_candidate`` accepts an optional
``RuntimeSpanEmitter`` from
``agentic_core.runtime.prove_requirements.otel_emitter``. When supplied,
the call is wrapped in an ``l6.promotion_attempt`` span carrying
reason_codes from the candidate-detection signals. Default behavior is
unchanged when no emitter is passed (every existing call site continues
to work). See `.windsurf/plans/runtime-proof-system-*.md` Author-Gate
``architecture_choice`` decision (W8) for context.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Optional

if TYPE_CHECKING:
    from agentic_core.runtime.prove_requirements.otel_emitter import (
        RuntimeSpanEmitter,
    )

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
    emitter: Optional["RuntimeSpanEmitter"] = None,
) -> TriageRecord | None:
    """End-to-end: analyze + optionally stage to triage directory.

    Args:
        event: EvalEvent dict (see ADR-040).
        triage_root: Override default ``data/eval/triage/`` location.
        stage_to_disk: If True, write the TriageRecord to disk.
        emitter: Optional ``RuntimeSpanEmitter`` from the proof system.
            When supplied, the analyze+stage operation is recorded as an
            ``l6.promotion_attempt`` OTEL span. Default ``None`` keeps the
            historical behavior (silent observer posture).

    Returns:
        A ``TriageRecord`` when the event qualifies, else ``None``.
    """
    if emitter is None:
        record = analyze(event)
        if record is None:
            return None
        if stage_to_disk:
            stage(record, triage_root=triage_root)
        return record

    # W8 live wire-up: emit l6.promotion_attempt with reason_codes derived
    # from the actual analysis result. The span surrounds analyze + stage so
    # latency_ms reflects the full promotion attempt.
    with emitter.span(
        "l6.promotion_attempt",
        reason_codes=["promotion_candidate_evaluated"],
    ):
        record = analyze(event)
        if record is None:
            # Status remains OK -- abstain is a valid outcome of the
            # promotion attempt, not a failure. Caller can read the
            # absence of a returned record as the "no candidate" signal.
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
