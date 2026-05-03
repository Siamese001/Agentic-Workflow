"""eval_trend_anomaly_detector — rolling-window anomaly detection (skeleton).

Plan: ``.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`` W5.P2.

Detects anomalies in eval outcomes by comparing rolling windows (1h / 6h /
24h) over the W5.P7 ``eval_harness_outcome`` ledger. Current detector is
a simple threshold check (pass-rate drop > 10 pp vs. baseline window);
real anomaly detection (EWMA, seasonal decomposition) is DEFERRED.

Output: ``artifacts/calibration/eval_trend_anomalies_latest.json`` —
shape-valid even when no anomalies detected.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

IS_SKELETON: bool = True


def _ledger_path() -> Path:
    return REPO_ROOT / "artifacts" / "ledgers" / "eval_harness_outcome.sqlite"


def _collect_by_window(window_hours: int) -> tuple[int, int]:
    """Return (pass_count, total_count) for rows in the last N hours."""
    path = _ledger_path()
    if not path.exists():
        return 0, 0
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
    try:
        conn = sqlite3.connect(str(path))
        try:
            rows = conn.execute(
                "SELECT score_band FROM events "
                "WHERE event_kind IN ('app_eval_bound','app_eval_unbound') "
                "AND ts_utc >= ?",
                (cutoff,),
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return 0, 0
    total = len(rows)
    passes = sum(1 for (b,) in rows if b == "pass")
    return passes, total


def build_report(drop_threshold_pp: float = 10.0) -> dict:
    windows = (1, 6, 24)
    window_stats = {}
    for w in windows:
        p, t = _collect_by_window(w)
        rate = (p / t) if t else None
        window_stats[f"{w}h"] = {"pass_count": p, "total": t, "pass_rate": rate}
    # Anomaly: compare each shorter window's pass_rate vs the 24h baseline.
    baseline = window_stats["24h"]["pass_rate"]
    anomalies = []
    if baseline is not None:
        for w_key in ("1h", "6h"):
            rate = window_stats[w_key]["pass_rate"]
            if rate is None or window_stats[w_key]["total"] < 5:
                continue  # insufficient data
            delta_pp = (baseline - rate) * 100.0
            if delta_pp >= drop_threshold_pp:
                anomalies.append({
                    "window": w_key,
                    "pass_rate": rate,
                    "baseline_24h": baseline,
                    "drop_pp": delta_pp,
                    "severity": "WARN",
                    "message": (
                        f"{w_key} pass-rate {rate:.2%} dropped {delta_pp:.1f}pp "
                        f"from 24h baseline {baseline:.2%}"
                    ),
                })
    return {
        "skeleton": IS_SKELETON,
        "ledger_source": str(_ledger_path()),
        "drop_threshold_pp": drop_threshold_pp,
        "windows": window_stats,
        "anomalies": anomalies,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Eval trend anomaly detector (skeleton)")
    parser.add_argument(
        "--out",
        default=str(REPO_ROOT / "artifacts" / "calibration" / "eval_trend_anomalies_latest.json"),
    )
    parser.add_argument("--threshold-pp", type=float, default=10.0)
    args = parser.parse_args(argv)
    report = build_report(drop_threshold_pp=args.threshold_pp)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"[eval_trend_anomaly_detector] skeleton=True "
        f"anomalies={len(report['anomalies'])} out={out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
