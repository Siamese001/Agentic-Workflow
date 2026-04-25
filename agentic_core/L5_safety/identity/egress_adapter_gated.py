"""Lane-Gated Principal-Aware Egress — L5 v4 Wave-O wire-in.

Wraps `attach_principal_to_egress` (Wave-W3) with a pre-emit
`evaluate_runtime_lane_with_sweep` (Wave-L) check. The egress envelope
is only emitted if the composed runtime-lane decision is `allow`;
otherwise the caller either gets `None` (soft mode) or an exception
(strict mode).

Mirror of Wave-N (write side) for the egress path — LLM gateway calls,
MCP connector invocations, HTTP tool calls, and A2A handoffs that cross
the external boundary.

Adoption:
    from agentic_core.L5_safety.identity.egress_adapter_gated import (
        emit_lane_gated_egress, EgressRefused,
    )
    envelope, decision = emit_lane_gated_egress(
        token=v4_token,
        egress_kind="mcp_connector",
        target_id="claude_mcp",
        request_digest=req_d,
        response_digest=resp_d,
    )
    if envelope is None:
        # decision denied egress — route to audit + step-up
        ...

Reference:
  - interfaces/principal_aware_egress.py (Wave-W3 base)
  - runtime_entry_sweep.py (Wave-L gating decision)
  - write_adapter_gated.py (Wave-N sibling for write path)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from typing import Sequence

from agentic_core.interfaces.principal_aware_egress import (
    EgressKind,
    PrincipalEgressEnvelope,
    attach_principal_to_egress,
)
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    evaluate_runtime_lane_with_sweep,
)


# Map egress kind → the rung required to authorize it. LLM providers and
# MCP connectors are "external" — the highest rung. HTTP tools and A2A
# handoffs likewise cross boundaries. Read-side queries that don't mutate
# state could relax this in a future wave via an override param.
_DEFAULT_RUNG_BY_KIND: dict[EgressKind, str] = {
    "llm_provider": "external",
    "mcp_connector": "external",
    "http_tool": "external",
    "a2a_agent": "external",
}


class EgressRefused(Exception):
    """Raised (strict mode) when the runtime-lane decision denies the egress."""

    def __init__(self, decision: RuntimeLaneDecisionWithSweep):
        super().__init__(
            f"EgressRefused: final_action={decision.final_action}",
        )
        self.decision = decision


def emit_lane_gated_egress(
    *,
    token: CapabilityTokenV4Artifact,
    egress_kind: EgressKind,
    target_id: str,
    request_digest: str,
    response_digest: str,
    ingress_outcomes: Sequence[GuardrailOutcome] = (),
    egress_outcomes: Sequence[GuardrailOutcome] = (),
    guard_model_outcome: GuardrailOutcome | None = None,
    strict: bool = False,
) -> tuple[PrincipalEgressEnvelope | None, RuntimeLaneDecisionWithSweep]:
    """Emit a v4 egress envelope only if the runtime-lane decision is `allow`.

    Returns (envelope_or_None, decision). The decision is always returned
    so the caller can route non-allow outcomes to audit with complete
    attribution.

    If `strict=True` and the decision denies, raises `EgressRefused`.
    """
    required_rung = _DEFAULT_RUNG_BY_KIND[egress_kind]
    connector_id = target_id if egress_kind == "mcp_connector" else None
    tool_id = target_id if egress_kind == "http_tool" else None

    decision = evaluate_runtime_lane_with_sweep(
        token=token,
        action_required_rung=required_rung,  # type: ignore[arg-type]
        action_connector_id=connector_id,
        action_tool_id=tool_id,
        touches_write_surface=False,
        ingress_outcomes=ingress_outcomes,
        egress_outcomes=egress_outcomes,
        guard_model_outcome=guard_model_outcome,
    )

    if decision.final_action != "allow":
        if strict:
            raise EgressRefused(decision)
        return None, decision

    envelope = attach_principal_to_egress(
        egress_kind=egress_kind,
        target_id=target_id,
        request_digest=request_digest,
        response_digest=response_digest,
        principal_chain=token.principal_chain,
    )
    return envelope, decision


__all__ = ["EgressRefused", "emit_lane_gated_egress"]
