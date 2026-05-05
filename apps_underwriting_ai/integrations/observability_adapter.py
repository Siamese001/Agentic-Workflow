"""ObservabilityAdapter — structured event emission for apps_underwriting_ai.

Wraps the lifecycle telemetry surface so engines + integrations emit
consistent app-tagged events. Emits OTEL spans when the SDK is available
and a tracer is configured; falls back to structured logging otherwise.

D4 — OTEL span wiring.
Plan: apps-underwriting-ai-deferred-scope-e8b2f4 D4.
"""

from __future__ import annotations

import contextlib
import logging
from contextlib import contextmanager
from typing import Any, Generator

_log = logging.getLogger(__name__)

_SERVICE_NAME = "apps_underwriting_ai"
_TRACER_NAME = "apps_underwriting_ai.observability"


def _get_tracer() -> Any:
    """Return an OTEL Tracer or None when SDK is absent / not configured.

    Never raises — the import block is the only failure point and it is
    fully guarded.
    """
    try:
        from opentelemetry import trace  # noqa: PLC0415

        return trace.get_tracer(_TRACER_NAME)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- OTEL SDK optional; fail-soft path
        return None


@contextmanager
def _otel_span(
    span_name: str,
    attributes: dict[str, Any] | None = None,
) -> Generator[Any, None, None]:
    """Context manager: create an OTEL span when SDK is available, else no-op.

    Args:
        span_name: OTEL span name (e.g. ``uw.stage.stage_1_evidence_register``).
        attributes: Optional dict of scalar span attributes.

    Yields:
        The OTEL span object, or a no-op sentinel when the SDK is absent.
    """
    tracer = _get_tracer()
    if tracer is None:
        yield None
        return

    try:
        with tracer.start_as_current_span(span_name) as span:
            if attributes:
                for k, v in attributes.items():
                    with contextlib.suppress(Exception):
                        span.set_attribute(k, v)
            yield span
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- span lifecycle must not crash callers
        yield None


class ObservabilityAdapter:
    """Structured-event emitter for apps_underwriting_ai.

    Emits OTEL spans (when SDK is present) in addition to structured log events.
    Every public method is fail-soft — errors in the telemetry path must never
    propagate to production code paths.
    """

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

    def emit_stage_span(
        self,
        stage_id: str,
        request_id: str,
        success: bool,
        duration_ms: float = 0.0,
        receipt_type: str = "",
    ) -> None:
        """Emit a ``uw.stage.<stage_id>`` OTEL span + structured log event.

        Called by L2 step adapters after each stage completes. Fail-soft —
        never raises.

        Args:
            stage_id: Stage identifier (e.g. ``stage_1_evidence_register``).
            request_id: Correlation ID for the request.
            success: Whether the adapter stage completed successfully.
            duration_ms: Wall-clock duration of the stage in milliseconds.
            receipt_type: L2 receipt type emitted (e.g. ``L2_RECEIPT_E1``).
        """
        span_name = f"uw.stage.{stage_id}"
        attributes = {
            "app": self.APP,
            "stage_id": stage_id,
            "request_id": request_id,
            "success": success,
            "duration_ms": duration_ms,
            "receipt_type": receipt_type,
        }
        try:
            with _otel_span(span_name, attributes=attributes):
                pass
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- telemetry must not crash caller
            pass
        self.emit(
            "stage.span",
            stage_id=stage_id,
            request_id=request_id,
            success=success,
            duration_ms=duration_ms,
            receipt_type=receipt_type,
        )

    def emit_x3_span(
        self,
        request_id: str,
        x3_disposition: str,
        exit_mode: str,
        hitl_posture: str = "HITL_NONE",
        violations: list[str] | None = None,
    ) -> None:
        """Emit a ``uw.exit.x3_disposition`` OTEL span + structured log event.

        Called by UnderwritingExitFecProducer after the X3 disposition is
        selected. Fail-soft — never raises.

        Args:
            request_id: Correlation ID for the request.
            x3_disposition: Selected X3 class (e.g. ``X3A_APPROVE``).
            exit_mode: Exit mode (``FAIL_CLOSED`` or ``SOFT``).
            hitl_posture: HITL posture resolved (e.g. ``HITL_NONE``).
            violations: List of precondition violations, if any.
        """
        span_name = "uw.exit.x3_disposition"
        attributes = {
            "app": self.APP,
            "request_id": request_id,
            "x3_disposition": x3_disposition,
            "exit_mode": exit_mode,
            "hitl_posture": hitl_posture,
            "violation_count": len(violations or []),
        }
        try:
            with _otel_span(span_name, attributes=attributes):
                pass
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- telemetry must not crash caller
            pass
        self.emit(
            "exit.x3_disposition",
            request_id=request_id,
            x3_disposition=x3_disposition,
            exit_mode=exit_mode,
            hitl_posture=hitl_posture,
            violation_count=len(violations or []),
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
