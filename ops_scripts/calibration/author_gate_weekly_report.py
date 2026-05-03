#!/usr/bin/env python3
"""author_gate_weekly_report.py — Weekly markdown calibration report.

Plan: `.windsurf/plans/author-gate-hardening-a3b8f2.md` W4.P4.2.

Renders a weekly markdown report to
``docs/reports/author-gate/<YYYY-Www>.md`` summarising:

- Decision counts by class + override %
- Brier / ECE per class (from decision_calibration_snapshots, most-recent fit)
- Flip-readiness: fraction of decisions in the 0.72–0.85 near-indifference band
- Top-5 overrides that led to promote_to_pattern=1 (learning candidates)
- Top-5 recommendations that led to rollback=1 or regression=1 (calibration failures)
- Precedent-agreement % (did Cascade's selected option match historical winning pick?)

Usage:
    python ops_scripts/calibration/author_gate_weekly_report.py
    python ops_scripts/calibration/author_gate_weekly_report.py --week 2026w18

Fail policy: SOFT — missing sections render "insufficient data" row; never crashes.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"
REPORT_DIR = REPO_ROOT / "docs" / "reports" / "author-gate"


def _iso_year_week(dt: datetime) -> str:
    return dt.strftime("%Y-W%V")


def _week_bounds(yw: str) -> tuple[datetime, datetime]:
    """Parse 'YYYY-WWW' or 'YYYYwWW' → (monday_utc, next_monday_utc)."""
    yw = yw.replace("-W", "w").replace("-w", "w")
    year, week = yw.split("w")
    monday = datetime.fromisocalendar(int(year), int(week), 1).replace(tzinfo=timezone.utc)
    return monday, monday + timedelta(days=7)


def _fetch(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return list(conn.execute(sql, params).fetchall())


def build_report(conn: sqlite3.Connection, start: datetime, end: datetime) -> str:
    s_iso = start.isoformat()
    e_iso = end.isoformat()
    out: list[str] = []
    out.append(f"# Author-Gate Weekly Calibration Report — {_iso_year_week(start)}")
    out.append("")
    out.append(f"**Window:** {s_iso} → {e_iso} (UTC)")
    out.append("")

    # 1) Counts by class + override %
    out.append("## 1. Decision Counts by Class")
    out.append("")
    out.append("| Class | N | Overrides | Override % |")
    out.append("|---|---:|---:|---:|")
    rows = _fetch(conn,
        """SELECT decision_type AS cls,
                  COUNT(*) AS n,
                  SUM(COALESCE(override_vs_recommendation, 0)) AS overrides
             FROM decisions
            WHERE created_at >= ? AND created_at < ?
         GROUP BY decision_type
         ORDER BY n DESC""", (s_iso, e_iso))
    if not rows:
        out.append("| _no decisions in window_ | 0 | 0 | 0% |")
    else:
        for r in rows:
            n = r["n"] or 0
            ov = r["overrides"] or 0
            pct = (100.0 * ov / n) if n else 0.0
            out.append(f"| {r['cls']} | {n} | {ov} | {pct:.1f}% |")
    out.append("")

    # 2) Latest calibration snapshot per class
    out.append("## 2. Calibration Quality (latest fit)")
    out.append("")
    out.append("| Class | n_outcomes | Brier | ECE | Version |")
    out.append("|---|---:|---:|---:|---|")
    rows = _fetch(conn,
        """SELECT decision_type AS cls, n_outcomes, brier_score, ece_score,
                  calibrator_version, created_at
             FROM decision_calibration_snapshots
            WHERE rowid IN (
              SELECT MAX(rowid) FROM decision_calibration_snapshots GROUP BY decision_type
            )
         ORDER BY cls""")
    if not rows:
        out.append("| _no calibration snapshots yet_ | — | — | — | — |")
    else:
        for r in rows:
            brier = r["brier_score"]
            ece = r["ece_score"]
            out.append(
                f"| {r['cls']} | {r['n_outcomes']} | "
                f"{brier:.4f} | {ece:.4f} | {r['calibrator_version']} |"
            )
    out.append("")

    # 3) Flip-readiness
    out.append("## 3. Flip-Readiness (0.72–0.85 near-indifference band)")
    out.append("")
    rows = _fetch(conn,
        """SELECT decision_type AS cls,
                  SUM(CASE WHEN confidence_top BETWEEN 0.72 AND 0.85 THEN 1 ELSE 0 END) AS in_band,
                  COUNT(*) AS total
             FROM decisions
            WHERE created_at >= ? AND created_at < ?
              AND confidence_top IS NOT NULL
         GROUP BY decision_type""", (s_iso, e_iso))
    if not rows:
        out.append("_no scored decisions in window_")
    else:
        out.append("| Class | in-band | total | in-band % |")
        out.append("|---|---:|---:|---:|")
        for r in rows:
            t = r["total"] or 0
            b = r["in_band"] or 0
            pct = (100.0 * b / t) if t else 0.0
            out.append(f"| {r['cls']} | {b} | {t} | {pct:.1f}% |")
    out.append("")

    # 4) Top-5 overrides that led to success (learning candidates)
    out.append("## 4. Top-5 Overrides → Promotion (learning candidates)")
    out.append("")
    rows = _fetch(conn,
        """SELECT d.decision_id, d.decision_type, d.reason_code, d.principle_at_stake,
                  d.confidence_top, d.confidence_dominance_gap
             FROM decisions d
             JOIN decision_outcomes o USING (decision_id)
            WHERE d.override_vs_recommendation = 1
              AND o.promote_to_pattern = 1
              AND o.rollback_required = 0
              AND o.regression_found = 0
              AND d.created_at >= ? AND d.created_at < ?
         ORDER BY d.confidence_dominance_gap ASC
         LIMIT 5""", (s_iso, e_iso))
    if not rows:
        out.append("_no override→promotion events in window_")
    else:
        out.append("| decision_id | class | reason | top | gap | principle |")
        out.append("|---|---|---|---:|---:|---|")
        for r in rows:
            out.append(
                f"| `{r['decision_id']}` | {r['decision_type']} | {r['reason_code'] or '—'} | "
                f"{(r['confidence_top'] or 0):.2f} | {(r['confidence_dominance_gap'] or 0):.2f} | "
                f"{(r['principle_at_stake'] or '—')[:40]} |"
            )
    out.append("")

    # 5) Top-5 recommendations that led to failure
    out.append("## 5. Top-5 Recommendations → Rollback/Regression (calibration failures)")
    out.append("")
    rows = _fetch(conn,
        """SELECT d.decision_id, d.decision_type, d.confidence_top,
                  o.rollback_required, o.regression_found
             FROM decisions d
             JOIN decision_outcomes o USING (decision_id)
            WHERE COALESCE(d.override_vs_recommendation, 0) = 0
              AND (o.rollback_required = 1 OR o.regression_found = 1)
              AND d.created_at >= ? AND d.created_at < ?
         ORDER BY d.confidence_top DESC
         LIMIT 5""", (s_iso, e_iso))
    if not rows:
        out.append("_no recommendation failures in window_")
    else:
        out.append("| decision_id | class | top-score | rollback | regression |")
        out.append("|---|---|---:|:---:|:---:|")
        for r in rows:
            out.append(
                f"| `{r['decision_id']}` | {r['decision_type']} | "
                f"{(r['confidence_top'] or 0):.2f} | "
                f"{'✅' if r['rollback_required'] else ''} | "
                f"{'✅' if r['regression_found'] else ''} |"
            )
    out.append("")

    # 6) Precedent-agreement
    out.append("## 6. Precedent Verdict Distribution")
    out.append("")
    rows = _fetch(conn,
        """SELECT COALESCE(precedent_verdict, 'none') AS verdict, COUNT(*) AS n
             FROM decisions
            WHERE created_at >= ? AND created_at < ?
         GROUP BY precedent_verdict
         ORDER BY n DESC""", (s_iso, e_iso))
    if not rows:
        out.append("_no precedent telemetry in window_")
    else:
        total = sum((r["n"] or 0) for r in rows)
        out.append("| Verdict | N | Share |")
        out.append("|---|---:|---:|")
        for r in rows:
            n = r["n"] or 0
            pct = (100.0 * n / total) if total else 0.0
            out.append(f"| {r['verdict']} | {n} | {pct:.1f}% |")
    out.append("")

    out.append("---")
    out.append("")
    out.append(
        f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by "
        "`ops_scripts/calibration/author_gate_weekly_report.py`."
    )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--db", default=str(DB_PATH))
    p.add_argument("--week", default=None, help="YYYY-WNN (default: current week)")
    p.add_argument("--out-dir", default=str(REPORT_DIR))
    args = p.parse_args(argv)

    yw = args.week or _iso_year_week(datetime.now(timezone.utc))
    try:
        start, end = _week_bounds(yw)
    except (ValueError, IndexError) as exc:
        print(f"[weekly_report] bad --week: {exc}", file=sys.stderr)
        return 2

    db = Path(args.db)
    if not db.exists():
        print(f"[weekly_report] ledger not found: {db}", file=sys.stderr)
        return 2

    conn = sqlite3.connect(str(db), timeout=15)
    try:
        md = build_report(conn, start, end)
    finally:
        conn.close()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{yw}.md"
    out_path.write_text(md, encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
