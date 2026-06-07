"""V4-Aware LLM Gateway Wrapper — closes SovereignLLMGateway deferred scope.

Thin additive wrapper over `SovereignLLMGateway.generate()` that emits a
lane-gated egress envelope (Wave-O) before the outbound call and records
the audit trail via the existing v4 surface.

Design:
- Does NOT modify SovereignLLMGateway (970-line class, many consumers).
- Wraps a `SovereignLLMGateway` instance via composition, not inheritance.
- Pre-call: evaluate runtime lane with sweep (Wave-L); if denied, refuse
  without invoking the real provider (saves tokens + prevents leaks).
- Post-call: emit `PrincipalEgressEnvelope` + `LaneAuditRecord` binding
  the request + response digests to the principal chain.

Adoption (at SovereignLLMGateway call sites):
    # BEFORE
    response = gateway.generate(artifact)

    # AFTER (v4-aware)
    from agentic_core.L5_safety.identity.llm_gateway_v4 import (
        GovernedLLMGateway, LLMEgressRefused,
    )
    governed = GovernedLLMGateway(gateway, target_id="openai.gpt-4")
    result = governed.generate(artifact, token=v4_token)
    # result.response is None iff denied; result.audit_record always present

Reference:
  - agentic_core/L2_execution/enforcement/SovereignLLMGateway.py (wrapped)
  - egress_adapter_gated.py (Wave-O gating)
  - audit_binding_lane.py (Wave-M record)
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from agentic_core.interfaces.principal_aware_egress import PrincipalEgressEnvelope
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.audit_binding_lane import (
    LaneAuditRecord,
    emit_lane_audit_record,
)
from agentic_core.L5_safety.identity.egress_adapter_gated import (
    emit_lane_gated_egress,
)
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    evaluate_runtime_lane_with_sweep,
)


class LLMEgressRefused(Exception):
    """Raised (strict mode) when the lane decision denies the LLM call."""

    def __init__(self, decision: RuntimeLaneDecisionWithSweep):
        super().__init__(
            f"LLMEgressRefused: final_action={decision.final_action}",
        )
        self.decision = decision


@dataclass(frozen=True)
class GovernedLLMResult:
    """Composite outcome of a governed LLM invocation."""

    response: Any | None
    envelope: PrincipalEgressEnvelope | None
    decision: RuntimeLaneDecisionWithSweep
    audit_record: LaneAuditRecord

    @property
    def allowed(self) -> bool:
        return self.decision.final_action == "allow"


def _digest_str(obj: Any) -> str:
    """Stable digest for arbitrary request/response payloads."""
    return hashlib.sha256(repr(obj).encode("utf-8")).hexdigest()


class GovernedLLMGateway:
    """Lane-gated wrapper over any object exposing a `.generate(artifact)` method.

    Does not depend on `SovereignLLMGateway` as a type so the wire-in
    stays layer-clean (L5 module wrapping an L2 class by duck-type only).
    """

    def __init__(self, inner: Any, *, target_id: str):
        self._inner = inner
        self._target_id = target_id

    def generate(
        self,
        artifact: Any,
        *,
        token: CapabilityTokenV4Artifact,
        strict: bool = False,
    ) -> GovernedLLMResult:
        """Pre-gate the call, invoke the inner gateway, audit-bind the result."""
        request_digest = _digest_str(artifact)

        # Stage 1: pre-call lane decision only (no envelope yet — response
        # digest isn't known). evaluate_runtime_lane_with_sweep uses the
        # same gates emit_lane_gated_egress would; any denial reason that
        # applies pre-call also applies post-call.
        decision_pre = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="external",
            action_connector_id=self._target_id,
            touches_write_surface=False,
        )

        if decision_pre.final_action != "allow":
            # Denial path: emit audit record binding the refusal.
            audit = emit_lane_audit_record(
                token=token,
                lane_decision=decision_pre,
                writes=(),
                egresses=(),
            )
            if strict:
                raise LLMEgressRefused(decision_pre)
            return GovernedLLMResult(
                response=None,
                envelope=None,
                decision=decision_pre,
                audit_record=audit,
            )

        # Stage 2: invoke the inner gateway (real LLM call).
        response = self._inner.generate(artifact)
        response_digest = _digest_str(response)

        # Stage 3: emit final egress envelope with the real response digest.
        envelope, decision = emit_lane_gated_egress(
            token=token,
            egress_kind="llm_provider",
            target_id=self._target_id,
            request_digest=request_digest,
            response_digest=response_digest,
        )

        # Stage 4: lane audit record binding write-empty + egress.
        audit = emit_lane_audit_record(
            token=token,
            lane_decision=decision,
            writes=(),
            egresses=(envelope,) if envelope is not None else (),
        )

        return GovernedLLMResult(
            response=response,
            envelope=envelope,
            decision=decision,
            audit_record=audit,
        )


__all__ = [
    "GovernedLLMGateway",
    "GovernedLLMResult",
    "LLMEgressRefused",
]
