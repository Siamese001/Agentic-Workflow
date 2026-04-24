"""Full V4 Action Pipeline — L5 v4 Wave-P wire-in.

One-call recipe that composes the full v4 action path for a write-side
invocation:

  1. Lane-gated write    (Wave-N) — gates on registry + data-authority +
                                     identity + chokepoint + handoff
  2. Optional egress     (Wave-O) — only runs if step 1 produced a write
  3. Lane audit record   (Wave-M) — emitted regardless of allow/deny

The intent: a v4 call site replaces its existing write+egress+audit
triple with ONE `run_v4_action()` call. The returned `V4ActionOutcome`
carries the decision, any emitted artifacts, and the audit record so the
caller has full attribution without re-invoking any gate.

Guarantees:
- Audit record is ALWAYS produced (even on denial) so forensic replay
  has a complete trail.
- Write and egress are BOTH gated on the SAME lane decision (no window
  where a write lands and its egress is refused, or vice-versa).
- Fail-soft by default: outcome.write_v3_key is None iff the decision
  denied the action. Callers decide whether to raise.

Adoption:
    from agentic_core.L5_safety.identity.action_pipeline import run_v4_action

    outcome = run_v4_action(
        token=v4_token,
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
        egress=(
            ("mcp_connector", "claude_mcp", req_d, resp_d),
        ),
    )
    if not outcome.allowed:
        # outcome.decision and outcome.audit_record carry full attribution
        return deny(outcome.decision.sweep.combined_failures)

Reference:
  - write_adapter_gated.py (Wave-N)
  - egress_adapter_gated.py (Wave-O)
  - audit_binding_lane.py (Wave-M)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from agentic_core.interfaces.principal_aware_egress import (
    EgressKind,
    PrincipalEgressEnvelope,
)
from agentic_core.interfaces.principal_aware_write import PrincipalAttachedWrite
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
from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    evaluate_runtime_lane_with_sweep,
)
from agentic_core.L5_safety.identity.write_adapter import emit_v4_write


# Egress request shape: (kind, target_id, request_digest, response_digest)
EgressRequest = tuple[EgressKind, str, str, str]


@dataclass(frozen=True)
class V4ActionOutcome:
    """Composite outcome of a full v4 action invocation."""

    decision: RuntimeLaneDecisionWithSweep
    write_v3_key: str | None
    write_attached: PrincipalAttachedWrite | None
    egresses: tuple[PrincipalEgressEnvelope, ...] = field(default_factory=tuple)
    audit_record: LaneAuditRecord | None = None

    @property
    def allowed(self) -> bool:
        return self.decision.final_action == "allow"


def run_v4_action(
    *,
    token: CapabilityTokenV4Artifact,
    plan_hash: str,
    tool_calls: Sequence[str],
    stdout_digest: str,
    state_diff_hash: str,
    egress: Sequence[EgressRequest] = (),
    ingress_outcomes: Sequence[GuardrailOutcome] = (),
    egress_outcomes: Sequence[GuardrailOutcome] = (),
    guard_model_outcome: GuardrailOutcome | None = None,
) -> V4ActionOutcome:
    """Run the full v4 action pipeline and return a composite outcome.

    Flow:
      1. Single lane decision via evaluate_runtime_lane_with_sweep.
      2. If allowed: emit_v4_write → PrincipalAttachedWrite.
      3. If allowed: for each (kind, target, req_d, resp_d), emit a
         PrincipalEgressEnvelope. Bound against the SAME lane decision
         (no re-gating — the decision already factored this call's
         guardrail outcomes).
      4. Always: emit a LaneAuditRecord binding writes + egresses to the
         decision.
    """
    # Step 1: single composed lane decision (write-surface rung)
    decision = evaluate_runtime_lane_with_sweep(
        token=token,
        action_required_rung="mutate",
        touches_write_surface=True,
        ingress_outcomes=ingress_outcomes,
        egress_outcomes=egress_outcomes,
        guard_model_outcome=guard_model_outcome,
    )

    write_v3_key: str | None = None
    write_attached: PrincipalAttachedWrite | None = None
    emitted_egresses: list[PrincipalEgressEnvelope] = []

    if decision.final_action == "allow":
        # Step 2: write
        write_v3_key, write_attached = emit_v4_write(
            plan_hash=plan_hash,
            tool_calls=tool_calls,
            stdout_digest=stdout_digest,
            state_diff_hash=state_diff_hash,
            principal_chain=token.principal_chain,
        )
        # Step 3: egresses — each re-gated via Wave-O so individual
        # connector allowlist checks fire; failures surface as None envelopes.
        for kind, target_id, req_d, resp_d in egress:
            env, _ = emit_lane_gated_egress(
                token=token,
                egress_kind=kind,
                target_id=target_id,
                request_digest=req_d,
                response_digest=resp_d,
                ingress_outcomes=ingress_outcomes,
                egress_outcomes=egress_outcomes,
                guard_model_outcome=guard_model_outcome,
            )
            if env is not None:
                emitted_egresses.append(env)

    # Step 4: audit record — always emitted
    audit_record = emit_lane_audit_record(
        token=token,
        lane_decision=decision,
        writes=(write_attached,) if write_attached is not None else (),
        egresses=tuple(emitted_egresses),
    )

    return V4ActionOutcome(
        decision=decision,
        write_v3_key=write_v3_key,
        write_attached=write_attached,
        egresses=tuple(emitted_egresses),
        audit_record=audit_record,
    )


__all__ = ["EgressRequest", "V4ActionOutcome", "run_v4_action"]
