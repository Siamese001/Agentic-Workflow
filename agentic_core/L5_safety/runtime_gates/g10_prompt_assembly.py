"""G10 — Prompt Assembly Gate.

Spec: ensure prompt packet is bounded, authority-ordered, replayable, and
injection-resistant. Canonical slot order: S0 -> D0 -> I0 -> E0 -> C0 -> M0
-> U0 -> H0; R0 bound through API response_schema, not prose.
Stop: if lower-authority content can override higher-authority instructions,
prompt MUST NOT dispatch.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.base import register_gate
from agentic_core.L5_safety.runtime_gates.contracts import (
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    RegressionSignal,
)

CANONICAL_ORDER = ("S0", "D0", "I0", "E0", "C0", "M0", "U0", "H0")
MAX_TOKENS_DEFAULT = 50_000


@register_gate
class PromptAssemblyGate:
    GATE_ID = "G10"
    PRIMARY_LAYER = "PA"

    def evaluate(self, ctx: GateContext) -> GateDecision:
        signals: list[RegressionSignal] = []
        packet = ctx.prompt_packet
        slots = list(packet.get("slot_order", []) or [])
        if not slots:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT.value,
                reason_codes=["empty_slot_order"],
                signals=signals,
                stop_condition_violated=True,
            )
        # Authority order check: every slot present must obey CANONICAL_ORDER.
        observed_indices = [CANONICAL_ORDER.index(s) for s in slots if s in CANONICAL_ORDER]
        if observed_indices != sorted(observed_indices):
            signals.append(
                RegressionSignal(name="prompt_injection_near_miss_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REBUILD.value,
                reason_codes=["authority_order_violation"],
                signals=signals,
                metadata={"observed": slots},
                stop_condition_violated=True,
            )
        unknown = [s for s in slots if s not in CANONICAL_ORDER]
        if unknown:
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT.value,
                reason_codes=["unknown_slot"],
                signals=signals,
                metadata={"unknown_slots": unknown},
            )
        # Token budget.
        max_tokens = int(packet.get("max_tokens", MAX_TOKENS_DEFAULT))
        used = int(packet.get("used_tokens", 0))
        if used > max_tokens:
            signals.append(RegressionSignal(name="prompt_budget_overflow_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.SHRINK_CONTEXT.value,
                reason_codes=["token_budget_exceeded"],
                signals=signals,
                metadata={"used": used, "max": max_tokens},
            )
        # Schema binding required for structured output.
        if packet.get("requires_structured_output") and not packet.get("response_schema_bound"):
            signals.append(RegressionSignal(name="schema_binding_missing_rate", value=1.0, severity="warn"))
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.RETRY,
                alias=DecisionAlias.REBUILD.value,
                reason_codes=["schema_not_bound"],
                signals=signals,
            )
        # HMAC + manifest.
        if not packet.get("hmac") or not packet.get("manifest_hash"):
            signals.append(
                RegressionSignal(name="prompt_manifest_mismatch_count", value=1.0, severity="alert")
            )
            return GateDecision(
                gate_id=self.GATE_ID,
                disposition=Disposition.DENY,
                alias=DecisionAlias.REJECT.value,
                reason_codes=["unsigned_prompt_packet"],
                signals=signals,
                stop_condition_violated=True,
            )
        return GateDecision(
            gate_id=self.GATE_ID,
            disposition=Disposition.ALLOW,
            alias=DecisionAlias.EMIT.value,
            reason_codes=["prompt_packet_signed"],
            signals=signals,
        )


__all__ = ["PromptAssemblyGate"]
