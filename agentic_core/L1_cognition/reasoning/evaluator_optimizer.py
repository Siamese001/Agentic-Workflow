"""Evaluator-optimizer loop primitive for the L1 Thinking Desk (ADR-043).

Implements the Anthropic-style evaluator-optimizer pattern called for in
``agentic_process_mapping_v33.md`` §2 T3: draft → critique → refine until
ACCEPT or budget exhausted.

This module is a **pure primitive**.  It has no I/O, no telemetry side
effects, and no dependency on any LLM.  Callers inject:
  - ``draft_fn``   — produces (or refines) a draft given an optional critique
  - ``critique_fn`` — evaluates a draft and returns a :class:`Critique`

The loop terminates on any of:
  - Critic emits ``accept`` verdict                       → LoopOutcome.ACCEPT
  - ``refinements_used >= max_refinements``                → LoopOutcome.REFINE_EXHAUSTED
  - ``clock_provider() - start >= wall_clock_ms_cap``      → LoopOutcome.BUDGET_EXHAUSTED
  - ``token_usage_accumulator >= token_cap``               → LoopOutcome.BUDGET_EXHAUSTED
  - Critic emits ``escalate`` verdict                      → LoopOutcome.ESCALATE

The primitive pairs with :class:`agentic_core.L1_cognition.types.plan_contract_types.PlannerTelemetry`:
the loop returns a :class:`LoopResult` whose fields map 1:1 onto the
telemetry dataclass so the chokepoint can emit it without transformation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Literal, Optional


class LoopOutcome(str, Enum):
    """Terminal state of the evaluator-optimizer loop."""

    ACCEPT = "ACCEPT"
    REFINE_EXHAUSTED = "REFINE_EXHAUSTED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    ESCALATE = "ESCALATE"


CriticVerdict = Literal["accept", "refine", "escalate"]


@dataclass(frozen=True)
class Critique:
    """A single critic pass result.

    Fields:
        verdict: One of ``"accept"`` | ``"refine"`` | ``"escalate"``.
        reason: Human-readable justification for the verdict.
        token_delta: Tokens consumed by this critique pass (>= 0).
    """

    verdict: CriticVerdict
    reason: str
    token_delta: int = 0


@dataclass(frozen=True)
class DraftResult:
    """A single draft pass result.

    Fields:
        draft: Arbitrary caller-defined draft object (e.g. a plan dict,
            a ``L1PlanContractV2``, a string).  Type is intentionally
            loose so the primitive stays pure.
        token_delta: Tokens consumed by this draft pass (>= 0).
    """

    draft: Any
    token_delta: int = 0


@dataclass(frozen=True)
class LoopBudget:
    """Iteration and resource caps for the loop.

    All fields must be non-negative.  A value of 0 means "no loop" for the
    corresponding cap; the loop will exit immediately with
    ``REFINE_EXHAUSTED`` or ``BUDGET_EXHAUSTED`` before the first critic
    pass.

    Defaults chosen to match ADR-043 §Open Questions default placeholders
    (1 refinement; 30s wall clock; 10k tokens) — callers SHOULD override.
    """

    max_refinements: int = 1
    wall_clock_ms_cap: int = 30_000
    token_cap: int = 10_000

    def __post_init__(self) -> None:
        for fname in ("max_refinements", "wall_clock_ms_cap", "token_cap"):
            val = getattr(self, fname)
            if not isinstance(val, int) or val < 0:
                raise ValueError(f"{fname} must be a non-negative int, got {val!r}")


@dataclass(frozen=True)
class LoopResult:
    """Terminal state returned by :func:`run_evaluator_optimizer_loop`.

    ``refinements_used``, ``wall_clock_ms``, ``token_usage`` and
    ``critic_iterations`` map 1:1 onto
    :class:`PlannerTelemetry` so the chokepoint can emit telemetry with no
    transformation.
    """

    outcome: LoopOutcome
    final_draft: Any
    final_critique: Optional[Critique]
    refinements_used: int
    wall_clock_ms: int
    token_usage: int
    critic_iterations: int
    history: tuple = field(default=())


def _default_clock_ms() -> int:
    """Monotonic clock in milliseconds — injected for test determinism."""
    return int(time.monotonic() * 1000)


def run_evaluator_optimizer_loop(
    *,
    draft_fn: Callable[[Optional[Critique]], DraftResult],
    critique_fn: Callable[[Any], Critique],
    budget: LoopBudget,
    clock_ms: Callable[[], int] = _default_clock_ms,
) -> LoopResult:
    """Run the evaluator-optimizer loop until ACCEPT or a cap is hit.

    Contract:
      - Always runs at least one draft pass.
      - Runs at most one critique pass per draft.
      - Never mutates caller state; all telemetry is returned on LoopResult.
      - Deterministic under a fixed ``clock_ms``.

    Args:
        draft_fn: ``(prior_critique | None) -> DraftResult``.  Called once
            for the initial draft (``prior_critique=None``), then once per
            refinement with the most recent critique.
        critique_fn: ``(draft) -> Critique``.  Called once per draft pass.
        budget: :class:`LoopBudget` with max_refinements / wall clock /
            token caps.
        clock_ms: Zero-arg callable returning monotonic ms.  Defaults to
            ``time.monotonic()``; override for tests.

    Returns:
        :class:`LoopResult` summarising the terminal state.
    """
    start_ms = clock_ms()
    token_usage = 0
    critic_iterations = 0
    refinements_used = 0
    history: list = []

    # Initial draft (always runs).
    first = draft_fn(None)
    token_usage += max(0, first.token_delta)
    current_draft = first.draft

    # Budget-exhausted check BEFORE first critique so a zero budget exits
    # cleanly.
    def _budget_exhausted() -> bool:
        if budget.wall_clock_ms_cap > 0 and (clock_ms() - start_ms) >= budget.wall_clock_ms_cap:
            return True
        if budget.token_cap > 0 and token_usage >= budget.token_cap:
            return True
        return False

    if _budget_exhausted():
        return LoopResult(
            outcome=LoopOutcome.BUDGET_EXHAUSTED,
            final_draft=current_draft,
            final_critique=None,
            refinements_used=refinements_used,
            wall_clock_ms=clock_ms() - start_ms,
            token_usage=token_usage,
            critic_iterations=critic_iterations,
            history=tuple(history),
        )

    # Critique initial draft.
    critique = critique_fn(current_draft)
    token_usage += max(0, critique.token_delta)
    critic_iterations += 1
    history.append(critique)

    if critique.verdict == "accept":
        return LoopResult(
            outcome=LoopOutcome.ACCEPT,
            final_draft=current_draft,
            final_critique=critique,
            refinements_used=refinements_used,
            wall_clock_ms=clock_ms() - start_ms,
            token_usage=token_usage,
            critic_iterations=critic_iterations,
            history=tuple(history),
        )
    if critique.verdict == "escalate":
        return LoopResult(
            outcome=LoopOutcome.ESCALATE,
            final_draft=current_draft,
            final_critique=critique,
            refinements_used=refinements_used,
            wall_clock_ms=clock_ms() - start_ms,
            token_usage=token_usage,
            critic_iterations=critic_iterations,
            history=tuple(history),
        )

    # Refinement loop (critique.verdict == "refine").
    while refinements_used < budget.max_refinements:
        if _budget_exhausted():
            return LoopResult(
                outcome=LoopOutcome.BUDGET_EXHAUSTED,
                final_draft=current_draft,
                final_critique=critique,
                refinements_used=refinements_used,
                wall_clock_ms=clock_ms() - start_ms,
                token_usage=token_usage,
                critic_iterations=critic_iterations,
                history=tuple(history),
            )

        refined = draft_fn(critique)
        token_usage += max(0, refined.token_delta)
        current_draft = refined.draft
        refinements_used += 1

        if _budget_exhausted():
            return LoopResult(
                outcome=LoopOutcome.BUDGET_EXHAUSTED,
                final_draft=current_draft,
                final_critique=critique,
                refinements_used=refinements_used,
                wall_clock_ms=clock_ms() - start_ms,
                token_usage=token_usage,
                critic_iterations=critic_iterations,
                history=tuple(history),
            )

        critique = critique_fn(current_draft)
        token_usage += max(0, critique.token_delta)
        critic_iterations += 1
        history.append(critique)

        if critique.verdict == "accept":
            return LoopResult(
                outcome=LoopOutcome.ACCEPT,
                final_draft=current_draft,
                final_critique=critique,
                refinements_used=refinements_used,
                wall_clock_ms=clock_ms() - start_ms,
                token_usage=token_usage,
                critic_iterations=critic_iterations,
                history=tuple(history),
            )
        if critique.verdict == "escalate":
            return LoopResult(
                outcome=LoopOutcome.ESCALATE,
                final_draft=current_draft,
                final_critique=critique,
                refinements_used=refinements_used,
                wall_clock_ms=clock_ms() - start_ms,
                token_usage=token_usage,
                critic_iterations=critic_iterations,
                history=tuple(history),
            )

    # Refinement budget exhausted; critic still wanted more.
    return LoopResult(
        outcome=LoopOutcome.REFINE_EXHAUSTED,
        final_draft=current_draft,
        final_critique=critique,
        refinements_used=refinements_used,
        wall_clock_ms=clock_ms() - start_ms,
        token_usage=token_usage,
        critic_iterations=critic_iterations,
        history=tuple(history),
    )


__all__ = [
    "Critique",
    "CriticVerdict",
    "DraftResult",
    "LoopBudget",
    "LoopOutcome",
    "LoopResult",
    "run_evaluator_optimizer_loop",
]
