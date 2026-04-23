"""Calibration helpers for LLM-as-Judge.

Implements inter-annotator agreement (IAA) metrics so judge outputs can
be compared to human expert labels on a gold set. Two metrics provided:

- :func:`cohens_kappa` — two-rater agreement adjusted for chance.
- :func:`krippendorffs_alpha` — N-rater agreement (ordinal scale) that
  also handles missing values (Unknown / abstention).

Both take iterables of per-item labels on the same ordinal scale
(default 1–5 integers, plus ``None`` / NaN for Unknown).

Also provides :func:`summarize_judge_vs_human` which loads a gold set
and a judge-outputs jsonl and emits per-dimension IAA plus the judge's
Unknown rate. Intended for the hardening plan's W5 wave.

Zero external dependencies beyond stdlib.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip().lower() in {"unknown", ""}:
        return True
    return False


def cohens_kappa(rater_a: Iterable[Any], rater_b: Iterable[Any]) -> float:
    """Cohen's kappa for two raters on a discrete scale.

    Items where either rater abstained (Unknown / NaN / None) are
    excluded from the calculation. Returns ``float('nan')`` when there
    are fewer than 2 comparable items.
    """
    pairs = [
        (a, b) for a, b in zip(rater_a, rater_b, strict=False) if not _is_missing(a) and not _is_missing(b)
    ]
    n = len(pairs)
    if n < 2:
        return float("nan")

    observed = sum(1 for a, b in pairs if a == b) / n

    counts_a = Counter(a for a, _ in pairs)
    counts_b = Counter(b for _, b in pairs)
    labels = set(counts_a) | set(counts_b)
    expected = sum((counts_a.get(label, 0) / n) * (counts_b.get(label, 0) / n) for label in labels)
    if expected >= 1.0:
        return 1.0 if observed >= 1.0 else float("nan")
    return (observed - expected) / (1.0 - expected)


def _ordinal_distance(x: float, y: float, max_diff: float) -> float:
    """Squared ordinal distance, normalized so the scale's max difference is 1."""
    if max_diff <= 0:
        return 0.0
    return ((x - y) / max_diff) ** 2


def krippendorffs_alpha(
    ratings: list[list[Any]],
    scale_min: float = 1.0,
    scale_max: float = 5.0,
) -> float:
    """Krippendorff's alpha for an N×M rater matrix on an ordinal scale.

    ``ratings`` is a list of rows; each row has one entry per rater.
    Missing values (None / NaN / Unknown) are dropped per-row, consistent
    with the Krippendorff definition.

    Returns ``float('nan')`` when there are fewer than 2 valid pairs.
    """
    max_diff = scale_max - scale_min
    numeric_rows: list[list[float]] = []
    for row in ratings:
        valid: list[float] = []
        for entry in row:
            if _is_missing(entry):
                continue
            try:
                valid.append(float(entry))
            except (TypeError, ValueError):
                continue
        if len(valid) >= 2:
            numeric_rows.append(valid)

    if not numeric_rows:
        return float("nan")

    # Observed disagreement Do.
    do_total = 0.0
    do_pairs = 0
    for row in numeric_rows:
        m = len(row)
        if m < 2:
            continue
        for i in range(m):
            for j in range(i + 1, m):
                do_total += _ordinal_distance(row[i], row[j], max_diff)
                do_pairs += 1
    if do_pairs == 0:
        return float("nan")
    do = do_total / do_pairs

    # Expected disagreement De across the full value pool.
    pool = [v for row in numeric_rows for v in row]
    n = len(pool)
    if n < 2:
        return float("nan")
    de_total = 0.0
    de_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            de_total += _ordinal_distance(pool[i], pool[j], max_diff)
            de_pairs += 1
    if de_pairs == 0 or de_total == 0.0:
        return 1.0 if do == 0.0 else float("nan")
    de = de_total / de_pairs
    return 1.0 - (do / de)


