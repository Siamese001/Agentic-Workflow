"""HITL Policy ↔ V4 Sweep Bridge — closes hitl_policy deferred scope.

Maps a Wave-K `PreL5SweepResult` (or a Wave-L `RuntimeLaneDecisionWithSweep`)
to the runtime HITL class that should handle any non-allow outcome.

Keeps the existing HITL policy plane (`hitl_policy.py`, `hitl_classes.py`)
completely untouched. The bridge is the translation layer between the v4
sweep world and the existing HITL enum/ClassPolicy machinery.

Mapping rules (deterministic, ordered):

    1. Identity verification FAIL            → POLICY_OVERRIDE
    2. Identity verification STEP_UP         → POLICY_OVERRIDE
    3. Registry-digest drift                 → POLICY_OVERRIDE  (needs re-issue)
    4. Data-authority drift                  → REGULATED        (data lineage)
    5. Chokepoint REJECT                     → SAFETY
    6. Chokepoint REMEDIATE (no other gates) → LOW_CONFIDENCE
    7. Handoff denial                        → POLICY_OVERRIDE
    8. all_pass                              → None (no HITL needed)

First-match wins — a single denial can only produce one class. The
ordering puts hard rejections before soft ones so the most restrictive
HITL class wins.

Adoption:
    from agentic_core.L5_safety.identity.hitl_sweep_bridge import (
        classify_sweep_as_hitl_class,
    )
    hitl_class = classify_sweep_as_hitl_class(decision_with_sweep)
    if hitl_class is not None:
        policy = load_policy()
        approver = resolve_approver_pool(hitl_class, ...)
        timeout = policy.classes[hitl_class].timeout_s

Reference:
  - hitl_policy.py (existing HITL plane, UNCHANGED)
  - hitl_classes.py (existing HITL enum, UNCHANGED)
  - pre_l5_sweep.py (Wave-K source of PreL5SweepResult)
  - runtime_entry_sweep.py (Wave-L source of RuntimeLaneDecisionWithSweep)
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from agentic_core.L5_safety.identity.pre_l5_sweep import PreL5SweepResult
from agentic_core.L5_safety.identity.principal_verifier import VerificationStatus
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
)


def classify_sweep_as_hitl_class(
    decision_or_sweep: RuntimeLaneDecisionWithSweep | PreL5SweepResult,
) -> HitlClass | None:
    """Return the HITL class that should handle a non-allow sweep outcome.

    Returns None if the sweep / decision passed all gates (no HITL needed).
    """
    if isinstance(decision_or_sweep, RuntimeLaneDecisionWithSweep):
        sweep = decision_or_sweep.sweep
        handoff = decision_or_sweep.handoff
        chokepoint_action = decision_or_sweep.chokepoint.final_action
    else:
        sweep = decision_or_sweep
        handoff = None
        chokepoint_action = "allow"

    # Rule 1-2: identity verification fail / step_up
    if sweep.verification.status is VerificationStatus.FAIL:
        return HitlClass.POLICY_OVERRIDE
    if sweep.verification.status is VerificationStatus.STEP_UP_REQUIRED:
        return HitlClass.POLICY_OVERRIDE

    # Rule 3: registry-digest drift
    if not sweep.registry_match:
        return HitlClass.POLICY_OVERRIDE

    # Rule 4: data-authority drift
    if not sweep.data_authority_all_match:
        return HitlClass.REGULATED

    # Rule 5: chokepoint reject
    if chokepoint_action == "reject":
        return HitlClass.SAFETY

    # Rule 6: chokepoint remediate (no other gate fired)
    if chokepoint_action == "remediate":
        return HitlClass.LOW_CONFIDENCE

    # Rule 7: handoff denial
    if handoff is not None and not handoff.allow:
        return HitlClass.POLICY_OVERRIDE

    # Rule 8: all_pass — no HITL needed
    return None


__all__ = ["classify_sweep_as_hitl_class"]
