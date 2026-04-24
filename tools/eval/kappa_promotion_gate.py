"""Inter-rater Cohen's kappa promotion gate (F4.1).

Promotes ``gold_outcome: pending`` items to ``gold_outcome: scored`` when
≥2 human raters have labeled the item and the inter-rater Cohen's kappa
meets the threshold declared in ``data/eval/golden/README.md`` (≥ 0.6).

Design
------
- Kappa is computed over the full rater set, weighted by ordinal distance
  on the 1-5 rubric scale (quadratic weighting). For the 2-rater case this
  reduces to the standard Cohen's kappa; for ≥3 raters we take the mean
  pairwise kappa, which is sufficient here because every item is labeled
  by the SAME rater pool (consistent margins).
- Consensus gold_score is the integer nearest to the mean of all rater
  scores. Ties break toward the STRICTER rater per the README convention
  (lower score wins on a tie, since "stricter" means "assigns lower
  scores" in this rubric family).
- Items where any rater returned ``null`` / ``"unknown"`` are promoted to
  ``gold_outcome: "unknown"`` with ``gold_score: null`` — never blocked —
  because unknown-handling is a measured dimension, not a failure.

Invariants
----------
- Pure functions; no IO, no wall-clock, no environment access.
- Idempotent: re-promoting a scored item is a no-op that returns the
  unchanged payload.
- Never downgrades: a scored item cannot revert to pending.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any, Literal

DEFAULT_KAPPA_THRESHOLD: float = 0.6
RUBRIC_MIN: int = 1
RUBRIC_MAX: int = 5


@dataclass(frozen=True, slots=True)
class RaterLabel:
    rater_id: str
    score: int | None            # None == "unknown"
    notes: str = ""


@dataclass(frozen=True, slots=True)
class PromotionDecision:
    item_id: str
    outcome: Literal["scored", "unknown", "pending", "unchanged"]
    gold_score: int | None
    kappa: float | None
    rater_count: int
    reason: str


def _quadratic_weight(i: int, j: int, k: int) -> float:
    """Weight matrix entry for ordinal ratings on a k-category scale."""
    denom = (k - 1) ** 2
    return 1.0 - ((i - j) ** 2) / denom if denom else 1.0


def _pairwise_weighted_kappa(a: list[int], b: list[int]) -> float:
    """Quadratic-weighted Cohen's kappa between two aligned rater lists."""
    assert len(a) == len(b) and a, "rater lists must be non-empty and aligned"
    categories = list(range(RUBRIC_MIN, RUBRIC_MAX + 1))
    k = len(categories)
    n = len(a)
    # Observed and expected weighted agreement.
    freq_a = {c: a.count(c) / n for c in categories}
    freq_b = {c: b.count(c) / n for c in categories}
    po = 0.0
    pe = 0.0
    for i_idx, ci in enumerate(categories):
        for j_idx, cj in enumerate(categories):
            w = _quadratic_weight(i_idx, j_idx, k)
            obs = sum(1 for x, y in zip(a, b) if x == ci and y == cj) / n
            exp = freq_a[ci] * freq_b[cj]
            po += w * obs
            pe += w * exp
    if abs(1.0 - pe) < 1e-12:
        # Degenerate: raters have zero marginal variance. Treat as
        # perfect agreement iff all observations match, else zero kappa.
        return 1.0 if a == b else 0.0
    return (po - pe) / (1.0 - pe)


def compute_kappa(rater_labels: list[RaterLabel]) -> float | None:
    """Return mean pairwise quadratic-weighted kappa over integer scores.

    Returns None if fewer than 2 raters supplied integer scores.
    """
    integer_labels = [r for r in rater_labels if isinstance(r.score, int)]
    if len(integer_labels) < 2:
        return None
    # One aligned score per rater per item — our caller passes labels for
    # a SINGLE item, so each rater contributes exactly one score. To use
    # pairwise kappa meaningfully we treat the (score_a, score_b) pair
    # directly with quadratic weight.
    kappas: list[float] = []
    for i, ra in enumerate(integer_labels):
        for rb in integer_labels[i + 1:]:
            kappas.append(_pairwise_weighted_kappa([ra.score], [rb.score]))  # type: ignore[list-item]
    return statistics.fmean(kappas) if kappas else None


