"""C0 retrieval-mode bandit + adaptive-k + citation-coverage metric.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W6.

Closes opportunities 3.1 (mode bandit per query class), 3.2 (adaptive k_max
via marginal utility), and 3.4 (citation-anchor coverage metric) from the
routing-enhancement opportunity register.

Three independent surfaces:

1. :class:`RetrievalModeBandit` — Thompson over {dense, sparse, hybrid, graph}
   keyed by intent class. Reuses the Beta-Bernoulli pattern from W4.
2. :func:`adaptive_k_cutoff` — stops k expansion at the first index where the
   marginal cosine drop exceeds θ (default 0.04). Replaces fixed top-k.
3. :func:`citation_coverage` — fraction of answer claims whose support
   anchor resolves to a returned chunk_id. Feeds R3 ``support_target``
   calibration.
"""

from __future__ import annotations

import random
import threading
from dataclasses import dataclass

from agentic_core.L0_routing.reasoning.namespace_bandit import (
    BetaPosterior,
)

KNOWN_RETRIEVAL_MODES: frozenset[str] = frozenset(
    {"dense", "sparse", "hybrid", "graph"},
)


@dataclass(frozen=True)
class _ModeKey:
    intent_class: str
    mode: str


class RetrievalModeBandit:
    """Thompson-sampling bandit over retrieval modes per intent class."""

    def __init__(self, seed: int | None = None) -> None:
        self._posteriors: dict[_ModeKey, BetaPosterior] = {}
        self._lock = threading.Lock()
        self._rng = random.Random(seed)

    def update(self, intent_class: str, mode: str, *, success: bool) -> None:
        if mode not in KNOWN_RETRIEVAL_MODES:
            raise ValueError(
                f"unknown mode={mode!r}; allowed={sorted(KNOWN_RETRIEVAL_MODES)}",
            )
        key = _ModeKey(intent_class=intent_class, mode=mode)
        with self._lock:
            self._posteriors.setdefault(key, BetaPosterior()).update(success)

    def choose(self, intent_class: str, admissible: list[str] | None = None) -> str:
        if admissible is None:
            modes = sorted(KNOWN_RETRIEVAL_MODES)
        else:
            modes = list(admissible)
        if not modes:
            raise ValueError("admissible modes list must be non-empty")
        for m in modes:
            if m not in KNOWN_RETRIEVAL_MODES:
                raise ValueError(f"unknown mode={m!r}")
        with self._lock:
            best_mode = modes[0]
            best_sample = float("-inf")
            for mode in modes:
                key = _ModeKey(intent_class=intent_class, mode=mode)
                p = self._posteriors.setdefault(key, BetaPosterior())
                sampled = p.sample(self._rng)
                if sampled > best_sample:
                    best_sample = sampled
                    best_mode = mode
            return best_mode

    def posterior(self, intent_class: str, mode: str) -> BetaPosterior:
        with self._lock:
            p = self._posteriors.get(_ModeKey(intent_class=intent_class, mode=mode))
            if p is None:
                return BetaPosterior()
            return BetaPosterior(alpha=p.alpha, beta=p.beta)


def adaptive_k_cutoff(
    cosine_scores: list[float],
    *,
    marginal_drop_threshold: float = 0.04,
    min_k: int = 1,
    max_k: int = 50,
) -> int:
    """Return the k at which to stop expansion via marginal-utility rule.

    Walk the sorted-descending cosine list. Stop at the first index where
    ``score[k-1] - score[k] > marginal_drop_threshold``. Always returns at
    least ``min_k`` and at most ``min(max_k, len(cosine_scores))``.

    Args:
        cosine_scores: Sorted-descending similarity scores (caller's job).
        marginal_drop_threshold: Per-step drop that triggers cutoff.
        min_k: Minimum docs to return regardless.
        max_k: Hard ceiling.

    Returns:
        The cutoff index (1-indexed count, suitable for ``scores[:k]``).

    Raises:
        ValueError: When ``min_k > max_k`` or ``min_k < 1``.
    """
    if min_k < 1:
        raise ValueError(f"min_k must be >= 1, got {min_k}")
    if min_k > max_k:
        raise ValueError(f"min_k={min_k} > max_k={max_k}")
    if not cosine_scores:
        return 0
    n = len(cosine_scores)
    ceiling = min(max_k, n)
    # Confirm sorted-descending
    for i in range(1, n):
        if cosine_scores[i] > cosine_scores[i - 1] + 1e-9:
            raise ValueError("cosine_scores must be sorted descending")
    # Walk forward from k=1 looking for first big drop. Clamp result to [min_k, ceiling]
    # so a drop before min_k still produces a valid cutoff at the floor.
    cutoff = ceiling
    for k in range(1, ceiling):
        drop = cosine_scores[k - 1] - cosine_scores[k]
        if drop > marginal_drop_threshold:
            cutoff = k
            break
    return max(min_k, min(cutoff, ceiling))


def citation_coverage(
    answer_claims: list[str],
    claim_to_anchor: dict[str, str | None],
    returned_chunk_ids: set[str],
) -> float:
    """Fraction of answer claims whose anchor lands in a returned chunk.

    Args:
        answer_claims: Atomic claim strings extracted from the answer.
        claim_to_anchor: Map from claim → chunk_id (or None when the claim
            has no resolvable anchor).
        returned_chunk_ids: chunk_ids C0 actually returned to the answerer.

    Returns:
        ``covered / total`` in ``[0.0, 1.0]``. Empty claim list → 0.0.
        A claim with anchor=None counts as uncovered.
    """
    if not answer_claims:
        return 0.0
    covered = 0
    for claim in answer_claims:
        anchor = claim_to_anchor.get(claim)
        if anchor is not None and anchor in returned_chunk_ids:
            covered += 1
    return covered / len(answer_claims)


__all__ = [
    "KNOWN_RETRIEVAL_MODES",
    "RetrievalModeBandit",
    "adaptive_k_cutoff",
    "citation_coverage",
]
