"""CLI for the offline section-quality benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from apps_rg.evals.section_quality_benchmark.evaluation import evaluate_section_benchmark
from apps_rg.evals.section_quality_benchmark.reporting import write_report

_EXIT_CODES = {"PASS": 0, "FAIL": 1, "UNKNOWN": 2, "NOT_MEASURED": 2}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate sealed Apps RG section artifacts and completed offline reviews."
    )
    parser.add_argument("--input", required=True, type=Path, help="Sealed section input JSON")
    parser.add_argument("--reviews", required=True, type=Path, help="Sealed completed-review JSON")
    parser.add_argument("--output", type=Path, help="Optional report JSON path")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        input_bundle = json.loads(args.input.read_text(encoding="utf-8"))
        review_bundle = json.loads(args.reviews.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"section-quality input error: {exc}", file=sys.stderr)
        return 3
    report = evaluate_section_benchmark(input_bundle, review_bundle)
    if args.output is not None:
        try:
            write_report(report, args.output, pretty=not args.compact)
        except OSError as exc:
            print(f"section-quality output error: {exc}", file=sys.stderr)
            return 3
    print(
        json.dumps(
            report,
            allow_nan=False,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            separators=(",", ":") if args.compact else None,
            sort_keys=True,
        )
    )
    return _EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
