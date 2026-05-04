"""apps_lic.engines.ab_variant_engine — D5-P1 + DS3.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W6 D5-P1
      Updated: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W4 DS3-P1

Holdout assignment and variant scoring for A/B testing of outreach strategies.
Non-blocking: if this engine is disabled or raises, callers MUST proceed with
the control arm unchanged. No provider calls. No durable writes from this
module — wiring to L6 shadow eval is done by the caller.

Surfaces
--------
- ABVariantEngine.assign(request_id, variant_config) → ABVariantAssignment
  Deterministic hash-based holdout assignment. Same request_id always maps
  to the same bucket so holdout is stable across retries.
- ABVariantEngine.score(assignment, outcome) → ABVariantScore
  Lightweight scoring record that the caller passes to L6 regret/promo.

Design constraints (D5-P1)
---------------------------
- Decision-only: no durable writes, no provider API calls, no subprocess.
- Config-gated: disabled without AB_VARIANT_ENABLED=1.
- Deterministic: sha256(request_id + salt) % 100 → bucket [0, 99].
- Non-blocking: engine.assign() never raises; returns disabled sentinel if
  AB_VARIANT_ENABLED is unset or config is absent.

DS3-P1: Real-traffic promotion gate
------------------------------------
REQUIRES_REAL_TRAFFIC = True signals that production promotion decisions
require real outreach traffic (n ≥ 30 per arm) rather than synthetic data.

ABTrafficAccumulator
  - Accepts ABVariantScore records from the caller.
  - Tracks per-experiment, per-arm sample counts.
  - Caller feeds real-traffic scores; accumulator is NOT a database.

ABPromotionGate
  - Evaluates whether accumulated traffic is sufficient for a promotion
    decision. Refuses when any arm has n < min_n (default 30).
  - Returns ABPromotionDecision with verdict ("promote", "underpowered",
    "no_data") plus per-arm counts and reasons.
  - Decision-only: no writes. Caller routes verdict to L6 promo.
"""

from __future__ import annotations

import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "ab_variant_policy.yaml"

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_config() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config, fall through to defaults.
        return {}


def _enabled() -> bool:
    return os.environ.get("AB_VARIANT_ENABLED", "").strip() == "1"


# ---------------------------------------------------------------------------
# Arm assignment
# ---------------------------------------------------------------------------

ARM_CONTROL = "control"
ARM_TREATMENT = "treatment"
ARM_HOLDOUT = "holdout"  # withheld from treatment — statistical control group

VALID_ARMS = frozenset({ARM_CONTROL, ARM_TREATMENT, ARM_HOLDOUT})


def _hash_bucket(request_id: str, salt: str = "") -> int:
    """Return deterministic bucket in [0, 99] for a request_id."""
    blob = f"{request_id}:{salt}".encode()
    return int(hashlib.sha256(blob).hexdigest(), 16) % 100


@dataclass(frozen=True)
class ABVariantConfig:
    """Per-experiment variant configuration.

    Fields
    ------
    experiment_id    : stable experiment identifier.
    treatment_pct    : percent [0–100] of traffic in treatment arm.
    holdout_pct      : percent [0–100] of traffic in holdout arm.
    salt             : per-experiment salt for hash independence.
    """

    experiment_id: str
    treatment_pct: int = 50
    holdout_pct: int = 10
    salt: str = ""

    def __post_init__(self) -> None:
        total = self.treatment_pct + self.holdout_pct
        if total > 100:
            raise ValueError(
                f"treatment_pct ({self.treatment_pct}) + holdout_pct "
                f"({self.holdout_pct}) > 100"
            )


@dataclass(frozen=True)
class ABVariantAssignment:
    """Result of a single holdout assignment.

    Fields
    ------
    enabled          : False when AB_VARIANT_ENABLED is unset.
    experiment_id    : mirrors ABVariantConfig.experiment_id.
    request_id       : caller-provided stable request ID.
    bucket           : hash bucket [0, 99].
    arm              : "control" | "treatment" | "holdout".
    """

    enabled: bool
    experiment_id: str
    request_id: str
    bucket: int
    arm: str


