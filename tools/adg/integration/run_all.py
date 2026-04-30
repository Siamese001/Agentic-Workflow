"""Unified post-ADG-regen integration runner.

Invokes all W8-W13 ingesters in order against the latest ADG SQLite
snapshot. Designed to run after `python tools/generate_full_adg.py`
to augment the static graph with runtime-, profiling-, and
governance-derived edges.

Usage:
    python tools/adg/integration/run_all.py
    python tools/adg/integration/run_all.py --sqlite /path/to/snapshot.sqlite
    python tools/adg/integration/run_all.py --skip W11,W13
"""

from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.integration import (
    branch_coverage_bridge,
    calls_ingester,
    hitl_decision_ingester,
    otel_ingester,
    profiling_bridge,
    secret_access_ingester,
)
from tools.adg.integration.common import latest_snapshot


WAVES: list[tuple[str, str, callable]] = [
    ("W8", "calls (static promotion)", calls_ingester.ingest),
    ("W9", "OTel runtime_trace", otel_ingester.ingest),
    ("W10", "branch coverage", branch_coverage_bridge.ingest),
    ("W11", "secret access", secret_access_ingester.ingest),
    ("W12", "Author-Gate hitl_decision", hitl_decision_ingester.ingest),
    ("W13", "profiler-derived calls", profiling_bridge.ingest),
]


def main() -> int:
    p = argparse.ArgumentParser(description="Run all W8-W13 ADG ingesters")
    p.add_argument("--sqlite", type=Path, default=None)
    p.add_argument("--skip", default="", help="Comma-separated wave IDs to skip")
    args = p.parse_args()

    sqlite_path = args.sqlite or latest_snapshot()
    skip = {s.strip().upper() for s in args.skip.split(",") if s.strip()}

    print(f"[INTEGRATION] Snapshot: {sqlite_path.name}")
    print("=" * 60)

    totals: dict[str, int] = {}
    failures: list[str] = []

    for wave_id, label, fn in WAVES:
        if wave_id in skip:
            print(f"[{wave_id}] SKIP ({label})")
            continue
        try:
            if wave_id in {"W9", "W10", "W11", "W12", "W13"}:
                # These accept an optional source path; default to seed mode here
                count = fn(sqlite_path)  # type: ignore[call-arg]
            else:
                count = fn(sqlite_path)
            totals[wave_id] = int(count)
            print(f"[{wave_id}] {label:35s} +{count:>6} edges")
        except (OSError, ValueError, RuntimeError) as exc:
            failures.append(f"{wave_id}: {exc}")
            print(f"[{wave_id}] FAILED: {exc}")
            traceback.print_exc()

    print("=" * 60)
    grand_total = sum(totals.values())
    print(f"[INTEGRATION] Inserted {grand_total} edges across {len(totals)} waves")
    if failures:
        print(f"[INTEGRATION] {len(failures)} failures:")
        for f in failures:
            print(f"  {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
