"""L6 promotion gates — Wilson-CI + auto-rollback + counterfactual shadow.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W12.

Closes opportunities 10.1 (Wilson confidence-interval promotion gate),
10.2 (auto-rollback canary trigger on regression), 10.3 (counterfactual
shadow eval).

Three pure-function surfaces:

1. :func:`wilson_interval` — exact Wilson score interval for a Bernoulli
   sample. Stable on tiny samples where naive normal approximation lies.
2. :func:`promotion_decision` — gates a candidate by requiring its lower
   bound to exceed the baseline's upper bound.
3. :func:`auto_rollback_trigger` — given paired (canary, baseline) samples
   on N metrics, returns True iff any metric regressed by >= ``sigma_threshold``.
4. :func:`counterfactual_uplift` — ``E[shadow] - E[prod]`` over paired
   samples; used as the shadow-stack uplift signal that gates promotion.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass

_LOGGER = logging.getLogger(__name__)

# Constitutional §29 closed-loop wiring (W5.3). The helper is imported lazily
# inside `promotion_decision` so this module stays importable when
# `tools.ledgers` is absent (e.g. isolated unit tests).
_PROMO_HELPER = None  # type: ignore[var-annotated]


def _get_promo_helper():
    """Lazy singleton for the L6/promo RouterClosedLoopHelper."""
    global _PROMO_HELPER  # noqa: PLW0603
    if _PROMO_HELPER is not None:
        return _PROMO_HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _PROMO_HELPER = RouterClosedLoopHelper(
            layer="L6",
            router="promo",
            ledger_name="router_l6_promo",
            repo_area="agentic_core/L6_observability/promotion_gates.py",
        )
        return _PROMO_HELPER
    except ImportError:  # guardian: allow-log-and-swallow -- helper unavailable must not break promotion gating
        _LOGGER.debug("RouterClosedLoopHelper unavailable for L6/promo", exc_info=True)
        return None


@dataclass(frozen=True)
class WilsonInterval:
    """Wilson score interval for a Bernoulli sample at a given z."""

    point: float
    lower: float
    upper: float
    n: int


def wilson_interval(
    successes: int,
    n: int,
    *,
    z: float = 1.96,
) -> WilsonInterval:
    """Return the Wilson confidence interval for ``successes/n`` at level ``z``.

    z=1.96 ≈ 95% two-sided. z=2.576 ≈ 99%.

    Empty sample (n=0) returns ``[0, 1]`` with point=0 — caller MUST treat
    as insufficient evidence.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    if successes < 0 or successes > n:
        raise ValueError(f"successes={successes} not in [0, {n}]")
    if z < 0:
        raise ValueError(f"z must be >= 0, got {z}")
    if n == 0:
        return WilsonInterval(point=0.0, lower=0.0, upper=1.0, n=0)
    p = successes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n)) / denom
    return WilsonInterval(
        point=p,
        lower=max(0.0, centre - half),
        upper=min(1.0, centre + half),
        n=n,
    )


@dataclass(frozen=True)
class PromotionVerdict:
    promote: bool
    reason: str
    candidate: WilsonInterval
    baseline: WilsonInterval


def promotion_decision(
    *,
    candidate_successes: int,
    candidate_n: int,
    baseline_successes: int,
    baseline_n: int,
    z: float = 1.96,
    min_n_each_arm: int = 30,
) -> PromotionVerdict:
    """Promote iff candidate lower-CI > baseline upper-CI on both arms.

    Per opportunity 10.1: Wilson lower bound > baseline upper bound is the
    strongest distribution-free promotion criterion.
    """
    candidate = wilson_interval(candidate_successes, candidate_n, z=z)
    baseline = wilson_interval(baseline_successes, baseline_n, z=z)
    if candidate.n < min_n_each_arm or baseline.n < min_n_each_arm:
        verdict = PromotionVerdict(
            promote=False,
            reason=(
                f"insufficient sample (need {min_n_each_arm} per arm; "
                f"have candidate={candidate.n}, baseline={baseline.n})"
            ),
            candidate=candidate,
            baseline=baseline,
        )
        _record_promo_decision(
            verdict=verdict,
            candidate_successes=candidate_successes,
            candidate_n=candidate_n,
            baseline_successes=baseline_successes,
            baseline_n=baseline_n,
            min_n_each_arm=min_n_each_arm,
            z=z,
        )
        return verdict
    verdict: PromotionVerdict
    if candidate.lower > baseline.upper:
        verdict = PromotionVerdict(
            promote=True,
            reason=(
                f"candidate lower={candidate.lower:.4f} > "
                f"baseline upper={baseline.upper:.4f}"
            ),
            candidate=candidate,
            baseline=baseline,
        )
        _record_promo_decision(
            verdict=verdict,
            candidate_successes=candidate_successes,
            candidate_n=candidate_n,
            baseline_successes=baseline_successes,
            baseline_n=baseline_n,
            min_n_each_arm=min_n_each_arm,
            z=z,
        )
        return verdict
    verdict = PromotionVerdict(
        promote=False,
        reason=(
            f"CIs overlap (candidate=[{candidate.lower:.4f}, {candidate.upper:.4f}], "
            f"baseline=[{baseline.lower:.4f}, {baseline.upper:.4f}])"
        ),
        candidate=candidate,
        baseline=baseline,
    )
    _record_promo_decision(
        verdict=verdict,
        candidate_successes=candidate_successes,
        candidate_n=candidate_n,
        baseline_successes=baseline_successes,
        baseline_n=baseline_n,
        min_n_each_arm=min_n_each_arm,
        z=z,
    )
    return verdict


