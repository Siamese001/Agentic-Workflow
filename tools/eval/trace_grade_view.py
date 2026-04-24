"""Trace-grade review surface (W2.5).

Operator-facing CLI that lists recent traces with their grader scores and
lets a human sample, regrade, or flag them for curation. Feeds the same
regrade queue as ``transcript_sampler.py`` and the golden-curation adapter.

The surface is intentionally CLI-first so it can be wrapped in the existing
``otel_mcp`` or a dedicated ``eval_mcp`` without introducing UI deps in the
harness.

Invariants:
  - Observer posture (no mutation of runtime state).
  - All regrade actions emit proposals through the UWG-routed adapters, not
    direct writes.
  - Deterministic output ordering: sort by (score_asc, trace_id).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TraceGradeRow:
    trace_id: str
    rubric_family: str
    dimension: str
    score: float | None
    outcome: str
    summary: str


def _load_graded_traces(source: Path) -> list[TraceGradeRow]:
    """Load pre-graded traces from a JSONL artifact.

    Scaffold: reads the format emitted by ``run_capability_regression.py``
    extended with per-trace grades. Kept separate from the harness runner so
    the review surface can evolve independently.
    """
    if not source.exists():
        return []
    rows: list[TraceGradeRow] = []
    with source.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            rows.append(TraceGradeRow(
                trace_id=str(obj.get("trace_id", "")),
                rubric_family=str(obj.get("rubric_family", "")),
                dimension=str(obj.get("dimension", "")),
                score=obj.get("score"),
                outcome=str(obj.get("outcome", "")),
                summary=str(obj.get("summary", "")),
            ))
    return rows


def list_rows(rows: list[TraceGradeRow], limit: int) -> list[TraceGradeRow]:
    def _key(r: TraceGradeRow) -> tuple[float, str]:
        score = r.score if r.score is not None else 999.0
        return (score, r.trace_id)
    return sorted(rows, key=_key)[:limit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("artifacts/eval/graded_traces.jsonl"))
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

    rows = list_rows(_load_graded_traces(args.source), args.limit)
    if args.format == "json":
        json.dump([r.__dict__ for r in rows], sys.stdout, indent=2, sort_keys=True)
    else:
        if not rows:
            print("(no graded traces available)")
            return 0
        print(f"{'score':>6}  {'outcome':<9}  {'family':<10}  {'dim':<30}  trace_id")
        print("-" * 78)
        for r in rows:
            score = f"{r.score:.2f}" if r.score is not None else "  -  "
            print(f"{score:>6}  {r.outcome:<9}  {r.rubric_family:<10}  {r.dimension:<30}  {r.trace_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
