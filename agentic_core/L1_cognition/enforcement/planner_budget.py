"""Plan-lifecycle budget enforcer (ADR-043, W4/P4.1).

Distinct from :class:`agentic_core.L1_cognition.reasoning.evaluator_optimizer.LoopBudget`:

- ``LoopBudget``    — caps ONE evaluator-optimizer refinement loop (T2↔T3).
- ``PlannerBudget`` — caps the ENTIRE plan lifecycle (triage → bundle → envelope
  → thinking desk → emit).  Spans multiple loops if the planner invokes
  several (e.g. outer decomposition + inner refinement).

Public surface:
    PlannerBudget        — frozen dataclass, hard caps + soft warning threshold
    PlannerBudgetTracker — stateful wall-clock/token/refinement/critic counter
    BudgetExhausted      — exception raised when ``require_remaining()`` fails

The tracker is injected into the planner; all I/O (clock, token counting) is
controlled by the caller so unit tests remain deterministic.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


class BudgetExhausted(RuntimeError):
    """Raised by :meth:`PlannerBudgetTracker.require_remaining` when a cap is hit."""


@dataclass(frozen=True)
class PlannerBudget:
    """Hard caps + soft warn threshold for a plan lifecycle.

    Fields:
        max_refinements: Total refinements summed across all inner loops.
        wall_clock_ms_cap: Total wall-clock for the plan lifecycle.
        token_cap: Total tokens allowed (draft + critic + envelope).
        max_critic_iterations: Total critic passes allowed.
        warn_fraction: 0.0 – 1.0, soft-warn threshold (default 0.80).
            ``warn_fraction == 0`` disables the warning signal.

    All caps must be non-negative integers.  A cap of 0 means "no budget"
    for that dimension — the tracker will raise :class:`BudgetExhausted`
    on the first increment.
    """

    max_refinements: int = 3
    wall_clock_ms_cap: int = 60_000
    token_cap: int = 50_000
    max_critic_iterations: int = 6
    warn_fraction: float = 0.80

    def __post_init__(self) -> None:
        for fname in (
            "max_refinements",
            "wall_clock_ms_cap",
            "token_cap",
            "max_critic_iterations",
        ):
            val = getattr(self, fname)
            if not isinstance(val, int) or val < 0:
                raise ValueError(f"{fname} must be a non-negative int, got {val!r}")
        if not 0.0 <= self.warn_fraction <= 1.0:
            raise ValueError(f"warn_fraction must be in [0.0, 1.0], got {self.warn_fraction!r}")


def _default_clock_ms() -> int:
    """Monotonic clock in milliseconds — injected for test determinism."""
    return int(time.monotonic() * 1000)


@dataclass
class PlannerBudgetTracker:
    """Stateful tracker for a PlannerBudget.

    Not frozen (it mutates as work is recorded).  Caller is responsible for
    feeding ``record_*`` calls.  Check :meth:`require_remaining` before each
    expensive step; it raises :class:`BudgetExhausted` when any cap is hit.
    """

    budget: PlannerBudget
    clock_ms: Callable[[], int] = field(default=_default_clock_ms)
    _start_ms: int = field(init=False, default=0)
    _tokens_used: int = field(init=False, default=0)
    _refinements_used: int = field(init=False, default=0)
    _critic_iterations: int = field(init=False, default=0)
    _warn_fired: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self._start_ms = self.clock_ms()

    @property
    def elapsed_ms(self) -> int:
        return max(0, self.clock_ms() - self._start_ms)

    @property
    def tokens_used(self) -> int:
        return self._tokens_used

    @property
    def refinements_used(self) -> int:
        return self._refinements_used

    @property
    def critic_iterations(self) -> int:
        return self._critic_iterations

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-safe dict of current counters."""
        return {
            "refinements_used": self._refinements_used,
            "wall_clock_ms": self.elapsed_ms,
            "token_usage": self._tokens_used,
            "critic_iterations": self._critic_iterations,
        }

    def record_tokens(self, n: int) -> None:
        if not isinstance(n, int) or n < 0:
            raise ValueError(f"record_tokens requires non-negative int, got {n!r}")
        self._tokens_used += n

    def record_refinement(self) -> None:
        self._refinements_used += 1

    def record_critic_pass(self) -> None:
        self._critic_iterations += 1

    def warn_threshold_hit(self) -> bool:
        """True once ANY dimension reaches ``warn_fraction`` of its cap.

        Idempotent: transitions False → True exactly once.
        """
        if self._warn_fired or self.budget.warn_fraction == 0.0:
            return self._warn_fired
        frac = self.budget.warn_fraction
        hit = (
            _at_or_above(self._refinements_used, self.budget.max_refinements, frac)
            or _at_or_above(self.elapsed_ms, self.budget.wall_clock_ms_cap, frac)
            or _at_or_above(self._tokens_used, self.budget.token_cap, frac)
            or _at_or_above(self._critic_iterations, self.budget.max_critic_iterations, frac)
        )
        if hit:
            self._warn_fired = True
        return hit

    def require_remaining(self) -> None:
        """Raise :class:`BudgetExhausted` if any hard cap is hit."""
        if self._refinements_used >= self.budget.max_refinements:
            raise BudgetExhausted(f"max_refinements {self.budget.max_refinements} reached")
        if self._critic_iterations >= self.budget.max_critic_iterations:
            raise BudgetExhausted(f"max_critic_iterations {self.budget.max_critic_iterations} reached")
        if self.elapsed_ms >= self.budget.wall_clock_ms_cap:
            raise BudgetExhausted(f"wall_clock_ms {self.elapsed_ms} >= cap {self.budget.wall_clock_ms_cap}")
        if self._tokens_used >= self.budget.token_cap:
            raise BudgetExhausted(f"tokens {self._tokens_used} >= cap {self.budget.token_cap}")


def _at_or_above(value: int, cap: int, fraction: float) -> bool:
    if cap <= 0:
        return False
    return value >= int(cap * fraction)


__all__ = [
    "BudgetExhausted",
    "PlannerBudget",
    "PlannerBudgetTracker",
]
