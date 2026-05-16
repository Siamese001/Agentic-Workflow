"""G13 — Tool / Retrieved Output Trust Gate.

Spec: prevent untrusted content from hijacking model context or execution.
Stop: untrusted content MUST NOT be treated as instruction.
"""

from __future__ import annotations

import re

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

INSTRUCTION_RE = re.compile(
    r"\b(ignore previous|disregard prior|new instructions?|system prompt:|act as |reveal your)\b",
    re.IGNORECASE,
)
HIDDEN_TEXT_PATTERNS = (
    "<!--",  # HTML comment hiding
    "data:text/html",
    "javascript:",
    "\u200b",  # zero-width space
    "\u202e",  # right-to-left override
)
TRUSTED_ORIGINS = {"system", "policy", "user_turn"}


@register_gate
class ToolOutputTrustGate:
    GATE_ID = "G13"
    PRIMARY_LAYER = "C0"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        body = str(ctx.tool_call.get("output", "") or "")
        origin = ctx.tool_call.get("origin", "tool_output")
        if origin in TRUSTED_ORIGINS:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.ALLOW,
                alias=DecisionAlias.PASS_AS_DATA.value,
                reason_codes=["trusted_origin"],
                signals=signals,
            )
        if INSTRUCTION_RE.search(body):
            signals.append(RegressionSignal(name="tool_output_injection_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.QUARANTINE,
                reason_codes=["embedded_instruction_detected"],
                signals=signals,
                stop_condition_violated=True,
            )
        if any(p in body for p in HIDDEN_TEXT_PATTERNS):
            signals.append(RegressionSignal(name="connector_poisoning_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REDACT,
                alias=DecisionAlias.STRIP.value,
                reason_codes=["hidden_text_detected"],
                signals=signals,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.PASS_AS_DATA.value,
            reason_codes=["content_clean"],
            signals=signals,
        )


__all__ = ["ToolOutputTrustGate"]
