"""Judge drift monitor — detects calibration drift between judge and human gold set.

Consumes the report emitted by
``agentic_core.evaluation.judges.calibration.summarize_judge_vs_human``
and returns structured drift events suitable for OTel emission.

A drift event fires when any of:
  - Cohen's kappa drops below the configured floor for any dimension.
  - Krippendorff's alpha drops below floor for any dimension.
  - Judge ``unknown_rate`` for a dimension exceeds that dimension's
    ``unknown_budget`` (configured in ``config/judges/rubrics.yaml``).
  - Kappa or alpha moves by more than ``delta_alert_threshold``
    compared to the previous calibration report (regression detection).

Design notes:
  - This module is intentionally read-only; it does not mutate any
    production state. Alert emission (OTel spans, Notion writeback) is
    the caller's responsibility.
  - Compatible with the existing L6_observability layout — lives next
    to ``consensus_otel.py`` and ``heal_router_otel.py``.
  - No external dependencies; stdlib only.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


DEFAULT_FLOORS: dict[str, float] = {
    "kappa_floor": 0.60,
    "alpha_floor": 0.60,
    "delta_alert_threshold": 0.10,
}


@dataclass(frozen=True)
class DriftEvent:
    """One drift signal surfaced by the monitor."""

    kind: str            # 'kappa_below_floor' | 'alpha_below_floor' |
                         # 'unknown_over_budget' | 'kappa_regression' |
                         # 'alpha_regression'
    dimension: str
    current: float
    previous: float | None
    threshold: float
    severity: str        # 'HIGH' | 'MEDIUM' | 'LOW'
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "dimension": self.dimension,
            "current": self.current,
            "previous": self.previous,
            "threshold": self.threshold,
            "severity": self.severity,
            "detail": self.detail,
        }


@dataclass
class JudgeDriftReport:
    """Aggregated drift report over one or more dimensions."""

    judge_id: str
    n_items: int
    events: list[DriftEvent] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return any(e.severity in {"HIGH", "MEDIUM"} for e in self.events)

    @property
    def worst_severity(self) -> str:
        if any(e.severity == "HIGH" for e in self.events):
            return "HIGH"
        if any(e.severity == "MEDIUM" for e in self.events):
            return "MEDIUM"
        if self.events:
            return "LOW"
        return "NONE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "judge_id": self.judge_id,
            "n_items": self.n_items,
            "has_drift": self.has_drift,
            "worst_severity": self.worst_severity,
            "events": [e.to_dict() for e in self.events],
        }


def _severity_for_below_floor(current: float, floor: float) -> str:
    if current < floor - 0.15:
        return "HIGH"
    if current < floor - 0.05:
        return "MEDIUM"
    return "LOW"


def _severity_for_delta(delta: float) -> str:
    if delta >= 0.20:
        return "HIGH"
    if delta >= 0.10:
        return "MEDIUM"
    return "LOW"


def analyze_drift(
    current: dict[str, Any],
    previous: dict[str, Any] | None = None,
    unknown_budgets: dict[str, float] | None = None,
    floors: dict[str, float] | None = None,
    judge_id: str = "",
) -> JudgeDriftReport:
    """Analyze one calibration report vs optional previous baseline.

    ``current`` / ``previous`` are dicts as produced by
    :func:`agentic_core.evaluation.judges.calibration.summarize_judge_vs_human`'s
    ``to_dict()`` method.

    ``unknown_budgets`` maps dimension name → allowed unknown fraction
    (pulled from ``config/judges/rubrics.yaml``). Dimensions not in the
    map have no unknown-budget check.

    Returns a :class:`JudgeDriftReport` with zero or more
    :class:`DriftEvent`s.
    """
    floors_ = {**DEFAULT_FLOORS, **(floors or {})}
    kappa_floor = floors_["kappa_floor"]
    alpha_floor = floors_["alpha_floor"]
    delta_thresh = floors_["delta_alert_threshold"]
    budgets = unknown_budgets or {}

    events: list[DriftEvent] = []

    current_kappa = current.get("dimension_kappa", {})
    current_alpha = current.get("dimension_alpha", {})
    current_unknown = current.get("unknown_rate_by_dim", {})
    previous_kappa = (previous or {}).get("dimension_kappa", {})
    previous_alpha = (previous or {}).get("dimension_alpha", {})

    for dim, kappa in current_kappa.items():
        if not isinstance(kappa, (int, float)) or kappa != kappa:  # NaN guard
            continue
        if kappa < kappa_floor:
            events.append(
                DriftEvent(
                    kind="kappa_below_floor",
                    dimension=dim,
                    current=float(kappa),
                    previous=previous_kappa.get(dim),
                    threshold=kappa_floor,
                    severity=_severity_for_below_floor(kappa, kappa_floor),
                    detail=f"kappa={kappa:.3f} < floor {kappa_floor:.2f}",
                ),
            )
        prev = previous_kappa.get(dim)
        if isinstance(prev, (int, float)) and prev == prev:
            delta = prev - kappa
            if delta >= delta_thresh:
                events.append(
                    DriftEvent(
                        kind="kappa_regression",
                        dimension=dim,
                        current=float(kappa),
                        previous=float(prev),
                        threshold=delta_thresh,
                        severity=_severity_for_delta(delta),
                        detail=f"kappa dropped by {delta:.3f}",
                    ),
                )

    for dim, alpha in current_alpha.items():
        if not isinstance(alpha, (int, float)) or alpha != alpha:
            continue
        if alpha < alpha_floor:
            events.append(
                DriftEvent(
                    kind="alpha_below_floor",
                    dimension=dim,
                    current=float(alpha),
                    previous=previous_alpha.get(dim),
                    threshold=alpha_floor,
                    severity=_severity_for_below_floor(alpha, alpha_floor),
                    detail=f"alpha={alpha:.3f} < floor {alpha_floor:.2f}",
                ),
            )
        prev = previous_alpha.get(dim)
        if isinstance(prev, (int, float)) and prev == prev:
            delta = prev - alpha
            if delta >= delta_thresh:
                events.append(
                    DriftEvent(
                        kind="alpha_regression",
                        dimension=dim,
                        current=float(alpha),
                        previous=float(prev),
                        threshold=delta_thresh,
                        severity=_severity_for_delta(delta),
                        detail=f"alpha dropped by {delta:.3f}",
                    ),
                )

    for dim, rate in current_unknown.items():
        budget = budgets.get(dim)
        if budget is None:
            continue
        if not isinstance(rate, (int, float)):
            continue
        if rate > budget:
            events.append(
                DriftEvent(
                    kind="unknown_over_budget",
                    dimension=dim,
                    current=float(rate),
                    previous=None,
                    threshold=float(budget),
                    severity="HIGH" if rate > budget + 0.10 else "MEDIUM",
                    detail=f"unknown_rate={rate:.3f} > budget {budget:.2f}",
                ),
            )

    return JudgeDriftReport(
        judge_id=judge_id,
        n_items=int(current.get("n_items", 0)),
        events=events,
    )


def load_report(path: str | Path) -> dict[str, Any]:
    """Convenience loader for calibration reports stored as JSON."""
    text = Path(path).read_text(encoding="utf-8")
    data: Any = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Report at {path} is not a JSON object")
    return data


__all__ = [
    "DEFAULT_FLOORS",
    "DriftEvent",
    "JudgeDriftReport",
    "analyze_drift",
    "load_report",
]
