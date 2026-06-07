"""L3 workflow-shape calibration — per-task-class loop iter + oscillation.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W7.

Closes opportunities 5.1 (per-task-class loop-iteration learner replacing
the global ``r_loop_max_iterations=3``), 5.3 (cascade off-ramp metric), and
5.4 (oscillation amplitude as early-break signal).

Three independent surfaces:

1. :func:`recommend_max_iterations` — fits a per-task-class iteration cap
   from the empirical convergence histogram (95th percentile). Replaces
   the global cap with a learned one when ``n_observations >= min_n``.
2. :func:`oscillation_amplitude` — cosine similarity between iter N and
   iter N-2. High amplitude → likely orbit, break early.
3. :func:`cascade_skip_rate` — fraction of cascades that jumped TIER_S →
   TIER_L without TIER_M. High rate signals TIER_M is mis-calibrated.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class IterationRecommendation:
    task_class: str
    n_observations: int
    p95_iterations: int
    recommended_max: int
    confident: bool


def recommend_max_iterations(
    convergence_histogram: dict[str, list[int]],
    *,
    min_observations: int = 30,
    fallback_max: int = 3,
    hard_ceiling: int = 10,
) -> dict[str, IterationRecommendation]:
    """Fit per-task-class max_iterations from observed convergence counts.

    Args:
        convergence_histogram: ``{task_class: [iters_per_run, ...]}`` — each
            list element is the observed iteration count at convergence
            for one run.
        min_observations: Below this count we keep ``fallback_max``.
        fallback_max: Cap when not enough data (matches global default).
        hard_ceiling: Hard ceiling regardless of empirical p95.

    Returns:
        Per-task-class recommendation dict.
    """
    out: dict[str, IterationRecommendation] = {}
    for task_class, observations in convergence_histogram.items():
        n = len(observations)
        if n == 0:
            continue
        sorted_obs = sorted(observations)
        # P95 — uses linear interpolation per inclusive convention
        rank = 0.95 * (n - 1)
        lo = math.floor(rank)
        hi = math.ceil(rank)
        if lo == hi:
            p95 = sorted_obs[lo]
        else:
            p95 = int(round(sorted_obs[lo] * (hi - rank) + sorted_obs[hi] * (rank - lo)))
        confident = n >= min_observations
        recommended = min(hard_ceiling, max(p95, fallback_max if not confident else 1))
        if not confident:
            recommended = fallback_max
        out[task_class] = IterationRecommendation(
            task_class=task_class,
            n_observations=n,
            p95_iterations=p95,
            recommended_max=recommended,
            confident=confident,
        )
    return out


def oscillation_amplitude(iteration_embeddings: list[list[float]]) -> list[float]:
    """Cosine similarity between iter N and iter N-2.

    High similarity = orbit / oscillation; the loop is repeating itself
    rather than converging. Caller can break the loop when amplitude
    exceeds a threshold (e.g. > 0.95).

    Args:
        iteration_embeddings: One embedding vector per iteration. Lists
            shorter than 3 return ``[]`` because there are no N-2 pairs.

    Returns:
        Per-iteration amplitude starting from index 2. Empty for short
        sequences. Each value in [-1.0, 1.0].

    Raises:
        ValueError: When embedding lengths are inconsistent.
    """
    if len(iteration_embeddings) < 3:
        return []
    dim = len(iteration_embeddings[0])
    for vec in iteration_embeddings:
        if len(vec) != dim:
            raise ValueError("inconsistent embedding dimensions")
    out: list[float] = []
    for i in range(2, len(iteration_embeddings)):
        a = iteration_embeddings[i]
        b = iteration_embeddings[i - 2]
        out.append(_cosine(a, b))
    return out


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity. Returns 0.0 when either vector is zero."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cascade_skip_rate(cascade_paths: list[list[str]]) -> float:
    """Fraction of cascades that skipped a tier (e.g. TIER_S → TIER_L).

    A "skip" is any path that contains TIER_S and TIER_L but NOT TIER_M.
    Empty input → 0.0. Out-of-vocabulary tiers are ignored.

    Args:
        cascade_paths: One list per request; elements are tier strings.

    Returns:
        skip_count / total in [0.0, 1.0].
    """
    if not cascade_paths:
        return 0.0
    skips = 0
    for path in cascade_paths:
        s = set(path)
        if "TIER_S" in s and "TIER_L" in s and "TIER_M" not in s:
            skips += 1
    return skips / len(cascade_paths)


def cascade_path_distribution(cascade_paths: list[list[str]]) -> dict[str, int]:
    """Return a Counter-as-dict of cascade-path-shape strings.

    Each path is collapsed to a "→"-joined string so dashboards can sort
    by frequency.
    """
    if not cascade_paths:
        return {}
    c: Counter[str] = Counter()
    for path in cascade_paths:
        c["→".join(path)] += 1
    return dict(c)


__all__ = [
    "IterationRecommendation",
    "cascade_path_distribution",
    "cascade_skip_rate",
    "oscillation_amplitude",
    "recommend_max_iterations",
]
