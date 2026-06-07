#!/usr/bin/env python3
"""ad-hoc ADG gate results query CLI (H3).

Replaces the retired ``tools/reports/wiring_ci_trend.py`` markdown trend
report. Instead of pre-generating decaying markdown, this CLI queries the
JSONL sink on demand.

Invocations:

    python tools/adg/query.py summary
        Latest run summary.

    python tools/adg/query.py trend --days 7
        Pass/fail trend for the last N days.

    python tools/adg/query.py regressions
        List gates currently above baseline in the latest run.

    python tools/adg/query.py history GATE_ID [--days N]
        Per-gate history over last N days (default 30).

Source sinks:
    - artifacts/cursor/adg_gate_dispatcher.jsonl  (H3 consolidated)
    - artifacts/cursor/wiring_gate_violations.jsonl (per-gate legacy, read-only)
    - artifacts/adg/adg_gate_results_<ts>.json (per-run snapshot)

Exit 0 on successful query, 2 on argparse error, 1 on I/O error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "artifacts"
SINK_DISPATCHER = ARTIFACTS / "windsurf" / "adg_gate_dispatcher.jsonl"
SINK_VIOLATIONS = ARTIFACTS / "windsurf" / "wiring_gate_violations.jsonl"
RESULTS_DIR = ARTIFACTS / "adg"


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def _latest_results_artifact() -> Path | None:
    artifacts = sorted(RESULTS_DIR.glob("adg_gate_results_*.json"))
    return artifacts[-1] if artifacts else None


def cmd_summary(args: argparse.Namespace) -> int:
    path = _latest_results_artifact()
    if not path:
        print("no adg_gate_results_*.json found; run `python -m ops_scripts.ci.adg_gates.run`")
        return 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(f"Snapshot: {path.name}")
    print(f"Timestamp: {payload.get('timestamp')}")
    print(f"Overall exit: {payload.get('overall_exit_code')}")
    print(f"Gates: {payload.get('total_gates')}")
    for k, v in payload.get("summary", {}).items():
        print(f"  {k:20s} {v}")
    return 0


def cmd_trend(args: argparse.Namespace) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    rows: list[dict[str, Any]] = []
    for entry in _iter_jsonl(SINK_DISPATCHER):
        ts = entry.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt < cutoff:
            continue
        rows.append(entry)
    if not rows:
        print(f"no dispatcher runs in last {args.days} days ({SINK_DISPATCHER})")
        return 0
    pass_count = sum(1 for r in rows if r.get("overall_exit_code") == 0)
    fail_count = sum(1 for r in rows if r.get("overall_exit_code") != 0)
    print(f"Window: last {args.days} days | runs={len(rows)} | pass={pass_count} fail={fail_count}")
    for r in rows[-10:]:
        s = r.get("summary", {})
        print(
            f"  {r['timestamp']:28s} exit={r['overall_exit_code']} "
            f"block_fail={s.get('block_fail', 0)} "
            f"regressed={s.get('ratchet_regressed', 0)}"
        )
    return 0


def cmd_regressions(args: argparse.Namespace) -> int:
    path = _latest_results_artifact()
    if not path:
        print("no adg_gate_results_*.json found")
        return 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    regressions = [g for g in payload.get("gates", []) if g.get("classification") == "regressed"]
    blocked = [g for g in payload.get("gates", []) if g.get("classification") == "blocked"]
    print(f"From {path.name}:")
    if blocked:
        print(f"\nBLOCKING ({len(blocked)}):")
        for g in blocked:
            print(f"  [{g['band']}] {g['gate_id']:42s} count={g['violation_count']}")
    if regressions:
        print(f"\nRATCHET REGRESSIONS ({len(regressions)}):")
        for g in regressions:
            base = g.get("baseline_count") or 0
            delta = g["violation_count"] - base
            print(
                f"  [{g['band']}] {g['gate_id']:42s} count={g['violation_count']} baseline={base} delta=+{delta}"
            )
    if not blocked and not regressions:
        print("no blocking failures or regressions")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    gate_id = args.gate_id
    matches = []
    for entry in tqdm(list(_iter_jsonl(SINK_VIOLATIONS)), desc="scan", unit="row"):
        if entry.get("gate_id") != gate_id:
            continue
        ts = entry.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if dt < cutoff:
            continue
        matches.append(entry)
    if not matches:
        print(f"no entries for {gate_id} in last {args.days} days")
        return 0
    print(f"Gate: {gate_id} | window: {args.days} days | runs={len(matches)}")
    for m in matches[-20:]:
        summary = m.get("summary", {})
        print(
            f"  {m['timestamp']:28s} status={m['status']:6s} "
            f"raw={summary.get('raw_count', '?')} active={summary.get('active_count', '?')}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("summary", help="Latest run summary")

    t = sub.add_parser("trend", help="Pass/fail trend over time")
    t.add_argument("--days", type=int, default=7)

    sub.add_parser("regressions", help="Current blockers + regressions")

    h = sub.add_parser("history", help="Per-gate history")
    h.add_argument("gate_id")
    h.add_argument("--days", type=int, default=30)

    args = parser.parse_args(argv)
    handler = {
        "summary": cmd_summary,
        "trend": cmd_trend,
        "regressions": cmd_regressions,
        "history": cmd_history,
    }[args.cmd]
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
