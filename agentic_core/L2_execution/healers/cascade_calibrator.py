"""Cascade calibrator — math primitives for L2/cascade router (constitutional §29).

Provides the four scoring functions the closed-loop ledger needs:

    eu       = Expected Utility of dispatching a tier given a calibrated prior
    brier    = (predicted_p - actual)^2 — per-row component for calibration
    fingerprint = stable hash over the routing cell (failure_class × source_layer
                  × retry_band × error_code) so identical situations aggregate
                  cleanly in calibration runs
    wilson_lower_bound = lower bound of Wilson score interval for a Bernoulli
                          proportion, used by the §29 promotion gate
                          (wilson_lower ≥ 0.60 required)

All four are pure functions, stdlib only, no I/O. The HealingRouter calls
``compute_decision_evidence`` once per dispatch to get the bundle that becomes
the row's prediction_json.

Plan: .windsurf/plans/l2-cascade-router-closed-loop-wiring-c4d8a1.md (W1.3)
Rule: .windsurf/rules/closed-loop-router-enforcement.md (row #4 L2/cascade)
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Any

from .confidence_scorer import HealTier

# ---------------------------------------------------------------------------
# Default cost / value table (bootstrap prior — env-overridable in HealingRouter)
# ---------------------------------------------------------------------------
# Cost in USD per dispatch, very rough order-of-magnitude bootstrap.
# Real numbers will be learned from outcome rows once N≥30 per tier accrues.
_DEFAULT_TIER_COST_USD: dict[HealTier, float] = {
    HealTier.HIGH: 0.0,         # local deterministic — free
    HealTier.MEDIUM: 0.001,     # local Qwen — electricity only
    HealTier.LOW: 0.05,         # Gemini Flash baseline (Pro = 10× via _PRO_REQUIRED_GATES)
    HealTier.HITL: 5.0,         # human review — high opportunity cost
}

# Value of a successful dispatch in USD-equivalent. A correct heal saves at
# minimum the cost of the highest tier; we use 2× LOW as a conservative floor.
DEFAULT_VALUE_PER_SUCCESS_USD: float = 0.10


# ---------------------------------------------------------------------------
# Fingerprint — stable hash over the routing cell
# ---------------------------------------------------------------------------
def fingerprint(
    *,
    failure_class: str,
    source_layer: str,
    error_code: str,
    retry_count: int,
) -> str:
    """Return a 12-hex-char SHA-256 prefix identifying the routing cell.

    The retry count is bucketed (0, 1-2, 3+) so calibration aggregates over
    semantically-equivalent retry pressures rather than exact integers.
    """
    if retry_count <= 0:
        retry_band = "r0"
    elif retry_count < 3:
        retry_band = "r1_2"
    else:
        retry_band = "r3p"
    raw = f"{failure_class}\x00{source_layer}\x00{error_code}\x00{retry_band}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Brier — per-row calibration component
# ---------------------------------------------------------------------------
def brier_component(predicted_p: float, actual_success: bool) -> float:
    """Return ``(predicted_p - actual)^2`` for one Bernoulli outcome.

    Aggregating the mean over a band of N rows yields the band's Brier score.
    Lower is better-calibrated (perfect calibration → 0.0; constant 0.5 prior → 0.25).
    """
    p = max(0.0, min(1.0, float(predicted_p)))
    actual = 1.0 if actual_success else 0.0
    diff = p - actual
    return diff * diff


def score_band_for(predicted_p: float, actual_success: bool, threshold: float = 0.5) -> str:
    """Return one of ``tp|fp|tn|fn`` for a (predicted, actual) pair.

    A row is "predicted-success" when ``predicted_p >= threshold``. The default
    threshold of 0.5 mirrors the calibration semantics: anything the router
    chose to dispatch with predicted P≥0.5 was a positive bet.
    """
    predicted_success = predicted_p >= threshold
    if predicted_success and actual_success:
        return "tp"
    if predicted_success and not actual_success:
        return "fp"
    if not predicted_success and actual_success:
        return "fn"
    return "tn"


# ---------------------------------------------------------------------------
# Wilson lower bound — promotion gate per §29 (wilson_lower ≥ 0.60 required)
# ---------------------------------------------------------------------------
def wilson_lower_bound(successes: int, total: int, *, z: float = 1.96) -> float:
    """Lower bound of the Wilson score interval for a binomial proportion.

    Returns 0.0 when ``total <= 0``. ``z=1.96`` corresponds to a 95% CI.
    """
    if total <= 0:
        return 0.0
    n = float(total)
    p = max(0.0, min(1.0, successes / n))
    denom = 1.0 + (z * z) / n
    centre = p + (z * z) / (2.0 * n)
    margin = z * math.sqrt((p * (1.0 - p) / n) + (z * z) / (4.0 * n * n))
    lower = (centre - margin) / denom
    return max(0.0, lower)


def wilson_upper_bound(successes: int, total: int, *, z: float = 1.96) -> float:
    """Upper bound of the Wilson score interval for a binomial proportion."""
    if total <= 0:
        return 1.0
    n = float(total)
    p = max(0.0, min(1.0, successes / n))
    denom = 1.0 + (z * z) / n
    centre = p + (z * z) / (2.0 * n)
    margin = z * math.sqrt((p * (1.0 - p) / n) + (z * z) / (4.0 * n * n))
    upper = (centre + margin) / denom
    return min(1.0, upper)


# ---------------------------------------------------------------------------
# Expected Utility
# ---------------------------------------------------------------------------
def compute_eu(
    *,
    predicted_p_success: float,
    tier: HealTier,
    value_per_success_usd: float = DEFAULT_VALUE_PER_SUCCESS_USD,
    cost_table: dict[HealTier, float] | None = None,
    cost_override_usd: float | None = None,
) -> float:
    """Expected Utility = P(success) × value − cost(tier).

    Args:
        predicted_p_success: Calibrated prior in [0, 1] for this tier on this
            cell (failure_class × source_layer × retry_band × error_code).
        tier: One of HealTier members.
        value_per_success_usd: Estimated USD value of one successful dispatch.
        cost_table: Override the default tier→USD cost mapping.
        cost_override_usd: When provided, bypass the table for this single
            call (e.g., live spot price from a billing API).

    Returns:
        EU in USD-equivalent. Higher is better. Negative means the tier is
        losing money in expectation.
    """
    p = max(0.0, min(1.0, float(predicted_p_success)))
    if cost_override_usd is not None:
        cost = float(cost_override_usd)
    else:
        table = cost_table if cost_table is not None else _DEFAULT_TIER_COST_USD
        cost = table.get(tier, 0.0)
    return p * value_per_success_usd - cost


# ---------------------------------------------------------------------------
# Provider mapping — string label per matrix contract
# ---------------------------------------------------------------------------
def provider_label(*, tier: HealTier, gemini_subtier: str, target_model: str) -> str:
    """Return the matrix-contract provider string for a routing decision.

    ``target_model`` is currently used only as a tiebreaker hint for future
    Qwen-variant disambiguation (e.g., distinguishing 14B from 32B once a
    learned router can route by size). Today it is folded into the label as
    a suffix only when the configured model id explicitly disagrees with the
    tier's canonical provider — otherwise the matrix-contract label wins.
    """
    if tier == HealTier.HIGH:
        return "deterministic"
    if tier == HealTier.MEDIUM:
        # Defensive: if the operator overrode VLLM_MODEL_NAME to a non-Qwen
        # model, surface that in the provider label so calibration doesn't
        # silently mix populations.
        model_lc = (target_model or "").lower()
        if model_lc and "qwen" not in model_lc:
            return f"local:{target_model}"
        return "qwen"
    if tier == HealTier.LOW:
        sub = (gemini_subtier or "").upper()
        if sub == "PRO":
            return "gemini_pro"
        return "gemini_flash"
    return "hitl"


# ---------------------------------------------------------------------------
# Decision evidence bundle — composes the prediction_json for the ledger row
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DecisionEvidence:
    """Bundle of scoring evidence accompanying a routing decision."""

    fingerprint_hex: str
    predicted_p_success: float
    eu_score: float
    provider: str
    extra: dict[str, Any] = field(default_factory=dict)

    def to_prediction_dict(
        self,
        *,
        decision_id: str,
        tier: HealTier,
        target_model: str,
        gate_applied: str,
        gemini_subtier: str,
        cost_demoted: bool,
        confidence_input: float,
        cost_budget_remaining_usd: float | None,
        app_name: str,
        vllm_healthy: bool | None,
    ) -> dict[str, Any]:
        """Render the prediction_json shape documented in the schema SQL."""
        out: dict[str, Any] = {
            "decision_id": decision_id,
            "tier": tier.name,
            "provider": self.provider,
            "target_model": target_model,
            "gate_applied": gate_applied,
            "gemini_subtier": gemini_subtier or "",
            "cost_demoted": bool(cost_demoted),
            "fingerprint": self.fingerprint_hex,
            "predicted_p_success": float(self.predicted_p_success),
            "eu_score": float(self.eu_score),
            "confidence_input": float(confidence_input),
            "cost_budget_remaining_usd": cost_budget_remaining_usd,
            "app_name": app_name,
            "vllm_healthy": vllm_healthy,
        }
        if self.extra:
            out.update(self.extra)
        return out


def compute_decision_evidence(
    *,
    tier: HealTier,
    gemini_subtier: str,
    target_model: str,
    confidence_input: float,
    failure_class: str,
    source_layer: str,
    error_code: str,
    retry_count: int,
    cost_override_usd: float | None = None,
) -> DecisionEvidence:
    """Construct the full evidence bundle for one routing decision.

    The ``predicted_p_success`` defaults to the heuristic confidence input —
    this is the bootstrap prior. Future waves will replace it with a learned
    posterior pulled from the ledger via ``LedgerConsulter``.
    """
    fp = fingerprint(
        failure_class=failure_class,
        source_layer=source_layer,
        error_code=error_code,
        retry_count=retry_count,
    )
    predicted_p = max(0.0, min(1.0, float(confidence_input)))
    eu = compute_eu(
        predicted_p_success=predicted_p,
        tier=tier,
        cost_override_usd=cost_override_usd,
    )
    provider = provider_label(
        tier=tier, gemini_subtier=gemini_subtier, target_model=target_model
    )
    return DecisionEvidence(
        fingerprint_hex=fp,
        predicted_p_success=predicted_p,
        eu_score=eu,
        provider=provider,
    )


__all__ = [
    "DEFAULT_VALUE_PER_SUCCESS_USD",
    "DecisionEvidence",
    "brier_component",
    "compute_decision_evidence",
    "compute_eu",
    "fingerprint",
    "provider_label",
    "score_band_for",
    "wilson_lower_bound",
    "wilson_upper_bound",
]