@dataclass
class JudgeCalibrationReport:
    """Per-dimension IAA summary for a judge vs human gold set."""

    n_items: int
    dimension_kappa: dict[str, float] = field(default_factory=dict)
    dimension_alpha: dict[str, float] = field(default_factory=dict)
    unknown_rate_by_dim: dict[str, float] = field(default_factory=dict)
    disagreement_samples: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_items": self.n_items,
            "dimension_kappa": self.dimension_kappa,
            "dimension_alpha": self.dimension_alpha,
            "unknown_rate_by_dim": self.unknown_rate_by_dim,
            "disagreement_samples": self.disagreement_samples,
        }


def summarize_judge_vs_human(
    gold_path: str | Path,
    judge_path: str | Path,
    dimensions: Iterable[str] | None = None,
    sample_disagreements: int = 5,
) -> JudgeCalibrationReport:
    """Build a calibration report from two aligned jsonl files.

    ``gold_path`` — each line is a record with an ``item_id`` field and
    per-dimension integer scores (or ``"Unknown"``).
    ``judge_path`` — same shape, produced by a judge over the same
    items. Only items present in BOTH files (matched on ``item_id``)
    are used.

    Returns a :class:`JudgeCalibrationReport` with Cohen's kappa,
    Krippendorff's alpha, unknown rate, and up to
    ``sample_disagreements`` example items where the judge and humans
    diverged most.
    """
    gold = _load_records(Path(gold_path))
    judge = _load_records(Path(judge_path))
    shared_ids = sorted(set(gold) & set(judge))

    if not shared_ids:
        return JudgeCalibrationReport(n_items=0)

    dims = (
        tuple(dimensions)
        if dimensions is not None
        else (
            "faithfulness",
            "answer_relevancy",
            "context_precision",
            "groundedness",
        )
    )

    report = JudgeCalibrationReport(n_items=len(shared_ids))
    disagreement_rows: list[tuple[float, dict[str, Any]]] = []

    for dim in dims:
        humans: list[Any] = []
        machines: list[Any] = []
        unknown_n = 0
        for item_id in shared_ids:
            human_val = gold[item_id].get(dim)
            judge_val = judge[item_id].get(dim)
            humans.append(human_val)
            machines.append(judge_val)
            if _is_missing(judge_val):
                unknown_n += 1
        report.dimension_kappa[dim] = round(cohens_kappa(humans, machines), 4)
        ratings_matrix = [
            [h, m] for h, m in zip(humans, machines, strict=False) if not (_is_missing(h) and _is_missing(m))
        ]
        report.dimension_alpha[dim] = round(
            krippendorffs_alpha(ratings_matrix),
            4,
        )
        report.unknown_rate_by_dim[dim] = round(unknown_n / len(shared_ids), 4)

    # Largest-disagreement samples across any dimension.
    for item_id in shared_ids:
        max_delta = 0.0
        deltas: dict[str, float] = {}
        for dim in dims:
            h = gold[item_id].get(dim)
            m = judge[item_id].get(dim)
            if _is_missing(h) or _is_missing(m):
                continue
            try:
                delta = abs(float(h) - float(m))  # type: ignore[arg-type]
            except (TypeError, ValueError):
                continue
            deltas[dim] = delta
            max_delta = max(max_delta, delta)
        if max_delta > 0:
            disagreement_rows.append(
                (
                    max_delta,
                    {
                        "item_id": item_id,
                        "max_delta": max_delta,
                        "deltas": deltas,
                    },
                ),
            )

    disagreement_rows.sort(key=lambda t: t[0], reverse=True)
    report.disagreement_samples = [row for _, row in disagreement_rows[:sample_disagreements]]
    return report


def _load_records(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            item_id = row.get("item_id")
            if not item_id:
                continue
            records[str(item_id)] = row
    return records


__all__ = [
    "JudgeCalibrationReport",
    "cohens_kappa",
    "krippendorffs_alpha",
    "summarize_judge_vs_human",
]
