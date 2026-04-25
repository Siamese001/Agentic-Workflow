"""R1B threshold-sweep harness (R1B follow-on #3).

Sweeps L2 semantic-cache similarity thresholds against a fixture set of
``(query, expected_answer_id)`` pairs and emits a CSV / Markdown report
showing precision, hit-rate, and false-positive rate at each threshold.

This harness is **synthetic-data-friendly**: the fixture file can be
hand-curated golden pairs OR drawn from production telemetry. The doctrine
in ``docs/contracts/semantic_cache_staleness.md`` is unchanged — operators
should run this harness against ≥1k production query samples before
flipping a per-tier threshold env var
(``SEMANTIC_CACHE_THRESHOLD_DYNAMIC``).

Usage::

    python -m tools.cache.threshold_sweep_harness \\
        --fixtures path/to/golden.jsonl \\
        --thresholds 0.85,0.90,0.92,0.95,0.97,0.99 \\
        --out-csv artifacts/cache/sweep_report.csv \\
        --out-md  artifacts/cache/sweep_report.md

Fixture line shape (JSONL)::

    {"query": "...", "expected_answer_id": "ans_42", "candidate_answer_id": "ans_42",
     "candidate_similarity": 0.965}

* ``expected_answer_id`` — ground-truth answer the cache *should* serve
* ``candidate_answer_id`` — answer the cache *would* serve at this similarity
* ``candidate_similarity`` — measured cosine similarity between query
  and the candidate's stored query

A "hit" is recorded when ``candidate_similarity ≥ threshold``. A "true
positive" is a hit where ``candidate_answer_id == expected_answer_id``;
a "false positive" is a hit where they differ.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

# Bounded, deterministic, no network. Suitable for CI cron.


@dataclass(frozen=True)
class SweepRow:
    threshold: float
    total: int
    hits: int
    true_positives: int
    false_positives: int

    @property
    def hit_rate(self) -> float:
        return (self.hits / self.total) if self.total else 0.0

    @property
    def precision(self) -> float:
        return (self.true_positives / self.hits) if self.hits else 0.0

    @property
    def false_positive_rate(self) -> float:
        return (self.false_positives / self.total) if self.total else 0.0


def _load_fixtures(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fp:
        for raw in fp:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL line in {path}: {exc}") from exc
    return rows


def sweep(fixtures: list[dict], thresholds: Iterable[float]) -> list[SweepRow]:
    """Compute hit / TP / FP counts for each threshold."""
    out: list[SweepRow] = []
    total = len(fixtures)
    for t in thresholds:
        hits = 0
        tp = 0
        fp = 0
        for row in fixtures:
            sim = float(row.get("candidate_similarity", 0.0))
            if sim < t:
                continue
            hits += 1
            if row.get("candidate_answer_id") == row.get("expected_answer_id"):
                tp += 1
            else:
                fp += 1
        out.append(SweepRow(threshold=t, total=total, hits=hits, true_positives=tp, false_positives=fp))
    return out


def write_csv(rows: list[SweepRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            [
                "threshold",
                "total",
                "hits",
                "true_positives",
                "false_positives",
                "hit_rate",
                "precision",
                "false_positive_rate",
            ]
        )
        for r in rows:
            writer.writerow(
                [
                    f"{r.threshold:.3f}",
                    r.total,
                    r.hits,
                    r.true_positives,
                    r.false_positives,
                    f"{r.hit_rate:.4f}",
                    f"{r.precision:.4f}",
                    f"{r.false_positive_rate:.4f}",
                ]
            )


def write_md(rows: list[SweepRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Semantic Cache Threshold Sweep Report",
        "",
        "| Threshold | Total | Hits | TP | FP | Hit Rate | Precision | FP Rate |",
        "|-----------|-------|------|----|----|----------|-----------|---------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.threshold:.3f} | {r.total} | {r.hits} | {r.true_positives} | "
            f"{r.false_positives} | {r.hit_rate:.4f} | {r.precision:.4f} | "
            f"{r.false_positive_rate:.4f} |"
        )
    lines.append("")
    lines.append(
        "Operator guidance: pick the lowest threshold whose precision is ≥ 0.99 "
        "AND false-positive rate is ≤ 0.005 across ≥1k samples."
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _parse_thresholds(spec: str) -> list[float]:
    return [float(x.strip()) for x in spec.split(",") if x.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sweep semantic-cache similarity thresholds.")
    parser.add_argument(
        "--fixtures", type=Path, required=True, help="JSONL file with query/expected/candidate rows."
    )
    parser.add_argument(
        "--thresholds", default="0.85,0.90,0.92,0.95,0.97,0.99", help="Comma-separated thresholds to test."
    )
    parser.add_argument("--out-csv", type=Path, default=Path("artifacts/cache/sweep_report.csv"))
    parser.add_argument("--out-md", type=Path, default=Path("artifacts/cache/sweep_report.md"))
    args = parser.parse_args(argv)

    fixtures = _load_fixtures(args.fixtures)
    if not fixtures:
        print(f"ERROR: no fixtures loaded from {args.fixtures}", file=sys.stderr)
        return 2

    thresholds = _parse_thresholds(args.thresholds)
    rows = sweep(fixtures, thresholds)
    write_csv(rows, args.out_csv)
    write_md(rows, args.out_md)
    print(f"wrote {args.out_csv} and {args.out_md} ({len(fixtures)} fixtures, {len(thresholds)} thresholds)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
