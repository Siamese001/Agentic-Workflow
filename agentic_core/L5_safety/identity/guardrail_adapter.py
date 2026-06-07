"""Guardrail Bank Wire-In Adapter — L5 v4 Wave-F.

Bridges the existing `PolicyValidationChokepoint` surface to the v4
layered guardrail bank (Wave-A). Existing chokepoint callers continue to
work unchanged; v4-aware callers use `run_chokepoint_v4` to get a
principal-attributed, two-layer, egress-inspected result in one call.

Adoption path:

    # BEFORE (v3): existing chokepoint returns a single verdict
    # AFTER  (v4): one import; returns structured GuardrailBankVerdict
    from agentic_core.L5_safety.identity.guardrail_adapter import (
        run_chokepoint_v4,
    )
    result = run_chokepoint_v4(
        ingress_outcomes=[...],      # v4 bank outcomes from per-family validators
        egress_outcomes=[...],       # v4 bank outcomes for post-LLM response
        guard_model_outcome=None,    # optional G-20 second-model review
    )

Invariants:
- Ingress and egress stages produce independent `GuardrailBankVerdict`s.
- Egress + optional guard-model compose into an `EgressInspectionResult`
  whose `final_action` is the strictly most-restrictive of the two.
- G-15 enforcement is preserved: hard_constraint + remediate raises at
  outcome construction (Wave-A invariant).

Reference:
  - agentic_core/L5_safety/identity/guardrail_bank.py (Wave-A)
  - docs/reference/00_L5_Policy_Plane/guardrail_families.md
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from agentic_core.L5_safety.identity.guardrail_bank import (
    EgressInspectionResult,
    GuardrailBankVerdict,
    GuardrailOutcome,
    compose_egress_inspection,
    resolve_bank_verdict,
)


@dataclass(frozen=True)
class ChokepointV4Result:
    """Composed result of a v4 chokepoint pass.

    `final_action` is the strictly most-restrictive across ingress bank +
    egress bank + optional guard-model.
    """

    ingress_verdict: GuardrailBankVerdict
    egress_inspection: EgressInspectionResult
    final_action: str  # "allow" | "remediate" | "reject"

    def to_dict(self) -> dict[str, object]:
        return {
            "egress_inspection": self.egress_inspection.to_dict(),
            "final_action": self.final_action,
            "ingress_verdict": self.ingress_verdict.to_dict(),
        }


def run_chokepoint_v4(
    *,
    ingress_outcomes: Sequence[GuardrailOutcome],
    egress_outcomes: Sequence[GuardrailOutcome],
    guard_model_outcome: GuardrailOutcome | None = None,
) -> ChokepointV4Result:
    """Run the v4 two-stage chokepoint (ingress + egress + optional guard model).

    Deterministic. No I/O. All guardrail evaluations are produced upstream
    by concrete family validators; this adapter only composes them.
    """
    ingress_verdict = resolve_bank_verdict("ingress", tuple(ingress_outcomes))
    egress_verdict = resolve_bank_verdict("egress", tuple(egress_outcomes))
    egress_inspection = compose_egress_inspection(
        egress_verdict,
        guard_model_outcome,
    )

    # final_action = most restrictive of ingress + egress_inspection
    order = {"allow": 0, "remediate": 1, "reject": 2}
    ingress_rank = order[ingress_verdict.verdict]
    egress_rank = order[egress_inspection.final_action]
    rank = max(ingress_rank, egress_rank)
    final_action = next(a for a, r in order.items() if r == rank)

    return ChokepointV4Result(
        ingress_verdict=ingress_verdict,
        egress_inspection=egress_inspection,
        final_action=final_action,
    )


__all__ = ["ChokepointV4Result", "run_chokepoint_v4"]
