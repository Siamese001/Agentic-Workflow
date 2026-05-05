"""Weekly calibration report for RationaleQualityJudge.

Plan: apps-underwriting-ai-d3-rationale-judge-f2c8d5 W3.P2.

Reads the eval_harness_outcome ledger and the holdout dataset.
Emits a JSON summary and a Markdown report under::

    docs/reports/eval_harness/rationale_judge/YYYY-Www.md

Usage::

    python ops_scripts/calibration/rationale_judge_weekly_report.py [--week YYYY-Www]

Outputs
-------
- JSON report at: artifacts/calibration/rationale_judge_<YYYY-Www>.json
- Markdown report at: docs/reports/eval_harness/rationale_judge/<YYYY-Www>.md

Environment variables
---------------------
RATIONALE_JUDGE_REPORT_BYPASS=1
    Skip report generation and exit 0.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_BYPASS = os.getenv("RATIONALE_JUDGE_REPORT_BYPASS", "").strip() == "1"

_HOLDOUT_PATH = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"
_ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "calibration"
_REPORTS_DIR = REPO_ROOT / "docs" / "reports" / "eval_harness" / "rationale_judge"
_LEDGER_PATH = REPO_ROOT / "artifacts" / "ledgers" / "eval_harness_outcome.sqlite"
_APP_ID = "apps_underwriting_ai"
_LEDGER_LIMIT = 500


def _iso_week(d: date | None = None) -> str:
    d = d or date.today()
    return f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"


def _spearman(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0

    def _rank(seq: list[float]) -> list[float]:
        sorted_idx = sorted(range(n), key=lambda i: seq[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and seq[sorted_idx[j + 1]] == seq[sorted_idx[j]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[sorted_idx[k]] = avg_rank
            i = j + 1
        return ranks

    rx, ry = _rank(x), _rank(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    std_rx = (sum((r - mean_rx) ** 2 for r in rx) ** 0.5) or 1e-9
    std_ry = (sum((r - mean_ry) ** 2 for r in ry) ** 0.5) or 1e-9
    return cov / (std_rx * std_ry)


def _query_ledger() -> dict[str, Any]:
    """Read recent apps_underwriting_ai rows from eval_harness_outcome ledger.

    Returns a dict with keys: ``available``, ``sample_size``, ``pass_rate``,
    ``score_band_counts``, ``weekly_pass_rates`` (last 4 iso-weeks),
    ``holdout_comparison`` (populated when Spearman data is present).
    """
    if not _LEDGER_PATH.exists():
        return {"available": False, "reason": "ledger_not_found"}

    try:
        conn = sqlite3.connect(str(_LEDGER_PATH))
    except sqlite3.Error as exc:
        return {"available": False, "reason": str(exc)}

    try:
        rows = conn.execute(
            """
            SELECT score_band, score_numeric, ts_utc, prediction_json
            FROM events
            WHERE event_kind IN ('app_eval_bound', 'app_eval_unbound')
              AND repo_area = ?
            ORDER BY ts_utc DESC
            LIMIT ?
            """,
            (_APP_ID, _LEDGER_LIMIT),
        ).fetchall()
    except sqlite3.Error as exc:
        conn.close()
        return {"available": False, "reason": str(exc)}
    finally:
        conn.close()

    if not rows:
        return {"available": True, "sample_size": 0, "pass_rate": None,
                "score_band_counts": {}, "weekly_pass_rates": [],
                "holdout_comparison": None}

    band_counts: dict[str, int] = {}
    week_pass: dict[str, list[int]] = {}
    for band, score_num, ts_utc, pred_raw in rows:
        band = band or "unknown"
        band_counts[band] = band_counts.get(band, 0) + 1
        iso_week = ""
        if ts_utc:
            try:
                d = date.fromisoformat(ts_utc[:10])
                iso_week = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
            except ValueError:
                pass
        if iso_week:
            week_pass.setdefault(iso_week, []).append(1 if band == "pass" else 0)

    total = sum(band_counts.values()) or 1
    pass_rate = band_counts.get("pass", 0) / total

    recent_weeks = sorted(week_pass)[-4:]
    weekly_pass_rates = [
        {"week": w, "pass_rate": round(sum(week_pass[w]) / len(week_pass[w]), 4),
         "n": len(week_pass[w])}
        for w in recent_weeks
    ]

    return {
        "available": True,
        "sample_size": len(rows),
        "pass_rate": round(pass_rate, 4),
        "score_band_counts": band_counts,
        "weekly_pass_rates": weekly_pass_rates,
        "holdout_comparison": None,
    }


def _load_holdout() -> list[dict[str, Any]]:
    try:
        import yaml
    except ImportError:
        return []
    if not _HOLDOUT_PATH.exists():
        return []
    data = yaml.safe_load(_HOLDOUT_PATH.read_text(encoding="utf-8"))
    return data.get("examples", [])


def _compute_calibration_stats(
    examples: list[dict[str, Any]],
) -> dict[str, Any]:
    if not examples:
        return {"status": "no_holdout_data", "global_spearman": None, "per_dim": {}}

    try:
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        from apps_underwriting_ai.engines.judges.rationale_quality_judge import grade
    except ImportError as exc:
        return {"status": f"import_error: {exc}", "global_spearman": None, "per_dim": {}}

    def _score(ex: dict[str, Any]) -> float:
        ctx = {
            "output": {
                "rationale": ex.get("rationale_text", ""),
                "evidence_refs": ex.get("evidence_refs", []),
            }
        }
        s, _ = grade(None, ctx)
        return 0.0 if s is GRADER_UNKNOWN_SENTINEL else float(s)

    all_judge = [_score(e) for e in examples]
    all_gt = [float(e["ground_truth_score"]) for e in examples]
    global_rho = _spearman(all_judge, all_gt)

    dims = sorted({e["dim_id"] for e in examples})
    per_dim: dict[str, dict[str, Any]] = {}
    for dim in dims:
        subset = [e for e in examples if e["dim_id"] == dim]
        j = [_score(e) for e in subset]
        g = [float(e["ground_truth_score"]) for e in subset]
        rho = _spearman(j, g)
        per_dim[dim] = {
            "spearman": round(rho, 4),
            "n": len(subset),
            "pass": rho >= 0.70,
        }

    unknown_count = sum(1 for s in all_judge if s == 0.0)
    unknown_rate = unknown_count / len(all_judge) if all_judge else 0.0

    return {
        "status": "ok",
        "global_spearman": round(global_rho, 4),
        "global_pass": global_rho >= 0.80,
        "n_total": len(examples),
        "unknown_rate": round(unknown_rate, 4),
        "per_dim": per_dim,
    }


def _write_markdown(
    stats: dict[str, Any],
    ledger: dict[str, Any],
    week: str,
    output_path: Path,
) -> None:
    lines = [
        f"# Rationale Judge Weekly Calibration Report — {week}",
        "",
        f"**Generated**: {date.today().isoformat()}  ",
        f"**Holdout**: `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`  ",
        f"**Judge**: `RationaleQualityJudge v2` (IS_STUB=False, deterministic heuristic)",
        "",
        "## Global Calibration (Holdout)",
        "",
    ]

    status = stats.get("status", "unknown")
    if status != "ok":
        lines += [f"**Status**: {status}", "", "*No calibration data available.*", ""]
    else:
        global_rho = stats.get("global_spearman")
        global_pass = stats.get("global_pass", False)
        n_total = stats.get("n_total", 0)
        unknown_rate = stats.get("unknown_rate", 0.0)
        verdict = "✅ PASS" if global_pass else "❌ FAIL"
        lines += [
            f"| Metric | Value | Threshold | Verdict |",
            f"|--------|-------|-----------|---------|"  ,
            f"| Global Spearman ρ | {global_rho:.3f} | ≥ 0.80 | {verdict} |",
            f"| Unknown rate | {unknown_rate:.1%} | — | — |",
            f"| Holdout examples | {n_total} | 100 | {'✅' if n_total >= 100 else '❌'} |",
            "",
            "## Per-Dimension Calibration",
            "",
            "| Dim | Spearman ρ | n | Threshold | Verdict |",
            "|-----|-----------|---|-----------|---------|"  ,
        ]
        for dim, d in sorted(stats.get("per_dim", {}).items()):
            rho = d["spearman"]
            n = d["n"]
            v = "✅" if d["pass"] else "❌"
            lines.append(f"| {dim} | {rho:.3f} | {n} | ≥ 0.70 | {v} |")

    lines += ["", "## Production Eval-Harness Outcomes (Last 4 Weeks)", ""]
    if not ledger.get("available"):
        reason = ledger.get("reason", "unavailable")
        lines += [f"*Ledger not available: {reason}*", ""]
    elif ledger.get("sample_size", 0) == 0:
        lines += ["*No apps_underwriting_ai rows in eval_harness_outcome ledger yet.*", ""]
    else:
        pass_rate = ledger.get("pass_rate")
        sample = ledger.get("sample_size", 0)
        bands = ledger.get("score_band_counts", {})
        lines += [
            f"| Metric | Value |",
            f"|--------|-------|"  ,
            f"| Total eval rows | {sample} |",
            f"| Pass rate | {pass_rate:.1%} |",
        ]
        for band, cnt in sorted(bands.items()):
            lines.append(f"| Band: {band} | {cnt} |")
        lines.append("")
        weekly = ledger.get("weekly_pass_rates", [])
        if weekly:
            lines += [
                "### Pass Rate Trend",
                "",
                "| Week | Pass Rate | n |",
                "|------|-----------|---|"  ,
            ]
            for entry in weekly:
                lines.append(
                    f"| {entry['week']} | {entry['pass_rate']:.1%} | {entry['n']} |"
                )
            lines.append("")

    lines += [
        "## Notes",
        "",
        "- Calibration is based on the synthetic holdout dataset seeded in W1.",
        "  Replace with human-labeled examples when available (DS-R1).",
        "- The deterministic heuristic scorer targets Spearman ≥ 0.80 globally",
        "  and ≥ 0.70 per-dim as a floor for promotion.",
        "- Future work: full LLM judge with Spearman ≥ 0.85 (DS-R2, requires human labels).",
        "- `holdout_comparison` will be populated once DS-R2 LLM judge is active.",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(week: str | None = None) -> None:
    if _BYPASS:
        print("BYPASS: RATIONALE_JUDGE_REPORT_BYPASS=1")
        sys.exit(0)

    week = week or _iso_week()
    print(f"Generating rationale judge weekly report for {week}...")

    examples = _load_holdout()
    stats = _compute_calibration_stats(examples)
    stats["week"] = week

    ledger = _query_ledger()
    stats["ledger"] = ledger
    stats["holdout_comparison"] = ledger.get("holdout_comparison")

    _ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _ARTIFACTS_DIR / f"rationale_judge_{week}.json"
    json_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"JSON report: {json_path}")

    md_path = _REPORTS_DIR / f"{week}.md"
    _write_markdown(stats, ledger, week, md_path)
    print(f"Markdown report: {md_path}")

    if stats.get("status") == "ok":
        global_pass = stats.get("global_pass", False)
        per_dim_fails = [
            d for d, v in stats.get("per_dim", {}).items() if not v["pass"]
        ]
        if not global_pass or per_dim_fails:
            print(
                f"WARNING: Calibration issues detected. "
                f"global_pass={global_pass} per_dim_fails={per_dim_fails}",
                file=sys.stderr,
            )
    if ledger.get("available") and ledger.get("sample_size", 0) > 0:
        print(
            f"Ledger: {ledger['sample_size']} rows, pass_rate={ledger['pass_rate']:.1%}"
        )
    else:
        print("Ledger: no data (ledger empty or not found — expected pre-production).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rationale judge weekly calibration report")
    parser.add_argument(
        "--week",
        type=str,
        default=None,
        help="ISO week string e.g. 2026-W20 (default: current week)",
    )
    args = parser.parse_args()
    main(week=args.week)
