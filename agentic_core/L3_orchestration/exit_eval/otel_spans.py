"""OTel span emission per hardening addendum H5.

Two span shapes:

- ``exit_control.gate`` — one per X1 gate execution. Dimension scores
  attach as span events so reviewers can traverse the decision.
- ``exit_control.disposition`` — one per run; links to gate spans so a
  commit can be traced back to the grader trajectory that cleared it.

This module is deliberately decoupled from any specific OTel SDK. It
exposes a ``SpanSink`` protocol that concrete deployments plug in (e.g.
the repo's ``otel_mcp`` ingest path). A no-op sink is provided for tests
and environments without OTel wiring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from agentic_core.L3_orchestration.exit_eval.disposition import (
    Disposition,
    DispositionEnvelope,
)
from agentic_core.L3_orchestration.exit_eval.gates import GateResult


@dataclass(frozen=True)
class GateSpan:
    """Per-gate span attributes per H5.1."""

    name: str  # always "exit_control.gate"
    kind: str  # "INTERNAL"
    status: str  # "OK" | "ERROR"
    attributes: dict[str, Any]
    events: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class DispositionSpan:
    """Per-disposition span per H5.2.

    ``gate_span_ids`` are the span ids of the gate spans this disposition
    references (OTel span-link semantics).
    """

    name: str  # always "exit_control.disposition"
    kind: str  # "INTERNAL"
    status: str  # "OK" | "ERROR"
    attributes: dict[str, Any]
    gate_span_ids: tuple[str, ...] = field(default_factory=tuple)


@runtime_checkable
class SpanSink(Protocol):
    """Abstraction over any OTel exporter.

    Returns the span id for span-link construction.
    """

    def emit_gate(self, span: GateSpan) -> str: ...

    def emit_disposition(self, span: DispositionSpan) -> str: ...


class NoOpSpanSink:
    """Sink that accepts spans and returns stub ids. Useful for tests."""

    def __init__(self) -> None:
        self.gate_spans: list[GateSpan] = []
        self.disposition_spans: list[DispositionSpan] = []
        self._next = 0

    def _id(self) -> str:
        self._next += 1
        return f"span-{self._next:06d}"

    def emit_gate(self, span: GateSpan) -> str:
        self.gate_spans.append(span)
        return self._id()

    def emit_disposition(self, span: DispositionSpan) -> str:
        self.disposition_spans.append(span)
        return self._id()


def build_gate_span(
    result: GateResult,
    *,
    run_id: str,
    track: str,
    trajectory_class: str,
    disposition_hint: str,
    bypass_audit_id: str | None = None,
) -> GateSpan:
    """Construct a per-gate span per H5.1."""
    attributes: dict[str, Any] = {
        "gate": result.gate,
        "run_id": run_id,
        "track": track,
        "trajectory_class": trajectory_class,
        "rubric_version": result.rubric_version,
        "composition": result.composition.value,
        "passed": result.passed,
        "abstain": result.abstained,
        "disposition_hint": disposition_hint,
        "reason_codes": [rc.value for rc in result.reason_codes],
    }
    if result.aggregate.aggregate_score is not None:
        attributes["aggregate_score"] = result.aggregate.aggregate_score
    if result.aggregate.aggregate_threshold is not None:
        attributes["aggregate_threshold"] = result.aggregate.aggregate_threshold
    if bypass_audit_id is not None:
        attributes["bypass_audit_id"] = bypass_audit_id

    events: list[dict[str, Any]] = []
    for d in result.dimension_results:
        events.append(
            {
                "name": "dimension_scored",
                "dim.name": d.name,
                "dim.score": d.score,
                "dim.weight": d.weight,
                "dim.threshold": d.threshold,
                "dim.passed": d.passed,
                "dim.grader_class": d.grader_class.value,
                "dim.abstain": d.abstain,
                "dim.is_hard_gate": d.is_hard_gate,
            }
        )

    status = "ERROR" if result.error else "OK"
    return GateSpan(
        name="exit_control.gate",
        kind="INTERNAL",
        status=status,
        attributes=attributes,
        events=tuple(events),
    )


def build_disposition_span(
    envelope: DispositionEnvelope,
    *,
    gate_span_ids: tuple[str, ...],
) -> DispositionSpan:
    attributes: dict[str, Any] = {
        "disposition": envelope.disposition.value,
        "run_id": envelope.run_id,
        "track": envelope.track,
        "trajectory_class": envelope.trajectory_class,
        "reason_codes": [rc.value for rc in envelope.reason_codes],
        "deny": envelope.deny,
    }
    if envelope.break_glass_audit_id:
        attributes["break_glass_audit_id"] = envelope.break_glass_audit_id
    # Error status for DENY paths; OK for ALLOW / COMMIT / ESCALATE /
    # BREAK_GLASS — those are legitimate exits, not errors.
    status = "ERROR" if envelope.disposition is Disposition.DENY else "OK"
    return DispositionSpan(
        name="exit_control.disposition",
        kind="INTERNAL",
        status=status,
        attributes=attributes,
        gate_span_ids=gate_span_ids,
    )


__all__ = [
    "DispositionSpan",
    "GateSpan",
    "NoOpSpanSink",
    "SpanSink",
    "build_disposition_span",
    "build_gate_span",
]
