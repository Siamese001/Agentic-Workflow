"""Qwen inference telemetry.

Wave F2 M4 (ADR-025, 2026-04-21): This module is **deprecated** as a
standalone telemetry surface. Callers should migrate to the unified
`heal_router.v1` OTEL schema emitted by
`agentic_core.L6_observability.heal_router_otel.HealRouterTelemetryEmitter`.

During the compat window, `record_metric()` also dual-emits a
`heal_router.v1.dispatch.qwen` child span so migration can be incremental.
A `DeprecationWarning` fires once at module import time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time
import warnings

warnings.warn(
    (
        "agentic_core.L3_orchestration.inference.qwen_vllm.telemetry is deprecated "
        "(ADR-025 Wave F2 M4). Use agentic_core.L6_observability.heal_router_otel "
        "HealRouterTelemetryEmitter for unified heal_router.v1 spans."
    ),
    DeprecationWarning,
    stacklevel=2,
)


@dataclass(frozen=True)
class QwenInferenceMetric:
    timestamp: float
    app_name: str
    model_id: str
    metric_name: str
    value: float

    def __post_init__(self) -> None:
        if not self.app_name:
            raise ValueError("app_name must be non-empty")
        if not self.model_id:
            raise ValueError("model_id must be non-empty")
        if not self.metric_name:
            raise ValueError("metric_name must be non-empty")


@dataclass
class QwenSessionMetrics:
    session_id: str
    app_name: str
    start_time: float
    end_time: float | None = None
    metrics: list[QwenInferenceMetric] = field(default_factory=list)

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return max(0.0, (self.end_time - self.start_time) * 1000.0)


class QwenInferenceTelemetry:
    def __init__(self):
        self._sessions: dict[str, QwenSessionMetrics] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def start_session(self, app_name: str) -> str:
        clean_name = str(app_name or "unknown").strip() or "unknown"
        with self._lock:
            self._counter += 1
            now = time.time()
            session_id = f"{clean_name}_{int(now * 1000)}_{self._counter}"
            self._sessions[session_id] = QwenSessionMetrics(
                session_id=session_id,
                app_name=clean_name,
                start_time=now,
            )
            return session_id

    def record_metric(self, session_id: str, metric: QwenInferenceMetric) -> None:
        with self._lock:
            session = self._sessions.setdefault(
                session_id,
                QwenSessionMetrics(
                    session_id=session_id, app_name=metric.app_name, start_time=metric.timestamp
                ),
            )
            session.metrics.append(metric)

        # Wave F2 M2 (ADR-025): dual-emit into the unified heal_router.v1
        # schema under a dispatch.qwen extra_attribute so future MV ingest
        # can correlate legacy QwenInferenceMetric rows with routing traces.
        # Best-effort; never raises into the caller.
        try:  # noqa: SIM105
            from agentic_core.L6_observability.heal_router_otel import (  # noqa: PLC0415
                RoutingSpanRecord,
                get_default_emitter,
            )

            # Synthesize a minimal RoutingSpanRecord-compatible dispatch-child
            # event. We don't have a full RoutingDecision here — just the
            # metric — so we attach it as an extra_attribute payload.
            emitter = get_default_emitter()
            synthetic = RoutingSpanRecord(
                routing_trace_id=f"qwen-metric-{session_id}",
                timestamp=metric.timestamp,
                app_name=metric.app_name,
                tier="MEDIUM",
                gate_applied="DISPATCH_ALIAS",
                gemini_subtier="",
                cost_demoted=False,
                target_model=metric.model_id,
                extra_attributes={
                    "routing.alias_source": "qwen_inference_telemetry",
                    "routing.metric_name": metric.metric_name,
                    "routing.metric_value": metric.value,
                },
            )
            emitter.append_alias_record(synthetic)
        except (
            ImportError,
            AttributeError,
            TypeError,
        ):  # guardian: allow-log-and-swallow -- telemetry dual-emit is best-effort; must never break record_metric
            pass

    def end_session(self, session_id: str) -> QwenSessionMetrics:
        with self._lock:
            session = self._sessions.setdefault(
                session_id,
                QwenSessionMetrics(session_id=session_id, app_name="unknown", start_time=time.time()),
            )
            if session.end_time is None:
                session.end_time = time.time()
            return session

    def get_session(self, session_id: str) -> QwenSessionMetrics | None:
        with self._lock:
            return self._sessions.get(session_id)

    def snapshot_sessions(self) -> dict[str, QwenSessionMetrics]:
        with self._lock:
            return dict(self._sessions)


AppsQwenMetric = QwenInferenceMetric
AppsQwenSessionMetrics = QwenSessionMetrics
AppsQwenTelemetry = QwenInferenceTelemetry

__all__ = [
    "AppsQwenMetric",
    "AppsQwenSessionMetrics",
    "AppsQwenTelemetry",
    "QwenInferenceMetric",
    "QwenInferenceTelemetry",
    "QwenSessionMetrics",
]