@dataclass(frozen=True)
class ABVariantScore:
    """Outcome score for one variant assignment.

    Passed by caller to L6 shadow eval / regret / promotion.

    Fields
    ------
    experiment_id   : mirrors assignment.
    arm             : mirrors assignment.
    request_id      : mirrors assignment.
    reward          : scalar reward in [0, 1].
    outcome_label   : human-readable outcome (e.g. "positive_response").
    """

    experiment_id: str
    arm: str
    request_id: str
    reward: float
    outcome_label: str = ""


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class ABVariantEngine:
    """Deterministic holdout assignment and lightweight variant scoring.

    Usage::

        engine = ABVariantEngine()
        cfg = ABVariantConfig(experiment_id="arc_v2", treatment_pct=50)
        assignment = engine.assign(request_id="req-001", variant_config=cfg)
        # ... run the assigned arm ...
        score = engine.score(assignment, reward=1.0, outcome_label="opened")
        # caller passes score to L6 regret / promotion gate
    """

    def __init__(self, config: dict | None = None) -> None:
        self._config = config if config is not None else _load_config()

    def assign(
        self,
        request_id: str,
        variant_config: ABVariantConfig | None = None,
    ) -> ABVariantAssignment:
        """Deterministically assign request_id to a holdout arm.

        Never raises. Returns disabled sentinel when AB_VARIANT_ENABLED unset.
        """
        if not _enabled():
            return ABVariantAssignment(
                enabled=False,
                experiment_id=getattr(variant_config, "experiment_id", ""),
                request_id=request_id,
                bucket=-1,
                arm=ARM_CONTROL,
            )

        if variant_config is None:
            # Default single-experiment config from policy YAML
            eid = self._config.get("default_experiment_id", "default")
            tpct = int(self._config.get("treatment_pct", 50))
            hpct = int(self._config.get("holdout_pct", 10))
            salt = str(self._config.get("salt", ""))
            variant_config = ABVariantConfig(
                experiment_id=eid,
                treatment_pct=tpct,
                holdout_pct=hpct,
                salt=salt,
            )

        bucket = _hash_bucket(request_id, variant_config.salt)

        if bucket < variant_config.holdout_pct:
            arm = ARM_HOLDOUT
        elif bucket < variant_config.holdout_pct + variant_config.treatment_pct:
            arm = ARM_TREATMENT
        else:
            arm = ARM_CONTROL

        return ABVariantAssignment(
            enabled=True,
            experiment_id=variant_config.experiment_id,
            request_id=request_id,
            bucket=bucket,
            arm=arm,
        )

    def score(
        self,
        assignment: ABVariantAssignment,
        *,
        reward: float,
        outcome_label: str = "",
    ) -> ABVariantScore:
        """Build a variant score record from an assignment and a reward."""
        return ABVariantScore(
            experiment_id=assignment.experiment_id,
            arm=assignment.arm,
            request_id=assignment.request_id,
            reward=float(max(0.0, min(1.0, reward))),
            outcome_label=outcome_label,
        )


# ---------------------------------------------------------------------------
# DS3-P1: Real-traffic flag
# ---------------------------------------------------------------------------

REQUIRES_REAL_TRAFFIC: bool = True
"""Promotion decisions require real outreach traffic (n ≥ 30 per arm).

Set to False ONLY in controlled test environments where synthetic traffic
is explicitly accepted. Production callers must leave this True.
"""

MIN_ARM_N_DEFAULT: int = 30
"""Default minimum sample count per arm for a valid promotion decision."""


# ---------------------------------------------------------------------------
# DS3-P1: Per-arm traffic accumulation
# ---------------------------------------------------------------------------


@dataclass
class ABTrafficAccumulator:
    """Accumulates ABVariantScore records per experiment and arm.

    Decision-only: does NOT write to any durable store. Caller owns the
    accumulator lifetime and feeds it real-traffic scores as they arrive.

    Usage::

        acc = ABTrafficAccumulator()
        acc.record(score)               # called per outreach outcome
        counts = acc.arm_counts("exp1") # {"control": 18, "treatment": 21}
    """

    # experiment_id → arm → count
    _counts: Dict[str, Dict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )
    # experiment_id → arm → sum of rewards (for mean reward reporting)
    _rewards: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )

    def record(self, score: "ABVariantScore") -> None:
        """Record one ABVariantScore observation."""
        eid = score.experiment_id
        arm = score.arm
        self._counts[eid][arm] += 1
        self._rewards[eid][arm] += float(score.reward)

    def arm_counts(self, experiment_id: str) -> Dict[str, int]:
        """Return per-arm sample counts for an experiment."""
        return dict(self._counts.get(experiment_id, {}))

    def arm_mean_reward(self, experiment_id: str) -> Dict[str, float]:
        """Return per-arm mean reward for an experiment (0.0 when n=0)."""
        counts = self._counts.get(experiment_id, {})
        rewards = self._rewards.get(experiment_id, {})
        result: Dict[str, float] = {}
        for arm, n in counts.items():
            result[arm] = rewards[arm] / n if n > 0 else 0.0
        return result

    def total_n(self, experiment_id: str) -> int:
        """Total observations across all arms for an experiment."""
        return sum(self._counts.get(experiment_id, {}).values())

    def reset(self, experiment_id: str | None = None) -> None:
        """Clear accumulator for one experiment or all if None."""
        if experiment_id is None:
            self._counts.clear()
            self._rewards.clear()
        else:
            self._counts.pop(experiment_id, None)
            self._rewards.pop(experiment_id, None)


