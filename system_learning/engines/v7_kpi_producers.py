"""W9 producers for KPIs whose specs existed in V6 but had no emitter.

Each tracker exposes a small mutator API and a ``publish_kpi_sample(board)``
method. KPI emission is fail-soft (logged, never raised).

Producers:
    - ReplayDivergenceLocalizer  → REPLAY_DIVERGENCE_LOCALIZATION (V6)
    - SaturationWatcher          → SATURATION_WATCH (V6)
    - ExemplarHitTracker         → EXEMPLAR_HIT_RATE (V6)
    - GauntletFalsePromoteTracker→ GAUNTLET_FALSE_PROMOTE_RATE (V6)
    - HeldProposalAgingTracker   → HELD_PROPOSAL_AGING_P95 (V7)
    - GoldenSetRegressionTracker → GOLDEN_SET_REGRESSION_PASS_RATE (V7)
    - OrphanArtifactTracker      → ORPHAN_ARTIFACT_RATE (V7)
    - CitationDriftTracker       → CITATION_SUPPORT_DRIFT (V7)
    - AbstainCalibrationTracker  → ABSTAIN_REFUSAL_CALIBRATION_DRIFT (V7)

References: spec lines 1212-1237 (V7 KPI BOARD).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


def _import_v6():
    from system_learning.engines.v6_kpi_board import (  # noqa: PLC0415
        V6KPIName,
        V6KPISample,
    )
    return V6KPIName, V6KPISample


def _import_v7():
    from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
        V7KPIName,
        V7KPISample,
    )
    return V7KPIName, V7KPISample


# =====================================================================
# ReplayDivergenceLocalizer  (V6 REPLAY_DIVERGENCE_LOCALIZATION, S4A)
# =====================================================================


@dataclass
class ReplayDivergenceLocalizer:
    """Track replay-divergence localization rate.

    A ``failed_replay`` is one where the replay digest differed from the
    sealed digest. ``localized`` means the localizer pinpointed a span,
    surface, or configuration class as the cause. Spec lines 919-921.
    """

    _failed_replays: int = 0
    _localized_failures: int = 0
    _last_localizations: list[str] = field(default_factory=list)

    def record_replay(
        self,
        *,
        succeeded: bool,
        localized_to: str | None = None,
    ) -> None:
        if succeeded:
            return
        self._failed_replays += 1
        if localized_to:
            self._localized_failures += 1
            self._last_localizations.append(localized_to)

    @property
    def localization_rate(self) -> float:
        if self._failed_replays == 0:
            return 1.0
        return self._localized_failures / self._failed_replays

    def reset(self) -> None:
        self._failed_replays = 0
        self._localized_failures = 0
        self._last_localizations.clear()

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V6KPIName, V6KPISample = _import_v6()
            board.record(V6KPISample(
                name=V6KPIName.REPLAY_DIVERGENCE_LOCALIZATION,
                value=self.localization_rate, timestamp=time.time(),
                source="replay_divergence_localizer",
                metadata={"failed": self._failed_replays,
                          "localized": self._localized_failures},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break replay tracking
            logger.warning("v6_kpi_replay_divergence_localization_failed: %s", exc)


# =====================================================================
# SaturationWatcher  (V6 SATURATION_WATCH)
# =====================================================================


@dataclass
class SaturationWatcher:
    """Track ratio of capability evals static for >= 30 days.

    ``register_capability_eval(eval_id, last_changed_epoch)`` records a per-
    capability eval's last-modified time. ``compute(now)`` returns the
    static-ratio. Spec line 1234.
    """

    _evals: dict[str, float] = field(default_factory=dict)
    static_threshold_seconds: float = 30 * 86400.0

    def register_capability_eval(
        self, eval_id: str, last_changed_epoch: float,
    ) -> None:
        self._evals[eval_id] = last_changed_epoch

    def compute(self, *, now_epoch: float | None = None) -> float:
        ts = now_epoch if now_epoch is not None else time.time()
        if not self._evals:
            return 0.0
        static = sum(
            1 for last in self._evals.values()
            if (ts - last) >= self.static_threshold_seconds
        )
        return static / len(self._evals)

    def reset(self) -> None:
        self._evals.clear()

    def publish_kpi_sample(
        self, board: Any, *, now_epoch: float | None = None,
    ) -> None:
        try:
            V6KPIName, V6KPISample = _import_v6()
            ratio = self.compute(now_epoch=now_epoch)
            board.record(V6KPISample(
                name=V6KPIName.SATURATION_WATCH,
                value=ratio, timestamp=time.time(),
                source="saturation_watcher",
                metadata={"static_evals": int(ratio * len(self._evals)),
                          "total_evals": len(self._evals)},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break saturation tracking
            logger.warning("v6_kpi_saturation_watch_failed: %s", exc)


# =====================================================================
# ExemplarHitTracker  (V6 EXEMPLAR_HIT_RATE)
# =====================================================================


@dataclass
class ExemplarHitTracker:
    """Track ratio of eligible plans that consulted-and-used an exemplar.

    Spec line 1233: ``green: >= 20% eligible plans consult exemplar hit``.
    """

    _eligible_plans: int = 0
    _plans_with_exemplar_hit: int = 0

    def record_eligible_plan(self, *, used_exemplar: bool) -> None:
        self._eligible_plans += 1
        if used_exemplar:
            self._plans_with_exemplar_hit += 1

    @property
    def hit_rate(self) -> float:
        if self._eligible_plans == 0:
            return 0.0
        return self._plans_with_exemplar_hit / self._eligible_plans

    def reset(self) -> None:
        self._eligible_plans = 0
        self._plans_with_exemplar_hit = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V6KPIName, V6KPISample = _import_v6()
            board.record(V6KPISample(
                name=V6KPIName.EXEMPLAR_HIT_RATE,
                value=self.hit_rate, timestamp=time.time(),
                source="exemplar_hit_tracker",
                metadata={"hits": self._plans_with_exemplar_hit,
                          "eligible": self._eligible_plans},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break exemplar tracking
            logger.warning("v6_kpi_exemplar_hit_rate_failed: %s", exc)


# =====================================================================
# GauntletFalsePromoteTracker  (V6 GAUNTLET_FALSE_PROMOTE_RATE)
# =====================================================================


@dataclass
class GauntletFalsePromoteTracker:
    """Track ratio of approved promotions that had to be reverted.

    ``record_promotion(was_reverted=True)`` increments both the promotion
    count and the false-promote count. Spec line 1227: green ``<= 1%``.
    """

    _promotions: int = 0
    _reverted: int = 0

    def record_promotion(self, *, was_reverted: bool) -> None:
        self._promotions += 1
        if was_reverted:
            self._reverted += 1

    @property
    def false_promote_rate(self) -> float:
        if self._promotions == 0:
            return 0.0
        return self._reverted / self._promotions

    def reset(self) -> None:
        self._promotions = 0
        self._reverted = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V6KPIName, V6KPISample = _import_v6()
            board.record(V6KPISample(
                name=V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE,
                value=self.false_promote_rate, timestamp=time.time(),
                source="gauntlet_false_promote_tracker",
                metadata={"reverted": self._reverted,
                          "promotions": self._promotions},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break promote tracking
            logger.warning(
                "v6_kpi_gauntlet_false_promote_rate_failed: %s", exc
            )


# =====================================================================
# HeldProposalAgingTracker  (V7 HELD_PROPOSAL_AGING_P95)
# =====================================================================


@dataclass
class HeldProposalAgingTracker:
    """Track p95 hold age of currently-held proposals.

    Spec line 1226: ``p95 hold age <= agreed TTL``. Threshold defaulted to
    14 days in v7 board spec.
    """

    _hold_starts: dict[str, float] = field(default_factory=dict)

    def record_hold_start(self, proposal_id: str, *,
                          start_epoch: float | None = None) -> None:
        ts = start_epoch if start_epoch is not None else time.time()
        self._hold_starts[proposal_id] = ts

    def record_hold_release(self, proposal_id: str) -> None:
        self._hold_starts.pop(proposal_id, None)

    def p95_age_seconds(self, *, now_epoch: float | None = None) -> float:
        ts = now_epoch if now_epoch is not None else time.time()
        ages = sorted(ts - s for s in self._hold_starts.values())
        if not ages:
            return 0.0
        # Standard p95 by index — deterministic nearest-rank.
        idx = max(0, int(round(0.95 * (len(ages) - 1))))
        return ages[idx]

    def reset(self) -> None:
        self._hold_starts.clear()

    def publish_kpi_sample(
        self, board: Any, *, now_epoch: float | None = None,
    ) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7()
            value = self.p95_age_seconds(now_epoch=now_epoch)
            board.record(V7KPISample(
                name=V7KPIName.HELD_PROPOSAL_AGING_P95,
                value=value, timestamp=time.time(),
                source="held_proposal_aging_tracker",
                metadata={"held": len(self._hold_starts)},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break aging tracking
            logger.warning("v7_kpi_held_proposal_aging_failed: %s", exc)


# =====================================================================
# GoldenSetRegressionTracker  (V7 GOLDEN_SET_REGRESSION_PASS_RATE)
# =====================================================================


@dataclass
class GoldenSetRegressionTracker:
    """Track pass rate over critical golden cases.

    Spec line 1222: green ``>= 99%``.
    """

    _critical_total: int = 0
    _critical_passed: int = 0

    def record_golden_case(self, *, critical: bool, passed: bool) -> None:
        if critical:
            self._critical_total += 1
            if passed:
                self._critical_passed += 1

    @property
    def pass_rate(self) -> float:
        if self._critical_total == 0:
            return 1.0
        return self._critical_passed / self._critical_total

    def reset(self) -> None:
        self._critical_total = 0
        self._critical_passed = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7()
            board.record(V7KPISample(
                name=V7KPIName.GOLDEN_SET_REGRESSION_PASS_RATE,
                value=self.pass_rate, timestamp=time.time(),
                source="golden_set_regression_tracker",
                metadata={"passed": self._critical_passed,
                          "total": self._critical_total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break golden tracking
            logger.warning(
                "v7_kpi_golden_set_regression_pass_rate_failed: %s", exc
            )


# =====================================================================
# OrphanArtifactTracker  (V7 ORPHAN_ARTIFACT_RATE)
# =====================================================================


@dataclass
class OrphanArtifactTracker:
    """Track ratio of artifacts lacking trace/run linkage.

    Spec line 1214: green ``<= 0.5%``. Used as a follow-up to the
    ``RuntimeExhaustCollector`` defect counts to publish the per-window
    ratio rather than the per-bundle defect list.
    """

    _total_artifacts: int = 0
    _orphan_artifacts: int = 0

    def record_artifact(self, *, is_orphan: bool) -> None:
        self._total_artifacts += 1
        if is_orphan:
            self._orphan_artifacts += 1

    @property
    def orphan_rate(self) -> float:
        if self._total_artifacts == 0:
            return 0.0
        return self._orphan_artifacts / self._total_artifacts

    def reset(self) -> None:
        self._total_artifacts = 0
        self._orphan_artifacts = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7()
            board.record(V7KPISample(
                name=V7KPIName.ORPHAN_ARTIFACT_RATE,
                value=self.orphan_rate, timestamp=time.time(),
                source="orphan_artifact_tracker",
                metadata={"orphans": self._orphan_artifacts,
                          "total": self._total_artifacts},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break orphan tracking
            logger.warning("v7_kpi_orphan_artifact_rate_failed: %s", exc)


# =====================================================================
# CitationDriftTracker  (V7 CITATION_SUPPORT_DRIFT)
# =====================================================================


@dataclass
class CitationDriftTracker:
    """Track citation-support precision drift relative to baseline.

    Spec line 1235: ``support precision stays within threshold``.
    Records baseline and current precision; emits the absolute drift
    as the KPI value.
    """

    baseline_precision: float = 1.0
    _current_precisions: list[float] = field(default_factory=list)

    def record_precision_sample(self, precision: float) -> None:
        self._current_precisions.append(precision)

    @property
    def drift(self) -> float:
        if not self._current_precisions:
            return 0.0
        avg = sum(self._current_precisions) / len(self._current_precisions)
        return abs(self.baseline_precision - avg)

    def reset(self) -> None:
        self._current_precisions.clear()

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7()
            board.record(V7KPISample(
                name=V7KPIName.CITATION_SUPPORT_DRIFT,
                value=self.drift, timestamp=time.time(),
                source="citation_drift_tracker",
                metadata={"baseline": self.baseline_precision,
                          "samples": len(self._current_precisions)},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break drift tracking
            logger.warning("v7_kpi_citation_support_drift_failed: %s", exc)


# =====================================================================
# AbstainCalibrationTracker  (V7 ABSTAIN_REFUSAL_CALIBRATION_DRIFT)
# =====================================================================


@dataclass
class AbstainCalibrationTracker:
    """Track false abstain/refusal rate against rubric band.

    Spec line 1236: ``false abstain/refusal within rubric band``.
    Records per-decision (was_correct_to_abstain). Drift = abs(rate - target).
    """

    target_rate: float = 0.05
    _abstains: int = 0
    _false_abstains: int = 0

    def record_abstain_decision(self, *, was_correct: bool) -> None:
        self._abstains += 1
        if not was_correct:
            self._false_abstains += 1

    @property
    def calibration_drift(self) -> float:
        if self._abstains == 0:
            return 0.0
        rate = self._false_abstains / self._abstains
        return abs(rate - self.target_rate)

    def reset(self) -> None:
        self._abstains = 0
        self._false_abstains = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            V7KPIName, V7KPISample = _import_v7()
            board.record(V7KPISample(
                name=V7KPIName.ABSTAIN_REFUSAL_CALIBRATION_DRIFT,
                value=self.calibration_drift, timestamp=time.time(),
                source="abstain_calibration_tracker",
                metadata={"target": self.target_rate,
                          "false_abstains": self._false_abstains,
                          "total": self._abstains},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break abstain tracking
            logger.warning(
                "v7_kpi_abstain_refusal_calibration_drift_failed: %s", exc
            )


__all__ = [
    "ReplayDivergenceLocalizer",
    "SaturationWatcher",
    "ExemplarHitTracker",
    "GauntletFalsePromoteTracker",
    "HeldProposalAgingTracker",
    "GoldenSetRegressionTracker",
    "OrphanArtifactTracker",
    "CitationDriftTracker",
    "AbstainCalibrationTracker",
]
