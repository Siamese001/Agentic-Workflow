"""Threshold-sweep harness — PR curves + optimal-threshold selection.

W0.P2 deposit. Consumes a :class:`~tools.calibration.feature_vector.CalibrationFixture`
and produces a :class:`SweepReport` with a per-threshold precision/recall/F1
table plus the optimal threshold under several objectives:

    - ``max_f1``           : highest F1 across the sweep
    - ``precision_first``  : highest recall subject to precision >= ``precision_floor``
    - ``recall_first``     : highest precision subject to recall >= ``recall_floor``
    - ``vertex_default``   : first threshold >= 0.7 (Vertex dynamic-retrieval default)

Vendor alignment:

- OpenAI Prompt Caching 201 §3.1 — compute hit ratio rollups (R1A/R1B).
- Vertex AI dynamic retrieval — default threshold 0.7, tune on representative set.
- Industry consensus — precision-critical 0.94, recall-optimized 0.88
  (VentureBeat / TrueFoundry / arXiv 2411.05276).

No live code is wired — W3 will consume the emitted YAML/JSON report.
Progress bar via :mod:`tools.progress_display` per constitutional §16.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from tools.calibration.feature_vector import CalibrationFixture, FixtureRecord, PathSignal
from tools.progress_display import ProgressReporter

Objective = Literal["max_f1", "precision_first", "recall_first", "vertex_default"]

DEFAULT_SWEEP_POINTS: int = 101
"""Resolution of the threshold sweep — 0.00, 0.01, ..., 1.00 by default."""

VERTEX_DEFAULT_THRESHOLD: float = 0.70
"""Vertex AI dynamic-retrieval default threshold (docs.cloud.google.com)."""


@dataclass(frozen=True)
class PRPoint:
    """One point on the PR curve."""

    threshold: float
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    precision: float
    recall: float
    f1: float
    support_positive: int
    support_negative: int


@dataclass(frozen=True)
class SweepReport:
    """Full sweep result for one fixture (optionally one namespace)."""

    path: PathSignal
    signal: str
    namespace: str
    invert_score: bool
    sample_count: int
    positive_count: int
    negative_count: int
    points: tuple[PRPoint, ...]
    optimal_max_f1: PRPoint | None = None
    optimal_precision_first: PRPoint | None = None
    optimal_recall_first: PRPoint | None = None
    vertex_default: PRPoint | None = None
    params: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Serialize to a plain dict (JSON-safe)."""
        return {
            "path": self.path,
            "signal": self.signal,
            "namespace": self.namespace,
            "invert_score": self.invert_score,
            "sample_count": self.sample_count,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "points": [asdict(p) for p in self.points],
            "optimal_max_f1": asdict(self.optimal_max_f1) if self.optimal_max_f1 else None,
            "optimal_precision_first": (
                asdict(self.optimal_precision_first) if self.optimal_precision_first else None
            ),
            "optimal_recall_first": (
                asdict(self.optimal_recall_first) if self.optimal_recall_first else None
            ),
            "vertex_default": asdict(self.vertex_default) if self.vertex_default else None,
            "params": dict(self.params),
        }


def _classify(record: FixtureRecord, threshold: float, invert: bool) -> bool:
    """Return True if the gate FIRES (predicts positive) at ``threshold``.

    When ``invert`` is True (R5 abstain semantics), LOW scores fire.
    """
    if invert:
        return record.score <= threshold
    return record.score >= threshold


def _pr_at_threshold(
    records: tuple[FixtureRecord, ...],
    threshold: float,
    invert: bool,
) -> PRPoint:
    """Compute a single PR point at one threshold."""
    tp = fp = tn = fn = 0
    pos = neg = 0
    for rec in records:
        predicted_positive = _classify(rec, threshold, invert)
        if rec.label:
            pos += 1
            if predicted_positive:
                tp += 1
            else:
                fn += 1
        else:
            neg += 1
            if predicted_positive:
                fp += 1
            else:
                tn += 1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return PRPoint(
        threshold=round(threshold, 6),
        true_positive=tp,
        false_positive=fp,
        true_negative=tn,
        false_negative=fn,
        precision=round(precision, 6),
        recall=round(recall, 6),
        f1=round(f1, 6),
        support_positive=pos,
        support_negative=neg,
    )