# ---------------------------------------------------------------------------
# DS3-P1: Promotion gate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ABPromotionDecision:
    """Result of ABPromotionGate.evaluate().

    Fields
    ------
    experiment_id  : experiment evaluated.
    verdict        : "promote" | "underpowered" | "no_data" | "disabled".
    arm_counts     : per-arm sample counts at evaluation time.
    arm_rewards    : per-arm mean reward at evaluation time.
    reasons        : human-readable reasons for the verdict.
    min_n_required : configured minimum per-arm threshold.
    requires_real_traffic : True when REQUIRES_REAL_TRAFFIC is set.
    """

    experiment_id: str
    verdict: str
    arm_counts: Dict[str, int]
    arm_rewards: Dict[str, float]
    reasons: tuple
    min_n_required: int
    requires_real_traffic: bool


VERDICT_PROMOTE = "promote"
VERDICT_UNDERPOWERED = "underpowered"
VERDICT_NO_DATA = "no_data"
VERDICT_DISABLED = "disabled"

VALID_VERDICTS = frozenset({
    VERDICT_PROMOTE,
    VERDICT_UNDERPOWERED,
    VERDICT_NO_DATA,
    VERDICT_DISABLED,
})


class ABPromotionGate:
    """Evaluates whether accumulated traffic is sufficient for promotion.

    Refuses to emit PROMOTE when any eligible arm has n < min_n.

    Design constraints:
    - Decision-only: no durable writes.
    - Non-blocking: evaluate() never raises.
    - Respects REQUIRES_REAL_TRAFFIC: when True, synthetic-traffic
      accumulators MUST NOT be used as input to a real promotion decision.
      (Enforcement is caller responsibility; this gate surfaces the flag.)

    Usage::

        gate = ABPromotionGate()
        decision = gate.evaluate(
            experiment_id="arc_v2",
            accumulator=acc,
            arms_to_compare=(ARM_CONTROL, ARM_TREATMENT),
        )
        if decision.verdict == VERDICT_PROMOTE:
            # route to L6 promo
    """

    def __init__(
        self,
        min_n: int = MIN_ARM_N_DEFAULT,
        config: dict | None = None,
    ) -> None:
        self._min_n = min_n
        if config is not None:
            self._min_n = int(config.get("min_n_per_arm", min_n))

    def evaluate(
        self,
        experiment_id: str,
        accumulator: ABTrafficAccumulator,
        arms_to_compare: tuple[str, ...] = (ARM_CONTROL, ARM_TREATMENT),
    ) -> ABPromotionDecision:
        """Evaluate promotion readiness for an experiment.

        Parameters
        ----------
        experiment_id   : experiment to evaluate.
        accumulator     : ABTrafficAccumulator populated with real scores.
        arms_to_compare : arms that must each reach min_n (default: control + treatment).
        """
        counts = accumulator.arm_counts(experiment_id)
        rewards = accumulator.arm_mean_reward(experiment_id)
        reasons: list[str] = []

        if not counts:
            return ABPromotionDecision(
                experiment_id=experiment_id,
                verdict=VERDICT_NO_DATA,
                arm_counts={},
                arm_rewards={},
                reasons=("no observations recorded for this experiment",),
                min_n_required=self._min_n,
                requires_real_traffic=REQUIRES_REAL_TRAFFIC,
            )

        underpowered_arms: list[str] = []
        for arm in arms_to_compare:
            n = counts.get(arm, 0)
            if n < self._min_n:
                underpowered_arms.append(arm)
                reasons.append(
                    f"arm '{arm}' has n={n} < min_n={self._min_n} "
                    "(REQUIRES_REAL_TRAFFIC=True)"
                    if REQUIRES_REAL_TRAFFIC else
                    f"arm '{arm}' has n={n} < min_n={self._min_n}"
                )

        if underpowered_arms:
            return ABPromotionDecision(
                experiment_id=experiment_id,
                verdict=VERDICT_UNDERPOWERED,
                arm_counts=counts,
                arm_rewards=rewards,
                reasons=tuple(reasons),
                min_n_required=self._min_n,
                requires_real_traffic=REQUIRES_REAL_TRAFFIC,
            )

        return ABPromotionDecision(
            experiment_id=experiment_id,
            verdict=VERDICT_PROMOTE,
            arm_counts=counts,
            arm_rewards=rewards,
            reasons=(f"all arms reached min_n={self._min_n}",),
            min_n_required=self._min_n,
            requires_real_traffic=REQUIRES_REAL_TRAFFIC,
        )


__all__ = [
    "ABVariantEngine",
    "ABVariantAssignment",
    "ABVariantConfig",
    "ABVariantScore",
    "ABTrafficAccumulator",
    "ABPromotionGate",
    "ABPromotionDecision",
    "ARM_CONTROL",
    "ARM_TREATMENT",
    "ARM_HOLDOUT",
    "VALID_ARMS",
    "VALID_VERDICTS",
    "VERDICT_PROMOTE",
    "VERDICT_UNDERPOWERED",
    "VERDICT_NO_DATA",
    "VERDICT_DISABLED",
    "REQUIRES_REAL_TRAFFIC",
    "MIN_ARM_N_DEFAULT",
]
