"""Qwen vLLM Inference Telemetry.

Telemetry and metrics collection for Qwen inference in L3 orchestration.
Separate from healing telemetry to maintain clean boundaries.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_evaluation_metric,
    _emit_records_telemetry_event,
)


@dataclass
class QwenInferenceMetric:
    """Single metric data point."""
    timestamp: float
    app_name: str
    model_id: str
    metric_name: str
    value: float
    context: dict[str, str] = field(default_factory=dict)


@dataclass
class QwenSessionMetrics:
    """Metrics for a single inference session."""
    session_id: str
    app_name: str
    start_time: float
    end_time: float | None = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    average_confidence: float = 0.0
    tokens_used: int = 0
    errors: list[str] = field(default_factory=list)


class QwenInferenceTelemetry:
    """Telemetry collector for Qwen inference operations.

    Tracks performance, usage, and error metrics across all apps.
    """

    def __init__(self):
        self._metrics: list[QwenInferenceMetric] = []
        self._sessions: dict[str, QwenSessionMetrics] = {}

    def start_session(self, app_name: str) -> str:
        """Start a new telemetry session.

        Args:
            app_name: Name of the app

        Returns:
            Session ID
        """
        session_id = f"{app_name}_{int(time.time() * 1000)}"

        session = QwenSessionMetrics(
            session_id=session_id,
            app_name=app_name,
            start_time=time.time()
        )

        self._sessions[session_id] = session

        _emit_records_telemetry_event(session_id, "qwen_inference_telemetry", "session_start")

        return session_id

    def end_session(self, session_id: str) -> QwenSessionMetrics | None:
        """End a telemetry session and calculate final metrics.

        Args:
            session_id: Session ID to end

        Returns:
            Session metrics if found
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]
        session.end_time = time.time()

        # Calculate final metrics
        if session.total_requests > 0:
            session.average_confidence = sum(
                m.value for m in self._metrics
                if m.context.get("session_id") == session_id and m.metric_name == "confidence"
            ) / session.total_requests

        _emit_captures_evaluation_metric(
            session_id,
            "apps_qwen_telemetry",
            "session_duration",
        )

        return session

    def record_request_start(self, session_id: str, app_name: str, model_id: str) -> None:
        """Record the start of an inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model being used
        """
        if session_id not in self._sessions:
            return

        self._sessions[session_id].total_requests += 1

        metric = QwenInferenceMetric(
            timestamp=time.time(),
            app_name=app_name,
            model_id=model_id,
            metric_name="request_start",
            value=1.0,
            context={"session_id": session_id}
        )

        self._metrics.append(metric)

    def record_request_success(
        self,
        session_id: str,
        app_name: str,
        model_id: str,
        latency_ms: float,
        confidence: float,
        tokens_used: int
    ) -> None:
        """Record successful inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model used
            latency_ms: Request latency
            confidence: Response confidence
            tokens_used: Tokens consumed
        """
        if session_id not in self._sessions:
            return

        session = self._sessions[session_id]
        session.successful_requests += 1
        session.total_latency_ms += latency_ms
        session.tokens_used += tokens_used

        # Record individual metrics
        metrics = [
            QwenInferenceMetric(
                timestamp=time.time(),
                app_name=app_name,
                model_id=model_id,
                metric_name="latency_ms",
                value=latency_ms,
                context={"session_id": session_id}
            ),
            QwenInferenceMetric(
                timestamp=time.time(),
                app_name=app_name,
                model_id=model_id,
                metric_name="confidence",
                value=confidence,
                context={"session_id": session_id}
            ),
            QwenInferenceMetric(
                timestamp=time.time(),
                app_name=app_name,
                model_id=model_id,
                metric_name="tokens_used",
                value=float(tokens_used),
                context={"session_id": session_id}
            )
        ]

        for metric in metrics:
            self._metrics.append(metric)
            _emit_captures_evaluation_metric(
                session_id,
                "qwen_inference_telemetry",
                f"qwen_inference_{metric.metric_name}",
            )

    def record_request_error(
        self,
        session_id: str,
        app_name: str,
        model_id: str,
        error_message: str
    ) -> None:
        """Record failed inference request.

        Args:
            session_id: Session ID
            app_name: App name
            model_id: Model used
            error_message: Error description
        """
        if session_id not in self._sessions:
            return

        session = self._sessions[session_id]
        session.failed_requests += 1
        session.errors.append(error_message)

        metric = QwenInferenceMetric(
            timestamp=time.time(),
            app_name=app_name,
            model_id=model_id,
            metric_name="error",
            value=1.0,
            context={
                "session_id": session_id,
                "error": error_message
            }
        )

        self._metrics.append(metric)

        _emit_records_telemetry_event(session_id, "qwen_inference_telemetry", "request_error")

    def get_session_summary(self, session_id: str) -> dict[str, float] | None:
        """Get summary metrics for a session.

        Args:
            session_id: Session ID

        Returns:
            Summary metrics dictionary
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]

        if session.total_requests == 0:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "average_latency_ms": 0.0,
                "average_confidence": 0.0,
                "total_tokens": 0
            }

        return {
            "total_requests": session.total_requests,
            "success_rate": session.successful_requests / session.total_requests,
            "average_latency_ms": session.total_latency_ms / session.successful_requests if session.successful_requests > 0 else 0.0,
            "average_confidence": session.average_confidence,
            "total_tokens": session.tokens_used
        }

    def get_app_summary(self, app_name: str) -> dict[str, float]:
        """Get aggregated metrics for an app.

        Args:
            app_name: App name

        Returns:
            Aggregated metrics
        """
        app_metrics = [m for m in self._metrics if m.app_name == app_name]

        if not app_metrics:
            return {
                "total_requests": 0,
                "success_rate": 0.0,
                "average_latency_ms": 0.0,
                "average_confidence": 0.0
            }

        # Calculate aggregates
        latency_metrics = [m for m in app_metrics if m.metric_name == "latency_ms"]
        confidence_metrics = [m for m in app_metrics if m.metric_name == "confidence"]
        error_metrics = [m for m in app_metrics if m.metric_name == "error"]

        total_requests = len([m for m in app_metrics if m.metric_name == "request_start"])

        return {
            "total_requests": total_requests,
            "success_rate": (total_requests - len(error_metrics)) / total_requests if total_requests > 0 else 0.0,
            "average_latency_ms": sum(m.value for m in latency_metrics) / len(latency_metrics) if latency_metrics else 0.0,
            "average_confidence": sum(m.value for m in confidence_metrics) / len(confidence_metrics) if confidence_metrics else 0.0
        }


# Global telemetry instance for L3 inference
qwen_inference_telemetry = QwenInferenceTelemetry()

# Backward compatibility aliases
AppsQwenMetric = QwenInferenceMetric
AppsQwenSessionMetrics = QwenSessionMetrics
AppsQwenTelemetry = QwenInferenceTelemetry
apps_qwen_telemetry = qwen_inference_telemetry
