"""Scheduled retrieval-eval harness for ADR-061.

This module supplies the cron/on-demand wrapper around the deterministic
RAGAS-shaped metrics in ``retrieval_ragas.py``. It deliberately accepts plain
JSONL inputs so CI and operators can run it without a live vector store.
Rows that include both ``expected_chunks`` and ``retrieved_chunks`` are scored;
rows without retrieved results are counted as skipped curation/eval gaps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.eval.retrieval_ragas import AggregateMetrics, RetrievalCase, aggregate


DEFAULT_GOLDEN_DIR = Path("data/eval/golden/retrieval")
DEFAULT_OUTPUT_DIR = Path("artifacts/eval/retrieval")


@dataclass(frozen=True)
class ScheduledRetrievalEval:
    """Serializable result for one scheduled retrieval-eval run."""

    run_id: str
    mode: str
    generated_at: str
    golden_files: tuple[str, ...]
    input_rows: int
    scored_cases: int
    skipped_cases: int
    metrics: AggregateMetrics
    failed_gates: tuple[str, ...]


def load_retrieval_cases(path: Path) -> tuple[list[RetrievalCase], int]:
    """Load scoreable retrieval cases from one JSONL file.

    Accepted row keys are ADR-061's ``expected_chunks`` plus either
    ``retrieved_chunks`` or ``retrieved_chunk_ids``. Missing retrieved chunks
    are treated as unscored rows instead of synthetic passes.
    """

    cases: list[RetrievalCase] = []
    row_count = 0
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        row_count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSONL row") from exc

        expected = row.get("expected_chunks") or row.get("expected_chunk_ids") or ()
        retrieved = row.get("retrieved_chunks", row.get("retrieved_chunk_ids"))
        if not expected or retrieved is None:
            continue

        cases.append(
            RetrievalCase(
                query_id=str(row.get("query_id") or row.get("id") or f"{path.stem}:{line_no}"),
                expected_chunks=tuple(str(chunk) for chunk in expected),
                retrieved_chunks=tuple(str(chunk) for chunk in retrieved),
            )
        )
    return cases, row_count


def select_golden_files(golden_dir: Path, mode: str) -> list[Path]:
    """Return the JSONL files for a slice or full scheduled run."""

    if mode not in {"slice", "full"}:
        raise ValueError(f"mode must be 'slice' or 'full', got {mode!r}")
    files = sorted(golden_dir.glob("*.jsonl"))
    if mode == "slice":
        return files[:1]
    return files


def run_scheduled_eval(
    *,
    golden_dir: Path = DEFAULT_GOLDEN_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    mode: str = "slice",
    min_recall_at_20: float = 0.0,
) -> tuple[ScheduledRetrievalEval, Path]:
    """Run the scheduled retrieval eval and write JSON + history artifacts."""

    if not 0.0 <= min_recall_at_20 <= 1.0:
        raise ValueError("min_recall_at_20 must be in [0, 1]")

    selected_files = select_golden_files(golden_dir, mode)
    cases: list[RetrievalCase] = []
    input_rows = 0
    for path in selected_files:
        file_cases, file_rows = load_retrieval_cases(path)
        cases.extend(file_cases)
        input_rows += file_rows

    metrics = aggregate(cases)
    failed_gates: list[str] = []
    if metrics.n_cases > 0 and metrics.recall_at_20 < min_recall_at_20:
        failed_gates.append(
            f"recall_at_20 {metrics.recall_at_20:.4f} below floor {min_recall_at_20:.4f}"
        )

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    run_hash = hashlib.sha256(
        json.dumps(
            {
                "mode": mode,
                "generated_at": generated_at,
                "files": [str(path) for path in selected_files],
                "n_cases": metrics.n_cases,
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()[:12]
    run_id = f"retrieval-eval-{generated_at.replace(':', '').replace('+0000', 'Z')}-{run_hash}"

    result = ScheduledRetrievalEval(
        run_id=run_id,
        mode=mode,
        generated_at=generated_at,
        golden_files=tuple(str(path) for path in selected_files),
        input_rows=input_rows,
        scored_cases=metrics.n_cases,
        skipped_cases=input_rows - metrics.n_cases,
        metrics=metrics,
        failed_gates=tuple(failed_gates),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / f"{run_id}.json"
    payload = _result_payload(result)
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    history_path = output_dir / "history.jsonl"
    with history_path.open("a", encoding="utf-8") as history:
        history.write(json.dumps(payload, sort_keys=True) + "\n")
    return result, artifact_path


def _result_payload(result: ScheduledRetrievalEval) -> dict[str, Any]:
    payload = asdict(result)
    payload["metrics"] = asdict(result.metrics)
    return payload


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run scheduled retrieval eval metrics.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--slice", action="store_true", help="Run the diagonal/smoke slice.")
    group.add_argument("--full", action="store_true", help="Run every JSONL file in the golden set.")
    parser.add_argument("--golden-dir", type=Path, default=DEFAULT_GOLDEN_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--min-recall-at-20", type=float, default=0.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    mode = "full" if args.full else "slice"
    result, artifact_path = run_scheduled_eval(
        golden_dir=args.golden_dir,
        output_dir=args.output_dir,
        mode=mode,
        min_recall_at_20=args.min_recall_at_20,
    )
    print(
        json.dumps(
            {
                "run_id": result.run_id,
                "artifact": str(artifact_path),
                "scored_cases": result.scored_cases,
                "skipped_cases": result.skipped_cases,
                "failed_gates": result.failed_gates,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 1 if result.failed_gates else 0


if __name__ == "__main__":
    raise SystemExit(main())
