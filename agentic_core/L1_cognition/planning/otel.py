"""OTEL span emitters for L1 v6 stages.

Doctrine reference: every 02.X file's PHASE 4 OTEL / TRACE REQUIREMENTS.

Each L1 stage emits exactly three spans: ``input.accepted``,
``core.completed``, ``output.emitted``. Each span carries the
non-authority assertions (``no_route_authority`` /
``no_retrieval_performed`` / ``no_execution_performed`` /
``no_write_performed``) plus the input and output digests so a replay
trace can prove the stage ran and produced the expected hashes.

The emitter is intentionally tiny and dependency-free. It accepts an
optional ``span_sink`` callable so tests can capture spans without
booting a real OpenTelemetry exporter; in production wiring, the sink
is replaced by the project's tracer adapter.

A span is a plain :class:`dict` with stable keys, suitable for
serialisation as JSON or for ingestion by the runtime ADG store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

__all__ = [
    "L1SpanEvent",
    "SpanSink",
    "InMemorySpanSink",
    "make_span_event",
    "STAGE_IDS",
]


STAGE_IDS: tuple[str, ...] = ("02.1", "02.2", "02.3", "02.4", "02.5", "02.6")


@dataclass(frozen=True)
class L1SpanEvent:
    """A single L1 stage OTEL span event (frozen, json-safe)."""

    span_name: str
    request_id: str
    trace_root: str
    l1_stage: str
    policy_hash_observed: str
    instruction_hash_observed: str
    input_digest: str
    output_digest: str
    no_route_authority: bool = True
    no_retrieval_performed: bool = True
    no_execution_performed: bool = True
    no_write_performed: bool = True
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "span_name": self.span_name,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "l1_stage": self.l1_stage,
            "policy_hash_observed": self.policy_hash_observed,
            "instruction_hash_observed": self.instruction_hash_observed,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "no_route_authority": self.no_route_authority,
            "no_retrieval_performed": self.no_retrieval_performed,
            "no_execution_performed": self.no_execution_performed,
            "no_write_performed": self.no_write_performed,
            "extra": dict(self.extra),
        }


SpanSink = Callable[[L1SpanEvent], None]


class InMemorySpanSink:
    """Test-friendly sink that records emitted spans in order."""

    def __init__(self) -> None:
        self.events: list[L1SpanEvent] = []

    def __call__(self, event: L1SpanEvent) -> None:
        self.events.append(event)

    def by_stage(self, stage: str) -> list[L1SpanEvent]:
        return [e for e in self.events if e.l1_stage == stage]

    def names(self) -> list[str]:
        return [e.span_name for e in self.events]


def _validate_stage(stage: str) -> None:
    if stage not in STAGE_IDS:
        raise ValueError(
            f"l1_stage must be one of {STAGE_IDS!r}, got {stage!r}"
        )


def make_span_event(
    *,
    span_name: str,
    request_id: str,
    trace_root: str,
    l1_stage: str,
    policy_hash_observed: str,
    instruction_hash_observed: str,
    input_digest: str,
    output_digest: str,
    extra: dict | None = None,
) -> L1SpanEvent:
    """Construct a frozen :class:`L1SpanEvent` with strict invariants.

    The four ``no_*`` flags are forced ``True`` — the v6 spec requires
    these as positive assertions on every L1 span. If a stage ever needs
    to relax one (it should not — that would mean L1 escaped its lane),
    a separate emitter must be authored, not a parameter on this one.
    """
    _validate_stage(l1_stage)
    if not span_name or not span_name.strip():
        raise ValueError("span_name must be a non-empty string")
    if not request_id or not request_id.strip():
        raise ValueError("request_id must be a non-empty string")
    if not trace_root or not trace_root.strip():
        raise ValueError("trace_root must be a non-empty string")
    return L1SpanEvent(
        span_name=span_name,
        request_id=request_id,
        trace_root=trace_root,
        l1_stage=l1_stage,
        policy_hash_observed=policy_hash_observed,
        instruction_hash_observed=instruction_hash_observed,
        input_digest=input_digest,
        output_digest=output_digest,
        no_route_authority=True,
        no_retrieval_performed=True,
        no_execution_performed=True,
        no_write_performed=True,
        extra=dict(extra or {}),
    )


def emit_stage_spans(
    *,
    stage: str,
    request_id: str,
    trace_root: str,
    policy_hash_observed: str,
    instruction_hash_observed: str,
    input_digest: str,
    output_digest: str,
    span_sink: SpanSink | None = None,
    extra: dict | None = None,
) -> tuple[L1SpanEvent, L1SpanEvent, L1SpanEvent]:
    """Emit the three canonical lifecycle spans for a stage.

    Returns the tuple ``(accepted, completed, emitted)``. When
    ``span_sink`` is provided, each span is also pushed to it.
    """
    accepted = make_span_event(
        span_name=f"l1.{stage}.input.accepted",
        request_id=request_id,
        trace_root=trace_root,
        l1_stage=stage,
        policy_hash_observed=policy_hash_observed,
        instruction_hash_observed=instruction_hash_observed,
        input_digest=input_digest,
        output_digest=output_digest,
        extra=extra,
    )
    completed = make_span_event(
        span_name=f"l1.{stage}.core.completed",
        request_id=request_id,
        trace_root=trace_root,
        l1_stage=stage,
        policy_hash_observed=policy_hash_observed,
        instruction_hash_observed=instruction_hash_observed,
        input_digest=input_digest,
        output_digest=output_digest,
        extra=extra,
    )
    emitted = make_span_event(
        span_name=f"l1.{stage}.output.emitted",
        request_id=request_id,
        trace_root=trace_root,
        l1_stage=stage,
        policy_hash_observed=policy_hash_observed,
        instruction_hash_observed=instruction_hash_observed,
        input_digest=input_digest,
        output_digest=output_digest,
        extra=extra,
    )
    if span_sink is not None:
        span_sink(accepted)
        span_sink(completed)
        span_sink(emitted)
    return accepted, completed, emitted
