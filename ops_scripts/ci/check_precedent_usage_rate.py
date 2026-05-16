#!/usr/bin/env python3
"""
check_precedent_usage_rate.py — W5.3 precedent usage-rate monitor.

Computes the % of recent Author-Gate decisions that had `precedent_seen > 0`.
Running baseline: the usage rate should remain within ± --max-deviation-pct
of the trailing 60-day average. A sudden collapse implies
`consult_precedent()` stopped matching (schema drift, fingerprint bug, etc).

Exit 0 — within tolerance (or insufficient history)
Exit 1 — usage rate dropped below baseline
Exit 2 — script error

Bypass: PRECEDENT_USAGE_BYPASS=1
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DB = REPO_ROOT / ".cursor" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "precedent_usage_violations.jsonl"
BYPASS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "precedent_usage_bypass.jsonl"
REPORT_PATH = REPO_ROOT / "artifacts" / "ledgers" / "precedent_usage_report.json"


def _log(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **payload,
                    }
                )
                + "\n"
            )
    except OSError:
        # guardian: allow-silent-swallow -- log unwritable: non-fatal
        pass


def _usage_rate(conn: sqlite3.Connection, since_iso: str) -> tuple[int, int]:
    """Return (total_with_receipt, total_with_matches) in window."""
    try:
        rows = list(
            conn.execute(
                "SELECT precedent_seen FROM decisions WHERE created_at >= ? AND precedent_seen IS NOT NULL",
                (since_iso,),
            )
        )
    except sqlite3.Error:
        return 0, 0
    total = len(rows)
    with_match = sum(1 for r in rows if isinstance(r[0], int) and r[0] > 0)
    return total, with_match


def main() -> int:
    ap = argparse.ArgumentParser(description="Precedent usage-rate monitor (W5.3)")
    ap.add_argument("--recent-days", type=int, default=7)
    ap.add_argument("--baseline-days", type=int, default=60)
    ap.add_argument("--max-deviation-pct", type=float, default=30.0)
    ap.add_argument(
        "--min-baseline-samples",
        type=int,
        default=10,
        help="Need at least this many baseline decisions to evaluate",
    )
    args = ap.parse_args()

    if os.environ.get("PRECEDENT_USAGE_BYPASS") == "1":
        _log(BYPASS_LOG, {"reason": "env"})
        print("[check_precedent_usage_rate] BYPASS (env). Logged.", file=sys.stderr)
        return 0

    if not LEDGER_DB.exists():
        print("[check_precedent_usage_rate] OK — ledger not present", file=sys.stderr)
        return 0

    now = datetime.now(timezone.utc)
    recent_cut = (now - timedelta(days=args.recent_days)).isoformat(timespec="seconds")
    baseline_cut = (now - timedelta(days=args.baseline_days)).isoformat(timespec="seconds")

    try:
        conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True, timeout=5)
    except sqlite3.Error as exc:
        print(f"[check_precedent_usage_rate] script error: {exc}", file=sys.stderr)
        return 2
    try:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(decisions)")}
        if "precedent_seen" not in cols:
            print(
                "[check_precedent_usage_rate] OK — precedent_seen column absent (pre-W2.1 schema)",
                file=sys.stderr,
            )
            return 0

        recent_total, recent_hits = _usage_rate(conn, recent_cut)
        baseline_total, baseline_hits = _usage_rate(conn, baseline_cut)
    finally:
        conn.close()

    recent_rate = (recent_hits / recent_total * 100.0) if recent_total else 0.0
    baseline_rate = (baseline_hits / baseline_total * 100.0) if baseline_total else 0.0

    report = {
        "generated_at": now.isoformat(timespec="seconds"),
        "recent_days": args.recent_days,
        "baseline_days": args.baseline_days,
        "recent_total": recent_total,
        "recent_hits": recent_hits,
        "recent_rate_pct": round(recent_rate, 1),
        "baseline_total": baseline_total,
        "baseline_hits": baseline_hits,
        "baseline_rate_pct": round(baseline_rate, 1),
    }
    try:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except OSError:
        # guardian: allow-silent-swallow -- report unwritable: non-fatal
        pass

    print(
        f"[check_precedent_usage_rate] recent={recent_rate:.1f}% "
        f"({recent_hits}/{recent_total}) baseline={baseline_rate:.1f}% "
        f"({baseline_hits}/{baseline_total})",
        file=sys.stderr,
    )

    if baseline_total < args.min_baseline_samples:
        print(
            f"[check_precedent_usage_rate] OK — insufficient baseline "
            f"({baseline_total} < {args.min_baseline_samples})",
            file=sys.stderr,
        )
        return 0

    drop = baseline_rate - recent_rate
    if drop > args.max_deviation_pct:
        print(
            f"[check_precedent_usage_rate] FAIL — rate dropped {drop:.1f}pp (max {args.max_deviation_pct}pp)",
            file=sys.stderr,
        )
        _log(VIOLATIONS_LOG, report)
        return 1

    print(f"[check_precedent_usage_rate] PASS — drop {drop:.1f}pp within tolerance", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (sqlite3.Error, OSError) as exc:
        print(f"[check_precedent_usage_rate] script error: {exc}", file=sys.stderr)
        sys.exit(2)
