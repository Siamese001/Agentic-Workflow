"""CLI for the threshold-sweep harness.

Usage::

    python -m tools.calibration \\
        --fixture tests/calibration/fixtures/r1b_semantic_cache.json \\
        --output docs/reports/calibration/r1b_sweep.json

    python -m tools.calibration --all  # sweep every fixture under tests/calibration/fixtures/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.calibration.feature_vector import load_fixture
from tools.calibration.threshold_sweep import (
    format_report_table,
    sweep_thresholds,
    write_report,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_FIXTURE_DIR = _REPO_ROOT / "tests" / "calibration" / "fixtures"
_DEFAULT_OUTPUT_DIR = _REPO_ROOT / "docs" / "reports" / "calibration"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.calibration",
        description="L0 routing calibration threshold-sweep harness (W0.P2).",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--fixture", type=Path, help="Path to a fixture JSON file.")
    src.add_argument(
        "--all",
        action="store_true",
        help=f"Sweep every *.json fixture under {_DEFAULT_FIXTURE_DIR.relative_to(_REPO_ROOT)}.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report here. Defaults to docs/reports/calibration/<fixture>_sweep.json.",
    )
    parser.add_argument(
        "--namespace",
        default="",
        help="Restrict sweep to one namespace (empty = all).",
    )
    parser.add_argument(
        "--points",
        type=int,
        default=101,
        help="Number of threshold points in the sweep (default 101 -> step 0.01).",
    )
    parser.add_argument(
        "--precision-floor",
        type=float,
        default=0.90,
        help="Minimum precision for precision_first objective (default 0.90).",
    )
    parser.add_argument(
        "--recall-floor",
        type=float,
        default=0.80,
        help="Minimum recall for recall_first objective (default 0.80).",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Suppress the progress bar.",
    )
    return parser


def _resolve_output(fixture_path: Path, override: Path | None) -> Path:
    if override is not None:
        return override
    return _DEFAULT_OUTPUT_DIR / f"{fixture_path.stem}_sweep.json"


def _run_one(fixture_path: Path, args: argparse.Namespace) -> int:
    fixture = load_fixture(fixture_path)
    report = sweep_thresholds(
        fixture,
        namespace=args.namespace,
        points=args.points,
        precision_floor=args.precision_floor,
        recall_floor=args.recall_floor,
        show_progress=not args.no_progress,
    )
    output_path = _resolve_output(fixture_path, args.output)
    resolved = write_report(report, output_path)
    print(format_report_table(report))
    print(f"\nreport written: {resolved}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.all:
        if args.output is not None:
            print("--output is incompatible with --all", file=sys.stderr)
            return 2
        fixtures = sorted(_DEFAULT_FIXTURE_DIR.glob("*.json"))
        if not fixtures:
            print(f"No fixtures found in {_DEFAULT_FIXTURE_DIR}", file=sys.stderr)
            return 1
        rc = 0
        for fixture_path in fixtures:
            print(f"\n=== {fixture_path.name} ===")
            rc = max(rc, _run_one(fixture_path, args))
        return rc
    return _run_one(args.fixture, args)


if __name__ == "__main__":
    raise SystemExit(main())
