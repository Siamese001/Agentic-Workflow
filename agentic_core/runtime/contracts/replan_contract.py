"""Replan re-entry contract for the L1 → [5] EXIT EVAL feedback loop.

Shared across routing (L0), cognition (L1), orchestration (L3) and the exit
gate ([5]).  When L2/C0/L3 return evidence that invalidates a declared
assumption on an L1 plan, the exit gate MAY emit a ``ReplanRequest`` that
routes back to L1.

Scope:
- Pure, synchronous primitives (``TypedDict`` + stateless validator).
- No layer-specific dependencies, no I/O, no telemetry side effects.
- Stable public contract — treat constants as a closed enum.

Invariants (enforced by :func:`validate_replan_request`):
- ``replan_depth`` is bounded by :data:`MAX_REPLAN_DEPTH` (ADR-043 §Risks
  R3 hard cap).  Exceeding it forces the caller to escalate to BEST-EFFORT
  or ABSTAIN, not another replan.
- ``residual_budget_ms`` and ``residual_refinements`` must be non-negative.
- ``original_plan_id`` and ``failed_assumption`` must be non-empty strings.
"""

from __future__ import annotations

from typing import Literal, TypedDict

MAX_REPLAN_DEPTH: int = 3
"""Hard cap on replan loops (ADR-043 §Risks R3).

The planner MUST escalate to ``BEST_EFFORT`` or ``ABSTAIN`` once
``replan_depth >= MAX_REPLAN_DEPTH``.  Enforced by
:func:`validate_replan_request`.
"""

# Stable exit-branch strings consumed by [5] EXIT EVAL.  Treat as a closed
# enum aligned with v33 §2 T3 exit branches.
REPLAN_BRANCH_ACCEPT: Literal["accept"] = "accept"
REPLAN_BRANCH_RETRY: Literal["retry"] = "retry"
REPLAN_BRANCH_BEST_EFFORT: Literal["best_effort"] = "best_effort"
REPLAN_BRANCH_ABSTAIN: Literal["abstain"] = "abstain"


class ReplanContractViolation(ValueError):
    """Raised when a ReplanRequest fails its structural or policy invariants."""


class ReplanRequest(TypedDict):
    """Serializable shape emitted by [5] EXIT EVAL when re-entering L1.

    Fields are all primitives or JSON-safe values so the dict round-trips
    through ``json.dumps`` / ``json.loads`` without transformation.

    Fields:
        original_plan_id: The ``plan_id`` of the L1PlanContract that is
            being re-planned.
        failed_assumption: The ``Assumption.statement`` that observed
            evidence contradicted.  Free-form string; callers SHOULD use
            the exact text from the original contract.
        observed_evidence: Short human-readable summary of what the exit
            gate observed (tool result, anomaly, etc.).
        residual_budget_ms: Remaining wall-clock budget for the replan.
            Must be >= 0.  When zero, the exit gate MUST route to
            ``best_effort`` or ``abstain`` rather than re-enter L1.
        residual_refinements: Remaining refinement-loop iterations allowed
            inside the new plan's thinking desk.  Must be >= 0.
        replan_depth: How many replans have already occurred on this
            logical request chain (0 = first replan).  Capped by
            :data:`MAX_REPLAN_DEPTH`.
    """

    original_plan_id: str
    failed_assumption: str
    observed_evidence: str
    residual_budget_ms: int
    residual_refinements: int
    replan_depth: int


def validate_replan_request(req: ReplanRequest) -> None:
    """Raise :class:`ReplanContractViolation` if the request is malformed.

    Structural checks: required fields present, non-empty strings,
    non-negative counters.  Policy check: ``replan_depth <
    MAX_REPLAN_DEPTH``.

    Args:
        req: A :class:`ReplanRequest` dict.

    Raises:
        ReplanContractViolation: If any invariant fails.
    """
    required = (
        "original_plan_id",
        "failed_assumption",
        "observed_evidence",
        "residual_budget_ms",
        "residual_refinements",
        "replan_depth",
    )
    for key in required:
        if key not in req:
            raise ReplanContractViolation(f"ReplanRequest missing required field: {key}")

    for key in ("original_plan_id", "failed_assumption", "observed_evidence"):
        val = req[key]  # type: ignore[literal-required]
        if not isinstance(val, str) or not val.strip():
            raise ReplanContractViolation(f"{key} must be a non-empty string.")

    for key in ("residual_budget_ms", "residual_refinements", "replan_depth"):
        val = req[key]  # type: ignore[literal-required]
        if not isinstance(val, int) or val < 0:
            raise ReplanContractViolation(f"{key} must be a non-negative int, got {val!r}")

    if req["replan_depth"] >= MAX_REPLAN_DEPTH:
        raise ReplanContractViolation(
            f"replan_depth {req['replan_depth']} exceeds cap {MAX_REPLAN_DEPTH}; "
            "caller must escalate to best_effort or abstain, not replan."
        )


def advance_replan_depth(req: ReplanRequest) -> ReplanRequest:
    """Return a new ReplanRequest with ``replan_depth`` incremented.

    Raises :class:`ReplanContractViolation` if advancing would exceed
    :data:`MAX_REPLAN_DEPTH`.  Callers SHOULD call this when they decide
    to re-enter L1 rather than hand-editing the dict.
    """
    new_depth = req["replan_depth"] + 1
    if new_depth >= MAX_REPLAN_DEPTH:
        raise ReplanContractViolation(
            f"advance_replan_depth would reach cap {MAX_REPLAN_DEPTH}; escalate instead."
        )
    # dict() not spread because TypedDict does not support spread at runtime
    updated: ReplanRequest = ReplanRequest(
        original_plan_id=req["original_plan_id"],
        failed_assumption=req["failed_assumption"],
        observed_evidence=req["observed_evidence"],
        residual_budget_ms=req["residual_budget_ms"],
        residual_refinements=req["residual_refinements"],
        replan_depth=new_depth,
    )
    return updated


__all__ = [
    "MAX_REPLAN_DEPTH",
    "REPLAN_BRANCH_ABSTAIN",
    "REPLAN_BRANCH_ACCEPT",
    "REPLAN_BRANCH_BEST_EFFORT",
    "REPLAN_BRANCH_RETRY",
    "ReplanContractViolation",
    "ReplanRequest",
    "advance_replan_depth",
    "validate_replan_request",
]
