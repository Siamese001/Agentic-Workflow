"""Emits ``judge_result`` events to ObservabilityAdapter.

The assembler's Qwen-first rationale cascade produces a pass/fail signal
against the judge rubric. This service wraps that signal in a structured
event and delegates emission to :class:`ObservabilityAdapter`.

Events are deliberately scalar-only (no PII, no raw LLM output) to keep
the telemetry surface regulator-audit-friendly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_underwriting_ai.integrations.observability_adapter import (
    ObservabilityAdapter,
)


@dataclass(frozen=True)
class JudgeTelemetryEvent:
    """Single judge-pass telemetry record (not PII-bearing)."""

    request_id: str
    rubric_id: str
    rubric_version: int
    passed: bool
    model_used: str
    fallback_reason: str = ""
    latency_ms: float = 0.0
    rationale_chars: int = 0
    first_failed_gate: str = "none"
    context: dict[str, Any] = field(default_factory=dict)


class LLMJudgeTelemetryService:
    """Thin emitter: accepts a :class:`JudgeTelemetryEvent`, logs it."""

    def __init__(self, adapter: ObservabilityAdapter | None = None) -> None:
        self._adapter = adapter or ObservabilityAdapter()

    @property
    def adapter(self) -> ObservabilityAdapter:
        return self._adapter

    def emit(self, event: JudgeTelemetryEvent) -> None:
        """Emit ``judge_result`` via the observability adapter."""
        self._adapter.emit_judge_result(
            request_id=event.request_id,
            rubric_id=event.rubric_id,
            rubric_version=event.rubric_version,
            passed=event.passed,
            model_used=event.model_used,
            fallback_reason=event.fallback_reason,
            latency_ms=event.latency_ms,
            rationale_chars=event.rationale_chars,
            first_failed_gate=event.first_failed_gate,
            **event.context,
        )
