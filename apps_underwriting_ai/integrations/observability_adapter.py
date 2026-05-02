"""ObservabilityAdapter — structured event emission for apps_underwriting_ai.

Wraps the lifecycle telemetry surface so engines + integrations emit
consistent app-tagged events. Skeleton implementation: events are logged
to a structured logger; full OTEL wiring will be layered on later.
"""

from __future__ import annotations

import logging
from typing import Any

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Structured-event emitter for apps_underwriting_ai."""

    APP = "apps_underwriting_ai"

    def emit(self, event: str, **fields: Any) -> None:
        """Emit a structured event.

        Args:
            event: Event name (e.g., 'pipeline.start', 'stage.complete').
            **fields: Arbitrary structured fields.
        """
        _log.info("event", extra={"app": self.APP, "event": event, **fields})

    def emit_stage_start(self, stage_name: str, request_id: str) -> None:
        """Emit a stage-start event."""
        self.emit("stage.start", stage_name=stage_name, request_id=request_id)

    def emit_stage_complete(
        self, stage_name: str, request_id: str, duration_ms: float = 0.0
    ) -> None:
        """Emit a stage-complete event."""
        self.emit(
            "stage.complete",
            stage_name=stage_name,
            request_id=request_id,
            duration_ms=duration_ms,
        )

    def emit_decision(
        self, request_id: str, verdict: str, evidence_count: int
    ) -> None:
        """Emit the final decision event."""
        self.emit(
            "decision.emitted",
            request_id=request_id,
            verdict=verdict,
            evidence_count=evidence_count,
        )

    def emit_judge_result(
        self,
        request_id: str,
        rubric_id: str,
        rubric_version: int,
        passed: bool,
        model_used: str,
        fallback_reason: str = "",
        latency_ms: float = 0.0,
        rationale_chars: int = 0,
        first_failed_gate: str = "none",
        **extra: Any,
    ) -> None:
        """Emit a ``judge_result`` event for the rationale-pass telemetry.

        Wired by :class:`apps_underwriting_ai.services.LLMJudgeTelemetryService`.
        Keep payload scalar-only (no raw LLM text, no PII).
        """
        self.emit(
            "judge_result",
            request_id=request_id,
            rubric_id=rubric_id,
            rubric_version=rubric_version,
            passed=passed,
            model_used=model_used,
            fallback_reason=fallback_reason,
            latency_ms=latency_ms,
            rationale_chars=rationale_chars,
            first_failed_gate=first_failed_gate,
            **extra,
        )