def sweep_thresholds(
    fixture: CalibrationFixture,
    *,
    namespace: str = "",
    points: int = DEFAULT_SWEEP_POINTS,
    precision_floor: float = 0.90,
    recall_floor: float = 0.80,
    show_progress: bool = True,
) -> SweepReport:
    """Sweep thresholds in [0,1] and return a :class:`SweepReport`.

    Args:
        fixture: Loaded calibration fixture.
        namespace: Restrict sweep to a namespace (empty = all records).
        points: Number of equally-spaced threshold points (>=2).
        precision_floor: Minimum precision for ``optimal_precision_first``.
        recall_floor: Minimum recall for ``optimal_recall_first``.
        show_progress: Display progress bar (constitutional §16).

    Raises:
        ValueError: points < 2, floors outside [0,1], or empty fixture.
    """
    if points < 2:
        raise ValueError(f"points must be >= 2, got {points}")
    if not 0.0 <= precision_floor <= 1.0:
        raise ValueError(f"precision_floor must be in [0,1], got {precision_floor}")
    if not 0.0 <= recall_floor <= 1.0:
        raise ValueError(f"recall_floor must be in [0,1], got {recall_floor}")

    records = fixture.by_namespace(namespace)
    if not records:
        raise ValueError(
            f"No records for path={fixture.path} namespace={namespace!r} — empty sweep",
        )

    positive_count = sum(1 for r in records if r.label)
    negative_count = len(records) - positive_count

    thresholds = [round(i / (points - 1), 6) for i in range(points)]

    reporter: ProgressReporter | None = None
    if show_progress and points >= 10:
        reporter = ProgressReporter(
            total=points,
            label=f"sweep:{fixture.path}:{namespace or 'ALL'}",
            unit="thr",
        )

    sweep_points: list[PRPoint] = []
    try:
        for thr in thresholds:
            sweep_points.append(_pr_at_threshold(records, thr, fixture.invert_score))
            if reporter is not None:
                reporter.update()
        if reporter is not None:
            reporter.done()
    except BaseException:
        if reporter is not None:
            reporter.fail("sweep interrupted")
        raise

    frozen_points = tuple(sweep_points)

    return SweepReport(
        path=fixture.path,
        signal=fixture.signal,
        namespace=namespace,
        invert_score=fixture.invert_score,
        sample_count=len(records),
        positive_count=positive_count,
        negative_count=negative_count,
        points=frozen_points,
        optimal_max_f1=select_optimal_threshold(frozen_points, "max_f1"),
        optimal_precision_first=select_optimal_threshold(
            frozen_points,
            "precision_first",
            precision_floor=precision_floor,
        ),
        optimal_recall_first=select_optimal_threshold(
            frozen_points,
            "recall_first",
            recall_floor=recall_floor,
        ),
        vertex_default=select_optimal_threshold(frozen_points, "vertex_default"),
        params={
            "points": float(points),
            "precision_floor": precision_floor,
            "recall_floor": recall_floor,
        },
    )


def select_optimal_threshold(
    points: tuple[PRPoint, ...],
    objective: Objective,
    *,
    precision_floor: float = 0.90,
    recall_floor: float = 0.80,
) -> PRPoint | None:
    """Pick the best PR point under ``objective``.

    Returns ``None`` when no point satisfies the constraint
    (e.g. ``precision_first`` with an unreachable floor).
    """
    if not points:
        return None

    if objective == "max_f1":
        # Argmax over F1; break ties by higher precision, then higher threshold.
        return max(points, key=lambda p: (p.f1, p.precision, p.threshold))

    if objective == "precision_first":
        eligible = [p for p in points if p.precision >= precision_floor]
        if not eligible:
            return None
        return max(eligible, key=lambda p: (p.recall, p.precision, p.threshold))

    if objective == "recall_first":
        eligible = [p for p in points if p.recall >= recall_floor]
        if not eligible:
            return None
        return max(eligible, key=lambda p: (p.precision, p.recall, -p.threshold))

    if objective == "vertex_default":
        eligible = [p for p in points if p.threshold >= VERTEX_DEFAULT_THRESHOLD]
        if not eligible:
            return None
        # Closest threshold at or above 0.7.
        return min(eligible, key=lambda p: (p.threshold, -p.f1))

    raise ValueError(f"Unknown objective: {objective!r}")


def write_report(report: SweepReport, output_path: Path | str) -> Path:
    """Write the report to ``output_path`` as JSON. Returns the resolved path."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        json.dump(report.to_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return out


def format_report_table(report: SweepReport) -> str:
    """Render a compact textual summary of the report (stdout-friendly)."""
    lines = [
        f"path={report.path} signal={report.signal} namespace={report.namespace or 'ALL'}",
        (
            f"samples={report.sample_count} "
            f"pos={report.positive_count} neg={report.negative_count} "
            f"invert={report.invert_score}"
        ),
        "",
        "optima:",
    ]
    named = (
        ("max_f1", report.optimal_max_f1),
        ("precision_first", report.optimal_precision_first),
        ("recall_first", report.optimal_recall_first),
        ("vertex_default", report.vertex_default),
    )
    for name, point in named:
        if point is None:
            lines.append(f"  {name:<18s} -> (none satisfies constraint)")
            continue
        lines.append(
            f"  {name:<18s} -> thr={point.threshold:.3f} "
            f"P={point.precision:.3f} R={point.recall:.3f} F1={point.f1:.3f} "
            f"(TP={point.true_positive} FP={point.false_positive} "
            f"TN={point.true_negative} FN={point.false_negative})",
        )
    return "\n".join(lines)


def area_under_pr(points: tuple[PRPoint, ...]) -> float:
    """Trapezoidal AUC of the PR curve, sorted by recall ascending."""
    if len(points) < 2:
        return 0.0
    sorted_pts = sorted(points, key=lambda p: p.recall)
    area = 0.0
    for left, right in zip(sorted_pts[:-1], sorted_pts[1:]):
        width = right.recall - left.recall
        height = (left.precision + right.precision) / 2.0
        area += width * height
    if math.isnan(area):
        return 0.0
    return round(area, 6)


__all__ = [
    "DEFAULT_SWEEP_POINTS",
    "Objective",
    "PRPoint",
    "SweepReport",
    "VERTEX_DEFAULT_THRESHOLD",
    "area_under_pr",
    "format_report_table",
    "select_optimal_threshold",
    "sweep_thresholds",
    "write_report",
]
