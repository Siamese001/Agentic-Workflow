from __future__ import annotations

from dataclasses import dataclass, field
import threading
import time


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
