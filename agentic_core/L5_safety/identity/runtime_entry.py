"""Runtime Lane Entry Wire-In — L5 v4 Wave-G + Wave-H.

Single-call entry point for the L5 runtime lane. Composes:

- **Wave-E**: emit the v4 principal-attached write record
- **Wave-F**: two-stage guardrail chokepoint (ingress + egress + guard-model)
- **Wave-B**: runtime risk-tier band selection (G-03) + A2A handoff
  validation (G-05) when applicable
- **Wave-W4**: v4 capability-token verification (identity + permissions)

This is the **end-to-end wire-in** that a v4-aware runtime-lane entry
point calls once per invocation. v3 call sites continue through the
legacy path; v4 call sites get a single-shape `RuntimeLaneDecision`.

Adoption path — the runtime lane entry point picks ONE of:

    # v3 (legacy): existing path, unchanged
    ...

    # v4 (new): one composed decision
    from agentic_core.L5_safety.identity.runtime_entry import (
        evaluate_runtime_lane,
    )
    decision = evaluate_runtime_lane(
        token=v4_token,
        action_required_rung="mutate",
        action_connector_id="...",
        touches_write_surface=True,
        ingress_outcomes=[...],
        egress_outcomes=[...],
        guard_model_outcome=None,
        handoff_target=None,  # set if this invocation is an A2A handoff
    )
    if decision.final_action != "allow":
        raise RuntimeLaneRejected(decision)

Reference:
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md (Runtime Lane)
  - docs/contracts/identity_propagation.md §5 (Composition)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from agentic_core.interfaces.principal_chain_types import PermissionLadderRung
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.guardrail_adapter import (
    ChokepointV4Result,
    run_chokepoint_v4,
)
from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome
from agentic_core.L5_safety.identity.principal_verifier import (
    VerificationResult,
    VerificationStatus,
    verify_v4_token,
)
from agentic_core.L5_safety.identity.runtime_rails import (
    AgentRegistryRecord,
    HandoffValidationResult,
    RiskTierDecision,
    select_runtime_band,
    validate_handoff,
)


@dataclass(frozen=True)
class RuntimeLaneDecision:
    """Composed runtime-lane decision for a single v4 invocation.

    `final_action` = most restrictive across:
      - verification (fail / step_up / pass)
      - chokepoint (allow / remediate / reject)
      - handoff validation (allow / reject) — only when handoff_target is set

    `final_action` values (broader than chokepoint alone):
      - "allow"       → proceed
      - "step_up"     → HITL exit-control required to re-issue at higher rung
      - "remediate"   → safe-to-remediate content rewrite
      - "reject"      → terminate; hard constraint violation
    """

    verification: VerificationResult
    risk_tier: RiskTierDecision
    chokepoint: ChokepointV4Result
    handoff: HandoffValidationResult | None
    final_action: str

    def to_dict(self) -> dict[str, object]:
        return {
            "chokepoint": self.chokepoint.to_dict(),
            "final_action": self.final_action,
            "handoff": self.handoff.to_dict() if self.handoff else None,
            "risk_tier": self.risk_tier.to_dict(),
            "verification": self.verification.to_dict(),
        }


class RuntimeLaneRejected(Exception):
    """Raised when the runtime lane's composed decision is not 'allow'.

    Carries the full `RuntimeLaneDecision` on `.decision` so the caller
    can inspect the precise failure path for audit.
    """

    def __init__(self, decision: RuntimeLaneDecision):
        super().__init__(
            f"RuntimeLaneRejected: final_action={decision.final_action}",
        )
        self.decision = decision


def evaluate_runtime_lane(
    *,
    token: CapabilityTokenV4Artifact,
    action_required_rung: PermissionLadderRung,
    ingress_outcomes: Sequence[GuardrailOutcome] = (),
    egress_outcomes: Sequence[GuardrailOutcome] = (),
    guard_model_outcome: GuardrailOutcome | None = None,
    action_connector_id: str | None = None,
    action_tool_id: str | None = None,
    connector_is_registered: bool = True,
    touches_write_surface: bool = False,
    current_semantic_tick: int | None = None,
    expected_plan_digest: str | None = None,
    revoked_token_ids: Sequence[str] = (),
    active_policy_version: str | None = None,
    handoff_target: AgentRegistryRecord | None = None,
    handoff_scope_added: Sequence[str] = (),
    handoff_scope_removed: Sequence[str] = (),
) -> RuntimeLaneDecision:
    """Evaluate the v4 runtime lane in a single call.

    Fails open (no mutation); the caller MUST inspect `final_action` and
    short-circuit the invocation if it is anything other than `"allow"`.
    """
    # Step 1: identity + permission verification (Wave-W4)
    verification = verify_v4_token(
        token=token,
        action_required_rung=action_required_rung,
        action_connector_id=action_connector_id,
        action_tool_id=action_tool_id,
        current_semantic_tick=current_semantic_tick,
        expected_plan_digest=expected_plan_digest,
        revoked_token_ids=revoked_token_ids,
        active_policy_version=active_policy_version,
    )

    # Step 2: risk-tier band selection (Wave-B G-03)
    risk_tier = select_runtime_band(
        token=token,
        action_required_rung=action_required_rung,
        action_connector_id=action_connector_id,
        connector_is_registered=connector_is_registered,
        touches_write_surface=touches_write_surface,
    )

    # Step 3: two-stage guardrail chokepoint (Wave-F)
    chokepoint = run_chokepoint_v4(
        ingress_outcomes=ingress_outcomes,
        egress_outcomes=egress_outcomes,
        guard_model_outcome=guard_model_outcome,
    )

    # Step 4: optional A2A handoff validation (Wave-B G-05)
    handoff: HandoffValidationResult | None = None
    if handoff_target is not None:
        handoff = validate_handoff(
            source_chain=token.principal_chain,
            target_agent=handoff_target,
            requested_scope_added=handoff_scope_added,
            requested_scope_removed=handoff_scope_removed,
            risk_tier_band=risk_tier.runtime_band,
        )

    # Compose final_action — most restrictive wins
    # Precedence: reject > step_up > remediate > allow
    order = {"allow": 0, "remediate": 1, "step_up": 2, "reject": 3}

    verification_rank = {
        VerificationStatus.PASS: order["allow"],
        VerificationStatus.STEP_UP_REQUIRED: order["step_up"],
        VerificationStatus.FAIL: order["reject"],
    }[verification.status]

    chokepoint_rank = order[chokepoint.final_action]

    handoff_rank = order["reject"] if handoff is not None and not handoff.allow else order["allow"]

    final_rank = max(verification_rank, chokepoint_rank, handoff_rank)
    final_action = next(a for a, r in order.items() if r == final_rank)

    return RuntimeLaneDecision(
        verification=verification,
        risk_tier=risk_tier,
        chokepoint=chokepoint,
        handoff=handoff,
        final_action=final_action,
    )


__all__ = [
    "RuntimeLaneDecision",
    "RuntimeLaneRejected",
    "evaluate_runtime_lane",
]
