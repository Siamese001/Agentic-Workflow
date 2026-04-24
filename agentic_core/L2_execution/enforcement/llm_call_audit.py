"""
Temperature-0 audit for tool-selection LLM calls — W5-P5.1 (gap plan G11).

Google Vertex AI best practice: for function-calling, use ``temperature=0``
(or other low value) to reduce hallucinated tool arguments. This module
audits outgoing LLM-call envelopes and emits a structured finding when a
tool-selecting call uses a temperature above the configured ceiling.

By design this is a **warning** layer in W5 (not a block). A future wave
can elevate it to a block by raising the returned finding to a
``TripwireTriggered`` via ``tool_guardrail_pipeline``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "LLMCallEnvelope",
    "LLMCallFinding",
    "audit_llm_call",
    "TEMPERATURE_CEILING_DEFAULT",
]


TEMPERATURE_CEILING_DEFAULT = 0.2


@dataclass(frozen=True, slots=True)
class LLMCallEnvelope:
    """Subset of an LLM call relevant to the audit."""

    model: str
    temperature: float
    tool_choice: str  # "none" | "auto" | "required" | specific tool name
    trace_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LLMCallFinding:
    """Non-blocking audit result."""

    compliant: bool
    severity: str  # "info" | "warning" | "critical"
    reason: str
    envelope: LLMCallEnvelope

    def to_dict(self) -> dict[str, Any]:
        return {
            "compliant": self.compliant,
            "severity": self.severity,
            "reason": self.reason,
            "envelope": {
                "model": self.envelope.model,
                "temperature": self.envelope.temperature,
                "tool_choice": self.envelope.tool_choice,
                "trace_id": self.envelope.trace_id,
            },
        }


def audit_llm_call(
    envelope: LLMCallEnvelope,
    *,
    temperature_ceiling: float = TEMPERATURE_CEILING_DEFAULT,
) -> LLMCallFinding:
    """Return an ``LLMCallFinding`` for the envelope.

    Compliant (info) when ``tool_choice == "none"`` (the call is not
    selecting tools) OR ``temperature <= temperature_ceiling``.
    Non-compliant (warning) otherwise. No exceptions are raised.
    """
    tc = (envelope.tool_choice or "").lower()
    if tc == "none":
        return LLMCallFinding(
            compliant=True,
            severity="info",
            reason="tool_choice=none; temperature audit does not apply",
            envelope=envelope,
        )
    if envelope.temperature <= temperature_ceiling:
        return LLMCallFinding(
            compliant=True,
            severity="info",
            reason=(
                f"temperature={envelope.temperature} within ceiling "
                f"{temperature_ceiling}"
            ),
            envelope=envelope,
        )
    return LLMCallFinding(
        compliant=False,
        severity="warning",
        reason=(
            f"temperature={envelope.temperature} exceeds ceiling "
            f"{temperature_ceiling} for tool-selecting call "
            f"(tool_choice={envelope.tool_choice!r})"
        ),
        envelope=envelope,
    )
