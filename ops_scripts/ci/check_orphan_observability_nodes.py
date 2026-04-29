"""CI gate: Orphan observability nodes (Static↔Runtime ADG join).

Wraps ``tools.audits.static_runtime_gap``. Generates the weekly markdown
report and exits 0 (informational) by default. Pass ``--strict`` to fail
the build when orphans exceed a threshold.

The strict-mode threshold is intentionally generous in the bootstrap phase
(orphans expected to be high until coverage matures). Calibration via the
weekly cadence per ADR-050.
"""

from __future__ import annotations

import argparse
import sys

from tools.audits.static_runtime_gap import compute_gap, render_markdown
from pathlib import Path
import time


REPO_ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument(
        "--max-orphans", type=int, default=500,
        help="Strict mode fails the build when orphan_count > this value.",
    )
    parser.add_argument(
        "--out", type=Path,
        default=REPO_ROOT / "docs" / "reports" / "calibration"
        / f"static_runtime_gap_{time.strftime('%Y_W%V')}.md",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Fail the build when orphan_count > --max-orphans.",
    )
    args = parser.parse_args(argv)

    report = compute_gap(lookback_days=args.lookback_days, limit=args.limit)
    if not report.get("ok"):
        print("[orphan_check] FAILED to compute gap:", report.get("error"))
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_markdown(report), encoding="utf-8")
    orphans = report.get("orphan_count", 0)
    coverage = report.get("observability_coverage", 0.0)
    print(
        f"[orphan_check] orphans={orphans}  coverage={coverage:.1%}  "
        f"static_nodes={report.get('static_observability_nodes', 0)}  "
        f"-> {args.out}"
    )
    if args.strict and orphans > args.max_orphans:
        print(
            f"[orphan_check] STRICT FAIL: orphans={orphans} > "
            f"max_orphans={args.max_orphans}"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
