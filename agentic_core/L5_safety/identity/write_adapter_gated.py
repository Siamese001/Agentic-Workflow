"""Lane-Gated Principal-Aware Write — L5 v4 Wave-N wire-in.

Wraps `emit_v4_write` (Wave-E) with a pre-commit `evaluate_runtime_lane_with_sweep`
(Wave-L) check. The write is only emitted if the composed runtime-lane
decision is `allow`; otherwise the caller either gets `None` (soft mode)
or an exception (strict mode).

Design:
- Soft mode (default) returns (None, decision) on non-allow, letting the
  caller route the record to HITL step-up / audit without crashing the
  turn.
- Strict mode raises `WriteRefused` so the write path aborts immediately.
- In both modes the composed decision is produced (so an audit sink can
  still record the refusal with full attribution via Wave-M).

Adoption:
    from agentic_core.L5_safety.identity.write_adapter_gated import (
        emit_lane_gated_write, WriteRefused,
    )
    v3_key, attached, decision = emit_lane_gated_write(
        token=v4_token,
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
        touches_write_surface=True,
    )
    if v3_key is None:
        # decision.final_action != "allow" — route to audit + step-up
        ...

Reference:
  - write_adapter.py (Wave-E base)
  - runtime_entry_sweep.py (Wave-L source of the gating decision)
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from typing import Sequence

from agentic_core.interfaces.principal_aware_write import PrincipalAttachedWrite
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    evaluate_runtime_lane_with_sweep,
)
from agentic_core.L5_safety.identity.write_adapter import emit_v4_write


class WriteRefused(Exception):
    """Raised (strict mode) when the runtime-lane decision denies the write.

    Carries the full decision on `.decision` so the caller can route the
    attribution into audit / step-up without re-running the gates.
    """

    def __init__(self, decision: RuntimeLaneDecisionWithSweep):
        super().__init__(
            f"WriteRefused: final_action={decision.final_action}",
        )
        self.decision = decision


def emit_lane_gated_write(
    *,
    token: CapabilityTokenV4Artifact,
    plan_hash: str,
    tool_calls: Sequence[str],
    stdout_digest: str,
    state_diff_hash: str,
    action_connector_id: str | None = None,
    action_tool_id: str | None = None,
    touches_write_surface: bool = True,
    ingress_outcomes: Sequence[GuardrailOutcome] = (),
    egress_outcomes: Sequence[GuardrailOutcome] = (),
    guard_model_outcome: GuardrailOutcome | None = None,
    strict: bool = False,
) -> tuple[str | None, PrincipalAttachedWrite | None, RuntimeLaneDecisionWithSweep]:
    """Emit a v4 write only if the runtime-lane decision is `allow`.

    Returns (v3_key_or_None, attached_or_None, decision). The decision
    is ALWAYS returned so the caller can route non-allow outcomes to
    audit with complete attribution.

    If `strict=True` and the decision denies the write, raises
    `WriteRefused` carrying the decision.
    """
    decision = evaluate_runtime_lane_with_sweep(
        token=token,
        action_required_rung="mutate",
        action_connector_id=action_connector_id,
        action_tool_id=action_tool_id,
        touches_write_surface=touches_write_surface,
        ingress_outcomes=ingress_outcomes,
        egress_outcomes=egress_outcomes,
        guard_model_outcome=guard_model_outcome,
    )

    if decision.final_action != "allow":
        if strict:
            raise WriteRefused(decision)
        return None, None, decision

    v3_key, attached = emit_v4_write(
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
        principal_chain=token.principal_chain,
    )
    return v3_key, attached, decision


__all__ = ["WriteRefused", "emit_lane_gated_write"]
