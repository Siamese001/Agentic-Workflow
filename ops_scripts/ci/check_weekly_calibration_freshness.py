#!/usr/bin/env python3
"""check_weekly_calibration_freshness.py — CI gate (W4.3, plan c8f4a2).

Asserts the unified ledger calibration report has been regenerated within the
freshness window. The weekly report at docs/reports/calibration/<YYYY-Www>.md
is the cross-ledger source-of-truth for precedent-hit rates and per-band
calibration curves; if it goes stale, downstream consumers (Author-Gate
threshold tuning, intelligence-ledger consulters, anomaly-driven Notion
writeback) silently lose signal.

Policy:
    - Default freshness window: 8 days (one week + 1 day grace)
    - Override with --max-age-days
    - Bypass via env CALIBRATION_FRESHNESS_BYPASS=1 (logs but exits 0)

Failure modes:
    - File missing entirely        → exit 1
    - File older than window       → exit 1
    - Generator script broken      → exit 2 (smoke-run check)

CONSTITUTIONAL
    - subprocess.run(argv, shell=False, timeout=) where used
    - Specific exceptions only
    - UTF-8 file I/O
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "calibration"
GENERATOR = REPO_ROOT / "ops_scripts" / "calibration" / "ledger_weekly_report.py"


def _iso_week(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def _latest_report() -> Path | None:
    if not REPORT_DIR.exists():
        return None
    candidates = sorted(REPORT_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=8,
        help="Maximum age in days before the latest report is considered stale (default 8)",
    )
    parser.add_argument(
        "--smoke-run",
        action="store_true",
        help="Also run the generator script with --no-write style dry probe",
    )
    args = parser.parse_args()

    if os.environ.get("CALIBRATION_FRESHNESS_BYPASS") == "1":
        print("[check_weekly_calibration_freshness] BYPASS active — skipping check")
        return 0

    latest = _latest_report()
    if latest is None:
        print(
            f"[check_weekly_calibration_freshness] FAIL — no report under {REPORT_DIR.relative_to(REPO_ROOT)}"
        )
        print("  Run: python ops_scripts/calibration/ledger_weekly_report.py")
        return 1

    age = datetime.now(timezone.utc) - datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
    age_days = age.total_seconds() / 86400
    if age_days > args.max_age_days:
        print(
            f"[check_weekly_calibration_freshness] FAIL — latest report "
            f"{latest.name} is {age_days:.1f} days old (max {args.max_age_days})"
        )
        print("  Run: python ops_scripts/calibration/ledger_weekly_report.py")
        return 1

    # Smoke-run: ensure the generator can produce a report. Bounded 60s.
    if args.smoke_run:
        try:
            result = subprocess.run(
                [sys.executable, str(GENERATOR), "--out", str(REPORT_DIR / "_smoke.md")],
                shell=False,
                timeout=60,
                capture_output=True,
                text=True,
                check=False,
            )
        except subprocess.TimeoutExpired:
            print("[check_weekly_calibration_freshness] FAIL — generator timed out (60s)")
            return 2
        except (OSError, ValueError) as exc:
            print(f"[check_weekly_calibration_freshness] FAIL — generator launch error: {exc}")
            return 2
        if result.returncode != 0:
            print(
                f"[check_weekly_calibration_freshness] FAIL — generator exited "
                f"{result.returncode}: {result.stderr[:300]}"
            )
            return 2
        # Clean up smoke artifact
        smoke_path = REPORT_DIR / "_smoke.md"
        if smoke_path.exists():
            try:
                smoke_path.unlink()
            except OSError:
                pass

    print(
        f"[check_weekly_calibration_freshness] OK — {latest.name} "
        f"({age_days:.1f} days old, week {_iso_week(datetime.now(timezone.utc))})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