def _record_promo_decision(
    *,
    verdict: PromotionVerdict,
    candidate_successes: int,
    candidate_n: int,
    baseline_successes: int,
    baseline_n: int,
    min_n_each_arm: int,
    z: float,
) -> None:
    """Constitutional §29 — emit ROUTER_DECISION + write durable ledger row.

    Fail-soft: any helper failure is swallowed so promotion gating is never
    broken by telemetry. Records the FULL Wilson interval evidence so
    downstream calibration can audit each verdict.
    """
    helper = _get_promo_helper()
    if helper is None:
        return
    try:
        helper.record_decision(
            selected="promote" if verdict.promote else "reject",
            cell={"min_n_each_arm": int(min_n_each_arm), "z": float(z)},
            predicted_p_success=float(verdict.candidate.lower),
            eu_score=float(verdict.candidate.lower - verdict.baseline.upper),
            prediction_extras={
                "candidate_successes": int(candidate_successes),
                "candidate_n": int(candidate_n),
                "baseline_successes": int(baseline_successes),
                "baseline_n": int(baseline_n),
                "candidate_lower": float(verdict.candidate.lower),
                "candidate_upper": float(verdict.candidate.upper),
                "baseline_lower": float(verdict.baseline.lower),
                "baseline_upper": float(verdict.baseline.upper),
                "promote": bool(verdict.promote),
                "verdict_reason": str(verdict.reason),
            },
        )
    except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- ledger emission is best-effort; promotion must never break
        _LOGGER.debug("promotion_decision ledger emit failed", exc_info=True)


@dataclass(frozen=True)
class MetricSample:
    """Paired metric observation for canary vs baseline."""

    metric_name: str
    canary_mean: float
    canary_stddev: float
    baseline_mean: float
    baseline_stddev: float
    n: int

    @property
    def regression_sigma(self) -> float:
        """How many baseline-stddevs below baseline the canary mean is.

        Negative when the canary is *better* than baseline. Higher = worse.
        """
        if self.baseline_stddev == 0:
            return 0.0 if self.canary_mean >= self.baseline_mean else float("inf")
        return (self.baseline_mean - self.canary_mean) / self.baseline_stddev


def auto_rollback_trigger(
    samples: list[MetricSample],
    *,
    sigma_threshold: float = 1.5,
    min_n: int = 20,
) -> tuple[bool, list[str]]:
    """Return (rollback_now, regressed_metric_names).

    Per opportunity 10.2: any single metric regressed by >= ``sigma_threshold``
    triggers rollback. ``min_n`` filters out noisy small samples.
    """
    if sigma_threshold < 0:
        raise ValueError("sigma_threshold must be >= 0")
    if min_n < 1:
        raise ValueError("min_n must be >= 1")
    regressed: list[str] = []
    for s in samples:
        if s.n < min_n:
            continue
        if s.regression_sigma >= sigma_threshold:
            regressed.append(s.metric_name)
    return (len(regressed) > 0, regressed)


def counterfactual_uplift(
    shadow_outcomes: list[bool],
    prod_outcomes: list[bool],
) -> float:
    """E[shadow] - E[prod]. Positive ⇒ shadow stack is better.

    Lists must be paired (same request replayed through both stacks) and
    of equal length.
    """
    if len(shadow_outcomes) != len(prod_outcomes):
        raise ValueError(
            f"length mismatch: shadow={len(shadow_outcomes)}, "
            f"prod={len(prod_outcomes)}",
        )
    if not shadow_outcomes:
        return 0.0
    shadow_mean = sum(1.0 if x else 0.0 for x in shadow_outcomes) / len(shadow_outcomes)
    prod_mean = sum(1.0 if x else 0.0 for x in prod_outcomes) / len(prod_outcomes)
    return shadow_mean - prod_mean


__all__ = [
    "MetricSample",
    "PromotionVerdict",
    "WilsonInterval",
    "auto_rollback_trigger",
    "counterfactual_uplift",
    "promotion_decision",
    "wilson_interval",
]
