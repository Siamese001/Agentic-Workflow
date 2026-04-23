"""Stability metrics for non-deterministic agent evaluations (LJH5.1).

Anthropic 'Demystifying evals for AI agents' (2026) recommends two
metrics for capturing per-task non-determinism:

- ``pass@k``  — probability an agent gets at least one correct solution
  in ``k`` attempts. Higher ``k`` generally raises the score (more
  "shots on goal").
- ``pass^k``  — probability ALL ``k`` trials succeed. Falls as ``k``
  grows because demanding consistency across more trials is a harder
  bar. Important for customer-facing agents where users expect reliable
  behavior every time.

Both use the unbiased estimator from Chen et al. 2021 (HumanEval) for
``pass@k``: given ``n`` total samples with ``c`` successes,

    pass@k = 1 - comb(n-c, k) / comb(n, k)     if n - c >= k, else 1.0

``pass^k`` is the straightforward ``(c/n) ** k`` when empirical or
``p ** k`` when given a per-trial success probability.

Zero external dependencies.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import comb

__all__ = ["StabilityReport", "pass_at_k", "pass_hat_k"]


def _validate_common(n: int, c: int, k: int) -> None:
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    if not 0 <= c <= n:
        raise ValueError(f"c must be in [0, {n}], got {c}")
    if k < 1:
        raise ValueError(f"k must be >= 1, got {k}")


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased ``pass@k`` estimator (Chen et al., HumanEval 2021).

    Args:
        n: total trials
        c: number of successful trials
        k: number of attempts considered (must be <= n)

    Returns:
        probability of at least one success in ``k`` independent samples
    """
    _validate_common(n, c, k)
    if k > n:
        raise ValueError(f"k={k} exceeds n={n}")
    if n - c < k:
        return 1.0
    return 1.0 - (comb(n - c, k) / comb(n, k))


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Empirical ``pass^k`` — probability all ``k`` trials succeed.

    Uses per-trial success rate ``c/n`` raised to the ``k`` power. Matches
    the Anthropic roadmap definition for customer-facing agent evals.
    Unlike ``pass_at_k``, ``k`` may exceed ``n`` (extrapolation is valid
    under the i.i.d. assumption).
    """
    _validate_common(n, c, k)
    p = c / n if n > 0 else 0.0
    return p ** k


@dataclass(frozen=True)
class StabilityReport:
    """Summary of pass@k / pass^k across one or more k values."""

    n: int
    c: int
    pass_rate: float  # c / n
    pass_at_k_values: tuple[tuple[int, float], ...]
    pass_hat_k_values: tuple[tuple[int, float], ...]

    @classmethod
    def from_results(
        cls,
        results: Sequence[bool],
        k_values: Sequence[int] = (1, 3, 5),
    ) -> StabilityReport:
        """Build a report from a sequence of boolean trial outcomes."""
        n = len(results)
        c = sum(1 for r in results if r)
        pass_rate = c / n if n > 0 else 0.0
        pak = tuple(
            (k, pass_at_k(n, c, k) if k <= n else float("nan"))
            for k in k_values
        )
        phk = tuple((k, pass_hat_k(n, c, k)) for k in k_values)
        return cls(
            n=n,
            c=c,
            pass_rate=pass_rate,
            pass_at_k_values=pak,
            pass_hat_k_values=phk,
        )
