"""judge_agreement_tracker — Spearman agreement skeleton (stub).

Plan: ``.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`` W5.P1.

SKELETON STATUS
===============

This script is a SKELETON. Real Spearman-correlation calibration requires
a human-labeled holdout set, which is DEFERRED to a separate plan
(parent plan's W5.P1 was not executed — no holdout fixtures exist).

Current behavior: reads ``artifacts/ledgers/eval_harness_outcome.sqlite``
(the W5.P7 ledger from the parent plan) and produces a shape-valid JSON
report at ``artifacts/calibration/judge_agreement_latest.json`` with:
  - per-app pass-rate (from `score_band`)
  - per-dim UNKNOWN rate
  - "holdout_comparison": null (pending real holdout)

Usage:
    python ops_scripts/calibration/judge_agreement_tracker.py
    python ops_scripts/calibration/judge_agreement_tracker.py --since 7d

Promotion path to real calibration:
    1. Add human-labeled holdout fixtures under apps_eval/fixtures/holdout/
    2. Replace holdout_comparison=null with per-dim Spearman ρ over the
       last N matched (ledger_score, human_score) pairs
    3. Flip this file's SKELETON flag to False
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

IS_SKELETON: bool = True
"""True while real Spearman calibration logic is DEFERRED."""


def _ledger_path() -> Path:
    return REPO_ROOT / "artifacts" / "ledgers" / "eval_harness_outcome.sqlite"


def _collect_outcomes() -> list[dict]:
    """Read the eval_harness_outcome ledger. Returns empty list on any failure."""
    path = _ledger_path()
    if not path.exists():
        return []
    try:
        conn = sqlite3.connect(str(path))
        try:
            rows = conn.execute(
                "SELECT repo_area, score_band, score_numeric, prediction_json "
                "FROM events WHERE event_kind IN ('app_eval_bound','app_eval_unbound') "
                "ORDER BY ts_utc DESC LIMIT 1000"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []
    out = []
    for repo_area, band, score, pred_raw in rows:
        try:
            pred = json.loads(pred_raw) if pred_raw else {}
        except json.JSONDecodeError:
            pred = {}
        out.append({
            "app_id": pred.get("app_id") or repo_area,
            "score_band": band,
            "overall_score": score,
            "dim_unknown_count": int(pred.get("dim_unknown_count", 0)),
            "dim_count": int(pred.get("dim_count", 0)),
        })
    return out


def build_report() -> dict:
    outcomes = _collect_outcomes()
    by_app_bands: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total_dims = 0
    total_unknown = 0
    for o in outcomes:
        by_app_bands[o["app_id"]][o["score_band"] or "unknown"] += 1
        total_dims += o["dim_count"]
        total_unknown += o["dim_unknown_count"]
    per_app = {}
    for app, bands in by_app_bands.items():
        total = sum(bands.values()) or 1
        per_app[app] = {
            "band_counts": dict(bands),
            "n": sum(bands.values()),
            "pass_rate": bands.get("pass", 0) / total,
            "escalate_rate": bands.get("escalate", 0) / total,
            "deny_rate": bands.get("deny", 0) / total,
        }
    return {
        "skeleton": IS_SKELETON,
        "ledger_source": str(_ledger_path()),
        "sample_size": len(outcomes),
        "per_app": per_app,
        "global_dim_unknown_rate": (total_unknown / total_dims) if total_dims else 0.0,
        # Real Spearman ρ goes here once a holdout set exists.
        "holdout_comparison": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Judge-human agreement tracker (skeleton)")
    parser.add_argument(
        "--out",
        default=str(REPO_ROOT / "artifacts" / "calibration" / "judge_agreement_latest.json"),
    )
    args = parser.parse_args(argv)
    report = build_report()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"[judge_agreement_tracker] skeleton=True n={report['sample_size']} "
        f"apps={len(report['per_app'])} out={out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
