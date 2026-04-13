"""EvaluationSignalBundle — C2 signal bundle contract.

Explicitly separates live control signals (BUS D/E — current run) from async
telemetry signals (BUS T — future-run learning pipeline).

Maps to: docs/reference/C2_Observability_Telemetry_Control_Signals.md
    BUS D/E — Real-time live control: Deny / Re-enter, Escalation triggers.
    BUS T   — Async telemetry: Metrics / Timing / Drift, Grounding telemetry.

Layer authority: L6 (Observability — read-only; no mutations to any layer)
No business logic.  No persistence.  Pure typed signal containers.

Architectural invariant
-----------------------
LiveControlSignal.scope  = 'CURRENT_RUN'  — can affect the run that produced them.
AsyncTelemetrySignal.scope = 'FUTURE_RUN' — feeds learning; must never mutate the
                                             completed run.
EvaluationSignalBundle co-locates both in one envelope to preserve observability
context, but the two tuple fields are typed separately so callers cannot mix them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar


class LiveSignalType(str, Enum):
    """Signal types that belong on BUS D/E (live control — current run).

    DENY      — Hard deny; gate should return DENY_RETURN.
    ESCALATE  — Confidence or policy ambiguity; gate should ESCALATE_TO_HITL.
    ANOMALY   — Deviation detected; caller decides severity routing.
    RE_ENTER  — Output must re-enter evaluation (e.g. after HITL re-clearance).
    """

    DENY = "DENY"
    ESCALATE = "ESCALATE"
    ANOMALY = "ANOMALY"
    RE_ENTER = "RE_ENTER"


class TelemetrySignalType(str, Enum):
    """Signal types that belong on BUS T (async telemetry — future-run only).

    METRIC      — Evaluation score or quality metric.
    DRIFT       — Schema, rubric, or behavior drift indicator.
    PERFORMANCE — Latency, throughput, or resource measurement.
    GROUNDING   — Citation / provenance / support coverage signal.
    TIMING      — Wall-clock or monotonic timing record.
    """

    METRIC = "METRIC"
    DRIFT = "DRIFT"
    PERFORMANCE = "PERFORMANCE"
    GROUNDING = "GROUNDING"
    TIMING = "TIMING"


@dataclass(frozen=True)
class LiveControlSignal:
    """BUS D/E — Real-time signal that can affect the current run disposition.

    Produced by: L6 VERIFY SPINE (Bell Tower) → BUS D/E
    Consumed by: Exit control gate (current run only)

    scope = 'CURRENT_RUN': must never be stored for future-run processing.

    signal_id         — Unique identifier for this signal.
    trace_id          — Links to the execution trace for correlation.
    signal_type       — One of LiveSignalType.
    reason            — Human-readable justification.
    disposition_hint  — ExitDisposition.value string recommended by the observer;
                        the gate may override this hint.
    issued_at         — Monotonic epoch tick.
    """

    scope: ClassVar[str] = "CURRENT_RUN"

    signal_id: str
    trace_id: str

    signal_type: LiveSignalType = LiveSignalType.ANOMALY
    reason: str = ""
    disposition_hint: str = ""
    issued_at: float = 0.0


@dataclass(frozen=True)
class AsyncTelemetrySignal:
    """BUS T — Async telemetry payload for future-run learning.

    Produced by: L6 VERIFY SPINE → BUS T
    Consumed by: System learning pipeline (future-run only)

    scope = 'FUTURE_RUN': must never influence the completed current run.

    signal_id       — Unique identifier for this signal.
    run_id          — Execution run_id (natural correlation key).
    signal_type     — One of TelemetrySignalType.
    payload         — Arbitrary metric or observation dict.
    latency_ms      — Latency measurement (0.0 = not measured).
    drift_score     — Drift magnitude 0.0–1.0 (0.0 = no drift detected).
    anomaly_score   — Anomaly magnitude 0.0–1.0 (0.0 = no anomaly detected).
    issued_at       — Monotonic epoch tick.
    """

    scope: ClassVar[str] = "FUTURE_RUN"

    signal_id: str
    run_id: str

    signal_type: TelemetrySignalType = TelemetrySignalType.METRIC
    payload: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    drift_score: float = 0.0
    anomaly_score: float = 0.0
    issued_at: float = 0.0


@dataclass(frozen=True)
class EvaluationSignalBundle:
    """Consolidated C2 signal bundle: live control + async telemetry, explicitly separated.

    Maps to: docs/reference/C2_Observability_Telemetry_Control_Signals.md

    The live_control_signals (BUS D/E) affect the CURRENT run; they are
    produced by L6 VERIFY SPINE and routed to the exit gate before disposition
    is finalised.

    The async_telemetry_signals (BUS T) feed the FUTURE-RUN learning pipeline;
    they are produced after the current-run boundary is crossed and must never
    mutate anything in the completed run.

    Co-locating both in one typed envelope preserves observability context while
    the separate tuple types enforce the BUS D/E vs BUS T boundary at compile
    time: a function that consumes live_control_signals cannot accidentally
    iterate async_telemetry_signals and vice versa.

    Layer authority: L6 (read-only observer — no mutations)
    No business logic.  No persistence.  Pure typed signal envelope.

    Fields
    ------
    bundle_id:
        Unique identifier for this signal bundle.
    run_id:
        Execution run_id (correlation key).
    live_control_signals:
        Tuple of LiveControlSignal objects (BUS D/E).  May be empty.
    async_telemetry_signals:
        Tuple of AsyncTelemetrySignal objects (BUS T).  May be empty.
    sealed_at:
        Monotonic epoch tick at bundle creation.
    """

    bundle_id: str
    run_id: str

    live_control_signals: tuple[LiveControlSignal, ...] = field(default_factory=tuple)
    async_telemetry_signals: tuple[AsyncTelemetrySignal, ...] = field(default_factory=tuple)

    sealed_at: float = 0.0


__all__ = [
    "LiveSignalType",
    "TelemetrySignalType",
    "LiveControlSignal",
    "AsyncTelemetrySignal",
    "EvaluationSignalBundle",
]
