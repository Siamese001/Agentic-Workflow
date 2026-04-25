"""Runtime Entry + Unified Sweep — L5 v4 Wave-L wire-in.

Extends `evaluate_runtime_lane` (Wave G+H) with the unified pre-L5 sweep
(Wave-K) so callers who migrate to this entry point get registry-digest
drift + data-authority drift gates in addition to the Wave G+H gates
(identity, risk-tier, chokepoint, handoff).

Additive: the original `evaluate_runtime_lane` remains untouched. Callers
opt in by switching to `evaluate_runtime_lane_with_sweep()`.

Precedence for `final_action` (most restrictive wins):
    reject  >  step_up  >  remediate  >  allow

Registry drift and data-authority drift both route to `step_up` (they are
remediable by a policy-bump + re-issue, not a hard deny).

Adoption path:

    from agentic_core.L5_safety.identity.runtime_entry_sweep import (
        evaluate_runtime_lane_with_sweep,
        RuntimeLaneRejected,
    )
    decision = evaluate_runtime_lane_with_sweep(
        token=v4_token,
        action_required_rung="mutate",
        action_connector_id="claude_mcp",
        touches_write_surface=True,
        ingress_outcomes=[...],
        egress_outcomes=[...],
    )
    if decision.final_action != "allow":
        raise RuntimeLaneRejected(decision)

Reference:
  - runtime_entry.py (Wave G+H base)
  - pre_l5_sweep.py (Wave-K composite)
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
from agentic_core.L5_safety.identity.pre_l5_sweep import (
    PreL5SweepResult,
    run_pre_l5_sweep,
)
from agentic_core.L5_safety.identity.principal_verifier import VerificationStatus
from agentic_core.L5_safety.identity.runtime_rails import (
    AgentRegistryRecord,
    HandoffValidationResult,
    RiskTierDecision,
    select_runtime_band,
    validate_handoff,
)

_ACTION_ORDER: dict[str, int] = {"allow": 0, "remediate": 1, "step_up": 2, "reject": 3}
_VERIFICATION_RANK: dict[VerificationStatus, int] = {
    VerificationStatus.PASS: 0,
    VerificationStatus.STEP_UP_REQUIRED: 2,
    VerificationStatus.FAIL: 3,
}


@dataclass(frozen=True)
class RuntimeLaneDecisionWithSweep:
    """Runtime-lane decision that includes the unified pre-L5 sweep result.

    Superset of `RuntimeLaneDecision` (Wave G+H) with `sweep` embedded and
    `final_action` recomputed to factor registry/data-authority drift.
    """

    sweep: PreL5SweepResult
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
            "sweep": self.sweep.to_dict(),
        }


class RuntimeLaneRejected(Exception):
    """Raised when the composed final_action is not 'allow'."""

    def __init__(self, decision: RuntimeLaneDecisionWithSweep):
        super().__init__(
            f"RuntimeLaneRejected: final_action={decision.final_action}",
        )
        self.decision = decision


def evaluate_runtime_lane_with_sweep(
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
) -> RuntimeLaneDecisionWithSweep:
    """Runtime lane entry with the unified pre-L5 sweep engaged."""
    # Step 1: unified pre-L5 sweep (identity + registry + data-authority)
    sweep = run_pre_l5_sweep(
        token=token,
        action_required_rung=action_required_rung,
        action_connector_id=action_connector_id,
        action_tool_id=action_tool_id,
        current_semantic_tick=current_semantic_tick,
        expected_plan_digest=expected_plan_digest,
        revoked_token_ids=revoked_token_ids,
        active_policy_version=active_policy_version,
    )

    # Step 2: risk-tier band selection
    risk_tier = select_runtime_band(
        token=token,
        action_required_rung=action_required_rung,
        action_connector_id=action_connector_id,
        connector_is_registered=connector_is_registered,
        touches_write_surface=touches_write_surface,
    )

    # Step 3: two-stage guardrail chokepoint
    chokepoint = run_chokepoint_v4(
        ingress_outcomes=ingress_outcomes,
        egress_outcomes=egress_outcomes,
        guard_model_outcome=guard_model_outcome,
    )

    # Step 4: optional A2A handoff validation
    handoff: HandoffValidationResult | None = None
    if handoff_target is not None:
        handoff = validate_handoff(
            source_chain=token.principal_chain,
            target_agent=handoff_target,
            requested_scope_added=handoff_scope_added,
            requested_scope_removed=handoff_scope_removed,
            risk_tier_band=risk_tier.runtime_band,
        )

    # Compose final_action — most restrictive wins across:
    #   verification status, registry drift, data-authority drift,
    #   chokepoint action, handoff validation.
    ranks: list[int] = [_VERIFICATION_RANK[sweep.verification.status]]
    if not sweep.registry_match:
        ranks.append(_ACTION_ORDER["step_up"])
    if not sweep.data_authority_all_match:
        ranks.append(_ACTION_ORDER["step_up"])
    ranks.append(_ACTION_ORDER[chokepoint.final_action])
    if handoff is not None and not handoff.allow:
        ranks.append(_ACTION_ORDER["reject"])

    final_rank = max(ranks)
    final_action = next(a for a, r in _ACTION_ORDER.items() if r == final_rank)

    return RuntimeLaneDecisionWithSweep(
        sweep=sweep,
        risk_tier=risk_tier,
        chokepoint=chokepoint,
        handoff=handoff,
        final_action=final_action,
    )


__all__ = [
    "RuntimeLaneDecisionWithSweep",
    "RuntimeLaneRejected",
    "evaluate_runtime_lane_with_sweep",
]
