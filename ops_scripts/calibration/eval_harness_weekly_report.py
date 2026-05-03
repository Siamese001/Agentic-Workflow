"""eval_harness_weekly_report — weekly rollup of eval_harness_outcome ledger.

Plan: ``.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`` W5.P3.

Produces a weekly summary of the W5.P7 ``eval_harness_outcome`` ledger:
per-app run counts, pass/deny/escalate/unknown breakdown, top fail
reasons, HITL policy effectiveness. Written as JSON + a short markdown
summary under ``docs/reports/eval_harness/<YYYY-Www>.md``.

Shape-valid even for an empty ledger.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _ledger_path() -> Path:
    return REPO_ROOT / "artifacts" / "ledgers" / "eval_harness_outcome.sqlite"


def _iso_week_tag(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    iso_year, iso_week, _ = now.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _collect_rows() -> list[dict]:
    path = _ledger_path()
    if not path.exists():
        return []
    try:
        conn = sqlite3.connect(str(path))
        try:
            rows = conn.execute(
                "SELECT repo_area, score_band, score_numeric, prediction_json, "
                "outcome_json, ts_utc FROM events "
                "WHERE event_kind IN ('app_eval_bound','app_eval_unbound') "
                "ORDER BY ts_utc DESC LIMIT 5000"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []
    out = []
    for repo_area, band, score, pred_raw, out_raw, ts in rows:
        try:
            pred = json.loads(pred_raw) if pred_raw else {}
        except json.JSONDecodeError:
            pred = {}
        try:
            outc = json.loads(out_raw) if out_raw else {}
        except json.JSONDecodeError:
            outc = {}
        out.append({
            "app_id": pred.get("app_id") or repo_area,
            "score_band": band or "unknown",
            "overall_score": score,
            "hitl_policy": pred.get("hitl_policy", "none"),
            "fail_reasons": pred.get("fail_reasons", []),
            "disposition": outc.get("disposition", ""),
            "rationale": outc.get("rationale", ""),
            "ts_utc": ts,
        })
    return out


def build_report() -> dict:
    rows = _collect_rows()
    per_app: dict[str, dict] = defaultdict(lambda: {
        "runs": 0,
        "bands": Counter(),
        "dispositions": Counter(),
        "top_fail_reasons": Counter(),
        "hitl_policies_seen": Counter(),
    })
    for r in rows:
        app = r["app_id"]
        per_app[app]["runs"] += 1
        per_app[app]["bands"][r["score_band"]] += 1
        if r["disposition"]:
            per_app[app]["dispositions"][r["disposition"]] += 1
        for reason in r["fail_reasons"]:
            per_app[app]["top_fail_reasons"][str(reason)] += 1
        per_app[app]["hitl_policies_seen"][r["hitl_policy"]] += 1

    # Normalize Counters to dicts for JSON serialization; keep only top-5 reasons.
    summary = {}
    for app, stats in per_app.items():
        summary[app] = {
            "runs": stats["runs"],
            "band_counts": dict(stats["bands"]),
            "disposition_counts": dict(stats["dispositions"]),
            "top_5_fail_reasons": dict(stats["top_fail_reasons"].most_common(5)),
            "hitl_policies_seen": dict(stats["hitl_policies_seen"]),
            "pass_rate": (stats["bands"].get("pass", 0) / stats["runs"]) if stats["runs"] else 0.0,
        }
    return {
        "week": _iso_week_tag(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ledger_source": str(_ledger_path()),
        "total_runs": len(rows),
        "per_app": summary,
    }


def _render_markdown(report: dict) -> str:
    lines = [
        f"# Eval Harness Weekly Report — {report['week']}",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Ledger: `{report['ledger_source']}`",
        f"- Total runs this week: {report['total_runs']}",
        "",
        "## Per-App Summary",
        "",
        "| App | Runs | Pass Rate | Top Disposition | HITL Mix |",
        "|---|---:|---:|---|---|",
    ]
    for app, s in sorted(report["per_app"].items()):
        top_disp = max(s["disposition_counts"].items(), key=lambda kv: kv[1], default=("-", 0))[0]
        hitl_mix = ", ".join(f"{k}:{v}" for k, v in s["hitl_policies_seen"].items())
        lines.append(
            f"| {app} | {s['runs']} | {s['pass_rate']:.2%} | {top_disp} | {hitl_mix} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Eval harness weekly rollup report")
    parser.add_argument(
        "--json-out",
        default=str(REPO_ROOT / "artifacts" / "calibration" / "eval_harness_weekly_latest.json"),
    )
    parser.add_argument(
        "--md-out",
        default=None,
        help="Optional Markdown output. Defaults to docs/reports/eval_harness/<YYYY-Www>.md",
    )
    args = parser.parse_args(argv)
    report = build_report()
    json_path = Path(args.json_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    md_path = Path(args.md_out) if args.md_out else (
        REPO_ROOT / "docs" / "reports" / "eval_harness" / f"{report['week']}.md"
    )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    print(
        f"[eval_harness_weekly_report] week={report['week']} "
        f"runs={report['total_runs']} apps={len(report['per_app'])} "
        f"json={json_path} md={md_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
