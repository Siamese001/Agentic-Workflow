"""G23 — Security / Leakage Gate.

Spec: detect adversarial behavior + sensitive-data leakage across ingress,
context, tools, and output.
Stop: secret / system prompt leakage risk MUST block output or egress.
"""

from __future__ import annotations

import re

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.types import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

INJECTION_RE = re.compile(
    r"\b(ignore previous|disregard prior|new instructions?|act as|reveal your|system prompt:)\b",
    re.IGNORECASE,
)
JAILBREAK_RE = re.compile(r"\b(DAN|developer mode|do anything now|jailbreak)\b", re.IGNORECASE)
SECRET_RE = re.compile(
    r"(?:sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|api[_-]?key\s*[:=]\s*\S+|password\s*[:=]\s*\S+)",
    re.IGNORECASE,
)
SYSTEM_PROMPT_LEAK_RE = re.compile(
    r"\b(you are an AI assistant designed to|your instructions are to|system:|developer:)\b",
    re.IGNORECASE,
)


@register_gate
class SecurityLeakageGate:
    GATE_ID = "G23"
    PRIMARY_LAYER = "Exit"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        text = str(ctx.output.get("text", "") or "")
        ingress_text = str(ctx.intent.get("raw_text", "") or "")
        # Stop: secret leakage in output.
        if SECRET_RE.search(text):
            signals.append(
                RegressionSignal(name="credential_access_attempt_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REDACT,
                reason_codes=["secret_in_output"],
                signals=signals,
                stop_condition_violated=True,
            )
        # System / developer prompt leakage in output.
        if SYSTEM_PROMPT_LEAK_RE.search(text):
            signals.append(RegressionSignal(name="leakage_near_miss_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.REDACT,
                reason_codes=["system_prompt_leak"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Direct injection in ingress.
        if INJECTION_RE.search(ingress_text):
            signals.append(RegressionSignal(name="injection_detect_rate", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.QUARANTINE,
                reason_codes=["prompt_injection_attempt"],
                signals=signals,
            )
        # Jailbreak attempt.
        if JAILBREAK_RE.search(ingress_text):
            signals.append(RegressionSignal(name="safety_bypass_attempt_count", value=1.0, severity="alert"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.SAFE_COMPLETE.value,
                reason_codes=["jailbreak_attempt"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Indirect injection via tool output bleeding into final text.
        tool_out = str(ctx.tool_call.get("output", "") or "")
        if tool_out and INJECTION_RE.search(tool_out) and INJECTION_RE.search(text):
            signals.append(
                RegressionSignal(name="injection_false_negative_rate", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.QUARANTINE,
                reason_codes=["indirect_injection_bleed"],
                signals=signals,
                stop_condition_violated=True,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            reason_codes=["security_clean"],
            signals=signals,
        )


__all__ = ["SecurityLeakageGate"]
