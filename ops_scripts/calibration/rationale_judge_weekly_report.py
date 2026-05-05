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


def _write_markdown(stats: dict[str, Any], week: str, output_path: Path) -> None:
    lines = [
        f"# Rationale Judge Weekly Calibration Report — {week}",
        "",
        f"**Generated**: {date.today().isoformat()}  ",
        f"**Holdout**: `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`  ",
        f"**Judge**: `RationaleQualityJudge v2` (IS_STUB=False, deterministic heuristic)",
        "",
        "## Global Calibration",
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
            f"|--------|-------|-----------|---------|",
            f"| Global Spearman ρ | {global_rho:.3f} | ≥ 0.80 | {verdict} |",
            f"| Unknown rate | {unknown_rate:.1%} | — | — |",
            f"| Holdout examples | {n_total} | 100 | {'✅' if n_total >= 100 else '❌'} |",
            "",
            "## Per-Dimension Calibration",
            "",
            "| Dim | Spearman ρ | n | Threshold | Verdict |",
            "|-----|-----------|---|-----------|---------|",
        ]
        for dim, d in sorted(stats.get("per_dim", {}).items()):
            rho = d["spearman"]
            n = d["n"]
            v = "✅" if d["pass"] else "❌"
            lines.append(f"| {dim} | {rho:.3f} | {n} | ≥ 0.70 | {v} |")
        lines += [
            "",
            "## Notes",
            "",
            "- Calibration is based on the synthetic holdout dataset seeded in W1.",
            "  Replace with human-labeled examples when available.",
            "- The deterministic heuristic scorer targets Spearman ≥ 0.80 globally",
            "  and ≥ 0.70 per-dim as a floor for promotion.",
            "- Future work: full LLM judge with Spearman ≥ 0.85 (requires human labels).",
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

    _ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = _ARTIFACTS_DIR / f"rationale_judge_{week}.json"
    json_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"JSON report: {json_path}")

    md_path = _REPORTS_DIR / f"{week}.md"
    _write_markdown(stats, week, md_path)
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
