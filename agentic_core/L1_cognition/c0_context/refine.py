"""C0.6 controlled refinement loop with allowed/disallowed enforcement.

Spec: ``docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md``
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.L1_cognition.c0_context.types import (
    DISALLOWED_REFINEMENTS,
    RefineTactic,
    RetrievalPlan,
    SupportStatus,
)


class DisallowedRefinementError(RuntimeError):
    """Raised when caller attempts a refinement banned by the spec."""


class RefinementBudgetExhaustedError(RuntimeError):
    """Raised when caller attempts refinement after the budget is spent."""


@dataclass(frozen=True)
class RefinementAttempt:
    """One attempted refinement and its outcome."""

    tactic: RefineTactic
    rationale: str
    succeeded: bool
    new_status: SupportStatus


@dataclass
class RefineLoopController:
    """Stateful controller per C0 invocation; one attempt budget."""

    plan: RetrievalPlan
    attempts_made: int = 0
    history: list[RefinementAttempt] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.history is None:
            object.__setattr__(self, "history", [])

    @property
    def max_refine_attempts(self) -> int:
        return self.plan.bounds.get("max_refine_attempts", 0)

    @property
    def can_refine(self) -> bool:
        return self.attempts_made < self.max_refine_attempts

    def request_refinement(
        self,
        tactic: RefineTactic,
        *,
        rationale: str,
        current_status: SupportStatus,
    ) -> None:
        """Validate the tactic and record an attempt slot.

        Raises:
            DisallowedRefinementError: When ``rationale`` describes a behavior
                in :data:`DISALLOWED_REFINEMENTS`, or when entry conditions
                from the spec are violated.
            RefinementBudgetExhaustedError: When budget is gone.
        """
        # Entry conditions — spec C0.6: WEAK / CONFLICTED / EMPTY only.
        if current_status not in {
            SupportStatus.WEAK,
            SupportStatus.WEAK_WITH_CAVEATS,
            SupportStatus.CONFLICTED,
            SupportStatus.EMPTY,
        }:
            raise DisallowedRefinementError(
                f"refinement disallowed when status={current_status.value} "
                "(entry conditions: WEAK / WEAK_WITH_CAVEATS / CONFLICTED / EMPTY)",
            )
        if not self.can_refine:
            raise RefinementBudgetExhaustedError(
                f"already attempted {self.attempts_made} refinements "
                f"(max={self.max_refine_attempts})",
            )
        # Disallowed-rationale check — banned behaviors from spec.
        rationale_lc = rationale.lower()
        for banned in DISALLOWED_REFINEMENTS:
            if banned.replace("_", " ") in rationale_lc or banned in rationale_lc:
                raise DisallowedRefinementError(
                    f"refinement rationale describes disallowed behavior: {banned}",
                )

    def record_attempt(self, attempt: RefinementAttempt) -> None:
        """Persist a completed refinement attempt."""
        self.attempts_made += 1
        self.history.append(attempt)


def is_refinement_allowed(tactic: RefineTactic) -> bool:
    """Per spec C0.6 — every RefineTactic enum value is allowed.

    The disallowed list lives in DISALLOWED_REFINEMENTS as behavioral
    descriptions, not enum values. This function is a sanity wrapper.
    """
    return isinstance(tactic, RefineTactic)


__all__ = [
    "DisallowedRefinementError",
    "RefineLoopController",
    "RefinementAttempt",
    "RefinementBudgetExhaustedError",
    "is_refinement_allowed",
]