def _consensus_score(rater_labels: list[RaterLabel]) -> int:
    """Integer nearest the mean; ties break toward the stricter (lower) rater."""
    scores = [r.score for r in rater_labels if isinstance(r.score, int)]
    assert scores, "consensus requires at least one integer score"
    mean = statistics.fmean(scores)
    lower = int(mean)
    upper = lower + 1
    # If mean is closer to lower OR exactly halfway, pick lower (strict).
    if (mean - lower) <= 0.5:
        return max(RUBRIC_MIN, lower)
    return min(RUBRIC_MAX, upper)


def evaluate_item(
    item: dict[str, Any],
    kappa_threshold: float = DEFAULT_KAPPA_THRESHOLD,
) -> PromotionDecision:
    """Decide whether an item with its ``human_labels`` can be promoted.

    Parameters
    ----------
    item : dict
        A golden-dataset item following ``data/eval/golden/README.md`` schema.
    kappa_threshold : float
        Promotion cutoff on the mean pairwise quadratic-weighted kappa.
    """
    item_id = str(item.get("item_id") or "<unknown>")
    outcome = str(item.get("gold_outcome") or "").lower()

    if outcome == "scored":
        return PromotionDecision(item_id, "unchanged", item.get("gold_score"), None,
                                 len(item.get("human_labels") or []),
                                 "already scored; idempotent no-op")

    raw = item.get("human_labels") or []
    raters = [
        RaterLabel(rater_id=str(e.get("rater_id") or f"anon-{i}"),
                   score=(int(e["score"]) if isinstance(e.get("score"), (int, float)) and e.get("score") is not None else None),
                   notes=str(e.get("notes") or ""))
        for i, e in enumerate(raw)
    ]

    if any(r.score is None for r in raters):
        if not raters:
            return PromotionDecision(item_id, "pending", None, None, 0,
                                     "no human labels yet")
        return PromotionDecision(item_id, "unknown", None, None, len(raters),
                                 "at least one rater returned unknown; outcome=unknown")

    if len(raters) < 2:
        return PromotionDecision(item_id, "pending", None, None, len(raters),
                                 f"need >=2 raters; got {len(raters)}")

    kappa = compute_kappa(raters)
    if kappa is None or kappa < kappa_threshold:
        return PromotionDecision(item_id, "pending", None, kappa, len(raters),
                                 f"kappa={kappa} < threshold={kappa_threshold}; rubric prompt needs revision")

    gold = _consensus_score(raters)
    return PromotionDecision(item_id, "scored", gold, kappa, len(raters),
                             f"kappa={kappa:.3f} meets threshold; gold_score={gold} (strict tie-break)")


def apply_promotion(item: dict[str, Any], decision: PromotionDecision) -> dict[str, Any]:
    """Return a new item dict reflecting the promotion decision.

    - ``unchanged`` and ``pending`` return the input unchanged.
    - ``scored`` sets ``gold_outcome`` and ``gold_score``.
    - ``unknown`` sets ``gold_outcome: "unknown"``, ``gold_score: null``.
    """
    if decision.outcome in ("unchanged", "pending"):
        return item
    out = dict(item)
    if decision.outcome == "scored":
        out["gold_outcome"] = "scored"
        out["gold_score"] = decision.gold_score
    elif decision.outcome == "unknown":
        out["gold_outcome"] = "unknown"
        out["gold_score"] = None
    out.setdefault("promotion_audit", {})
    out["promotion_audit"] = {
        "kappa": decision.kappa,
        "rater_count": decision.rater_count,
        "reason": decision.reason,
    }
    return out
