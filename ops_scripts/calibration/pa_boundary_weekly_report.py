"""PA boundary weekly calibration report — P4.2 of apps-rg-spine-hardening-deferred-wave-2f8b1d.

Reads `artifacts/windsurf/apps_rg_pa_boundary_violations.jsonl` and emits:
- Per-week ERROR/WARN/CONDITIONAL_V1 counts
- Trend: is ERROR count rising, stable, or falling?
- Airlock detection-rate proxy (weeks at ERROR=0 / total weeks)
- Report saved to `docs/reports/apps_rg/pa_boundary_weekly_<YYYY-Www>.md`

Run:
    python ops_scripts/calibration/pa_boundary_weekly_report.py
    python ops_scripts/calibration/pa_boundary_weekly_report.py --weeks 4
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "apps_rg_pa_boundary_violations.jsonl"
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "apps_rg"


def _iso_to_week(ts: str) -> str:
    """Convert ISO timestamp to YYYY-Www string."""
    dt = datetime.fromisoformat(ts)
    return dt.strftime("%G-W%V")


def _load_rows(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    rows = []
    with log_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def _aggregate_by_week(rows: list[dict], weeks: int) -> dict[str, dict]:
    """Return per-week aggregates, most recent `weeks` weeks only."""
    by_week: dict[str, dict] = defaultdict(lambda: {"runs": 0, "errors": 0, "warns": 0, "conditional": 0, "bypassed": 0})
    for row in rows:
        if row.get("bypassed"):
            week = _iso_to_week(row["timestamp"])
            by_week[week]["bypassed"] += 1
            continue
        week = _iso_to_week(row["timestamp"])
        by_week[week]["runs"] += 1
        by_week[week]["errors"] += row.get("by_severity", {}).get("ERROR", 0)
        by_week[week]["warns"] += row.get("by_severity", {}).get("WARN", 0)
        by_week[week]["conditional"] += sum(
            1 for f in row.get("findings", [])
            if f.get("code") == "CONDITIONAL_V1_BASELINED"
        )

    sorted_weeks = sorted(by_week.keys())[-weeks:]
    return {w: by_week[w] for w in sorted_weeks}


def _trend(weekly: dict[str, dict]) -> str:
    """Simple trend: last 2 weeks ERROR delta."""
    weeks = list(weekly.values())
    if len(weeks) < 2:
        return "insufficient_data"
    delta = weeks[-1]["errors"] - weeks[-2]["errors"]
    if delta > 0:
        return "rising"
    if delta < 0:
        return "falling"
    return "stable"


def _clean_rate(weekly: dict[str, dict]) -> str:
    """Fraction of weeks with ERROR=0."""
    if not weekly:
        return "0/0"
    clean = sum(1 for w in weekly.values() if w["errors"] == 0)
    return f"{clean}/{len(weekly)}"


def generate_report(weeks: int = 8) -> str:
    rows = _load_rows(VIOLATIONS_LOG)
    weekly = _aggregate_by_week(rows, weeks)
    trend = _trend(weekly)
    clean_rate = _clean_rate(weekly)
    now = datetime.now(timezone.utc)
    week_label = now.strftime("%G-W%V")

    lines = [
        f"# PA Boundary Weekly Calibration Report — {week_label}",
        "",
        f"**Generated**: {now.strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Source**: `artifacts/windsurf/apps_rg_pa_boundary_violations.jsonl`  ",
        f"**Scanner**: `ops_scripts/ci/check_apps_rg_pa_boundary.py`  ",
        f"**Plan**: `apps-rg-spine-hardening-deferred-wave-2f8b1d` W4 P4.2",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Weeks in window | {len(weekly)} of {weeks} requested |",
        f"| Error trend | {trend} |",
        f"| Clean weeks (ERROR=0) | {clean_rate} |",
        f"| Fail-closed ready | {'YES — promote PA-RG1' if all(w['errors'] == 0 for w in weekly.values()) else 'NO — errors present'} |",
        "",
        "## Per-Week Breakdown",
        "",
        "| Week | Runs | ERROR | WARN | CONDITIONAL_V1 | Bypassed |",
        "|---|---|---|---|---|---|",
    ]

    for week, data in weekly.items():
        lines.append(
            f"| {week} | {data['runs']} | {data['errors']} | {data['warns']} | {data['conditional']} | {data['bypassed']} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- **ERROR=0 for all weeks** → promote `PA-RG1` to fail-closed (`APPS_RG_PA_BOUNDARY_FAIL_CLOSED=1`).",
        "- **CONDITIONAL_V1 count** → tracks progress toward NEXT_STEP-1 (SovereignLLMGateway wiring for `hops/_llm_client.py`).",
        "- **Rising errors** → investigate new direct-SDK callers; add to allowlist or baseline with Author-Gate approval.",
        "",
        "## Gate Promotion Criteria (D15)",
        "",
        "- ≥4 consecutive weeks at ERROR=0",
        "- CONDITIONAL_V1 count stable or falling",
        "- No new allowlist entries in the reporting window",
        "",
        "---",
        f"*Auto-generated by `ops_scripts/calibration/pa_boundary_weekly_report.py`*",
    ]

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--weeks", type=int, default=8, help="Number of weeks to include (default 8)")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout only; don't write file")
    args = parser.parse_args(argv)

    report = generate_report(weeks=args.weeks)

    if args.stdout:
        print(report)
        return 0

    now = datetime.now(timezone.utc)
    week_label = now.strftime("%G-W%V")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / f"pa_boundary_weekly_{week_label}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"[pa-boundary-weekly] Report written to {out_path}")
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
