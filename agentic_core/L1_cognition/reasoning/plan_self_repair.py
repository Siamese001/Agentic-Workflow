"""V6 Self-Repair Loop — v5 doctrine § V6.

Doctrine reference: ``02_L1_Reasoning_Plan_Generation_v5.md`` § V6 SELF-REPAIR LOOP.

When semantic validation (V1-V5 + V3A) returns FAIL or WARN, this module
attempts ONE bounded refinement step that produces a new plan with the
specific issues addressed. The doctrine says::

    refine once or twice inside L1; if still weak, mark
    clarify / abstain / fallback; do not spin indefinitely.

This module is **deterministic** — no LLM calls, no retrieval, no tool use.
Each repair rule is an idempotent transformer ``plan -> plan'`` keyed off a
finding string. After the configured cap (default 2), the planner is
forced to mark ``ClarifyOrAbstainMarker.FALLBACK``.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any

from agentic_core.L1_cognition.enforcement.plan_semantic_validators import (
    GateOutcome,
    PlanValidationOutcome,
    validate_plan_semantically,
)
from agentic_core.L1_cognition.types.intent_frame_types import IntentFrame
from agentic_core.L1_cognition.types.plan_bundle_types import PlanBundle
from agentic_core.L1_cognition.types.plan_contract_types import (
    ClarifyOrAbstainMarker,
    EscalationHint,
    L1PlanContractV2,
    LowestViableAgency,
    ProposedRoute,
    SupportTarget,
)

__all__ = [
    "RepairAction",
    "RepairOutcome",
    "RepairResult",
    "repair_plan_once",
    "repair_plan_with_loop",
]

DEFAULT_LOOP_CAP: int = 2


class RepairAction(str, Enum):
    """Which doctrine repair rule fired during a single self-repair pass."""

    NO_ACTION_NEEDED = "no_action_needed"
    DROPPED_CONSTRAINT = "dropped_constraint_repaired"
    MISSING_OUTPUT_TARGET = "missing_output_target_repaired"
    UNSAFE_ROUTE_HINT = "unsafe_route_hint_repaired"
    UNCLEAR_SUPPORT = "unclear_support_repaired"
    OVER_BROAD_ACTION = "over_broad_action_repaired"
    MISSING_FALLBACK = "missing_fallback_repaired"
    MISSING_HITL_OR_UWG = "missing_hitl_or_uwg_repaired"
    UNNECESSARY_WORKFLOW = "unnecessary_workflow_repaired"
    EXCESSIVE_CLARIFICATION = "excessive_clarification_repaired"
    UNSUPPORTED_CERTAINTY = "unsupported_certainty_repaired"
    UNREPAIRABLE = "unrepairable_marked_for_clarify_or_abstain"


class RepairOutcome(str, Enum):
    """Loop-level outcome."""

    PASS_NO_REPAIR = "pass_no_repair"  # Validation passed first try.
    REPAIRED_TO_PASS = "repaired_to_pass"  # Loop converged to PASS.
    REPAIRED_TO_WARN = "repaired_to_warn"  # Loop converged to WARN.
    LOOP_CAPPED_FALLBACK = "loop_capped_fallback"  # Hit cap, marked FALLBACK.


@dataclass(frozen=True)
class RepairResult:
    """Result of running the V6 self-repair loop."""

    outcome: RepairOutcome
    final_plan: L1PlanContractV2
    final_validation: PlanValidationOutcome
    iterations: int
    actions: tuple = field(default_factory=tuple)  # (RepairAction, ...)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "iterations": self.iterations,
            "actions": [a.value for a in self.actions],
            "final_validation": self.final_validation.to_dict(),
        }


# ---------------------------------------------------------------------------
# Single-pass repair rules.
# ---------------------------------------------------------------------------


def _has_finding_substr(validation: PlanValidationOutcome, *needles: str, gate_id: str | None = None) -> bool:
    """True if any finding contains any of the lowercased needles."""
    for gate in validation.gates:
        if gate_id is not None and gate.gate_id != gate_id:
            continue
        for f in gate.findings:
            fl = f.lower()
            if any(n.lower() in fl for n in needles):
                return True
    return False


def repair_plan_once(
    plan: L1PlanContractV2,
    validation: PlanValidationOutcome,
    intent: IntentFrame,
    bundle: PlanBundle,
) -> tuple[L1PlanContractV2, RepairAction]:
    """Single deterministic repair pass.

    Inspects ``validation.gates`` and applies the FIRST matching repair rule.
    Rules are checked in priority order — most-impactful first — so a single
    call addresses the most serious issue and lets the next iteration
    handle any remaining ones.

    Returns:
        ``(repaired_plan, action)``. If no rule matches, returns the input
        plan unchanged with :data:`RepairAction.NO_ACTION_NEEDED`.
    """
    if not validation.has_failures() and not validation.has_warnings():
        return plan, RepairAction.NO_ACTION_NEEDED

    # 1. UNSAFE ROUTE HINT (V2 fail: WRITE without escalation_hint and no HITL trigger).
    if _has_finding_substr(validation, "potential UWG bypass", "WRITE with no escalation_hint", gate_id="V2"):
        repaired = replace(plan, escalation_hint=EscalationHint.IRREVERSIBLE)
        return repaired, RepairAction.UNSAFE_ROUTE_HINT

    # 2. MISSING HITL/UWG marker (V3A fail #7: HIGH_IMPACT without escalation).
    if _has_finding_substr(validation, "HIGH_IMPACT but no escalation_hint", gate_id="V3A"):
        repaired = replace(plan, escalation_hint=EscalationHint.HIGH_IMPACT)
        return repaired, RepairAction.MISSING_HITL_OR_UWG

    # 3. UNSUPPORTED CERTAINTY (V3A fail #8: grounding_required but support_target=NONE).
    if _has_finding_substr(validation, "support_target=NONE", gate_id="V3A"):
        repaired = replace(plan, support_target=SupportTarget.CITATION)
        return repaired, RepairAction.UNSUPPORTED_CERTAINTY

    # 4. UNCLEAR SUPPORT (V3 fail: grounding_required=True but query_spec is None).
    if _has_finding_substr(validation, "grounding_required=True but query_spec is None", gate_id="V3"):
        # Cannot synthesize a QuerySpec from nothing — escalate to FALLBACK.
        repaired = replace(
            plan,
            grounding_required=False,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.FALLBACK,
            lowest_viable_agency=LowestViableAgency.FALLBACK,
        )
        return repaired, RepairAction.UNCLEAR_SUPPORT

    # 5. OVER-BROAD ACTION (V3A fail #3: R4 with multi-step task_spec).
    if _has_finding_substr(validation, "R4 single-action route used with multi-step", gate_id="V3A"):
        repaired = replace(plan, proposed_route=ProposedRoute.R3R4_MANAGED_WORKFLOW)
        return repaired, RepairAction.OVER_BROAD_ACTION

    # 6. UNNECESSARY WORKFLOW (V3A WARN #4: R3R4_MANAGED_WORKFLOW with ≤ 1 step).
    if _has_finding_substr(validation, "MANAGED_WORKFLOW with", "1 task step", gate_id="V3A"):
        # Default down to R3 if grounding required, else R4.
        next_route = ProposedRoute.R3 if plan.grounding_required else ProposedRoute.R4
        repaired = replace(plan, proposed_route=next_route)
        return repaired, RepairAction.UNNECESSARY_WORKFLOW

    # 7. MISSING FALLBACK (V3A fail #5: R5 without reason in rationale).
    if _has_finding_substr(validation, "R5 fallback route used but published_rationale", gate_id="V3A"):
        repaired = replace(
            plan,
            published_rationale=(
                plan.published_rationale.rstrip(".")
                + ". Fallback engaged because direct completion is unsupported."
            ),
        )
        return repaired, RepairAction.MISSING_FALLBACK

    # 8. EXCESSIVE CLARIFICATION (V5 fail: ABSTAIN with multi-step task_spec).
    if _has_finding_substr(validation, "ABSTAIN but task_spec has multiple steps", gate_id="V5"):
        # Keep only the first step — abstain is supposed to be terminal.
        repaired = replace(plan, task_spec=plan.task_spec[:1])
        return repaired, RepairAction.EXCESSIVE_CLARIFICATION

    # 9. DROPPED CONSTRAINT (V1 fail: intent.goal not in published_rationale).
    if _has_finding_substr(validation, "intent.goal not referenced", gate_id="V1"):
        repaired = replace(
            plan,
            published_rationale=(
                f"planner addressing intent goal: {intent.goal}. " + plan.published_rationale
            ),
        )
        return repaired, RepairAction.DROPPED_CONSTRAINT

    # 10. MISSING OUTPUT TARGET (V1 fail: ACTION-intent + READ reversibility).
    if _has_finding_substr(
        validation, "intent requested ACTION but route_risk.reversibility=READ", gate_id="V1"
    ):
        # Read-only plan cannot satisfy an ACTION intent — fallback.
        repaired = replace(
            plan,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.FALLBACK,
            lowest_viable_agency=LowestViableAgency.FALLBACK,
        )
        return repaired, RepairAction.MISSING_OUTPUT_TARGET

    # 11. Unmatched / unrepairable — mark FALLBACK to surface to the user.
    repaired = replace(
        plan,
        clarify_or_abstain_marker=ClarifyOrAbstainMarker.FALLBACK,
        lowest_viable_agency=LowestViableAgency.FALLBACK,
    )
    return repaired, RepairAction.UNREPAIRABLE


# ---------------------------------------------------------------------------
# Bounded loop (the doctrine's V6).
# ---------------------------------------------------------------------------


def repair_plan_with_loop(
    plan: L1PlanContractV2,
    intent: IntentFrame,
    bundle: PlanBundle,
    *,
    loop_cap: int = DEFAULT_LOOP_CAP,
) -> RepairResult:
    """Run the bounded V6 self-repair loop.

    Each iteration:
      1. Run V1-V5 + V3A.
      2. If PASS → return ``REPAIRED_TO_PASS`` (or ``PASS_NO_REPAIR`` on iter 0).
      3. If FAIL/WARN → apply :func:`repair_plan_once`.
      4. After ``loop_cap`` iterations, force ``FALLBACK`` and return
         :data:`RepairOutcome.LOOP_CAPPED_FALLBACK`.

    Args:
        loop_cap: Doctrine says "refine once or twice"; default ``2`` matches.

    Hard invariant: the loop never calls a tool, never retrieves evidence,
    and terminates in at most ``loop_cap + 1`` validation passes.
    """
    if loop_cap < 0:
        raise ValueError(f"loop_cap must be non-negative, got {loop_cap}")

    actions: list[RepairAction] = []
    current_plan = plan
    current_validation = validate_plan_semantically(current_plan, intent, bundle)

    if current_validation.overall == GateOutcome.PASS:
        return RepairResult(
            outcome=RepairOutcome.PASS_NO_REPAIR,
            final_plan=current_plan,
            final_validation=current_validation,
            iterations=0,
            actions=(),
        )

    for i in range(1, loop_cap + 1):
        current_plan, action = repair_plan_once(current_plan, current_validation, intent, bundle)
        actions.append(action)
        current_validation = validate_plan_semantically(current_plan, intent, bundle)
        if current_validation.overall == GateOutcome.PASS:
            return RepairResult(
                outcome=RepairOutcome.REPAIRED_TO_PASS,
                final_plan=current_plan,
                final_validation=current_validation,
                iterations=i,
                actions=tuple(actions),
            )

    # Hit the cap.
    if current_validation.overall == GateOutcome.WARN and not current_validation.has_failures():
        # Plan is suboptimal but not unsafe — accept WARN.
        return RepairResult(
            outcome=RepairOutcome.REPAIRED_TO_WARN,
            final_plan=current_plan,
            final_validation=current_validation,
            iterations=loop_cap,
            actions=tuple(actions),
        )

    # Still failing after the cap — force FALLBACK.
    forced_plan = replace(
        current_plan,
        clarify_or_abstain_marker=ClarifyOrAbstainMarker.FALLBACK,
        lowest_viable_agency=LowestViableAgency.FALLBACK,
    )
    forced_validation = validate_plan_semantically(forced_plan, intent, bundle)
    actions.append(RepairAction.UNREPAIRABLE)
    return RepairResult(
        outcome=RepairOutcome.LOOP_CAPPED_FALLBACK,
        final_plan=forced_plan,
        final_validation=forced_validation,
        iterations=loop_cap,
        actions=tuple(actions),
    )
