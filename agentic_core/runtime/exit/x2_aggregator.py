"""AG-5 X2 aggregation — X1CheckoutResult → X2AggregationResult."""

from __future__ import annotations

from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult, X1Verdict
from agentic_core.runtime.exit.exit_disposition import X3A_DENY_REROUTE, X3B_ESCALATE_HITL, X3D_ALLOW_FINISH
from agentic_core.runtime.exit.x2_aggregation_result import X2AggregationResult


def aggregate_x1_for_exit(checkout: X1CheckoutResult) -> X2AggregationResult:
    """Derive disposition candidate from structured X1 checkout."""
    if checkout.is_overall_pass():
        return X2AggregationResult(
            disposition_candidate=X3D_ALLOW_FINISH,
            decisive_failures=(),
            unknown_material_fields=(),
            policy_ref="ag5-x2-default-policy",
            emits_final_x3=False,
        )

    blocker = checkout.first_blocking_gate()
    unknown_fields: tuple[str, ...] = ()
    if blocker is not None and blocker.verdict == X1Verdict.UNKNOWN:
        unknown_fields = (f"{blocker.gate_id}:UNKNOWN",)

    if unknown_fields:
        return X2AggregationResult(
            disposition_candidate=X3B_ESCALATE_HITL,
            decisive_failures=(f"{blocker.gate_id}:{blocker.verdict.value}",) if blocker else (),
            unknown_material_fields=unknown_fields,
            policy_ref="ag5-x2-unknown-material",
            emits_final_x3=False,
        )

    gate = blocker.gate_id if blocker else "X1?"
    ver = blocker.verdict.value if blocker else "FAIL"
    return X2AggregationResult(
        disposition_candidate=X3A_DENY_REROUTE,
        decisive_failures=(f"{gate}:{ver}",),
        unknown_material_fields=(),
        policy_ref="ag5-x2-deny-policy",
        emits_final_x3=False,
        deterministic_blocked=True,
    )


__all__ = ["aggregate_x1_for_exit"]
