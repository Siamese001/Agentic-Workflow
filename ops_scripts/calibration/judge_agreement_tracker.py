"""judge_agreement_tracker — Spearman agreement tracker.

Plan: ``.windsurf/plans/apps-eval-harness-deferred-e4a1b7.md`` W5.P1 (skeleton).
Promoted: ``.windsurf/plans/apps-research-deferred-scope-b7e3d2.md`` W4 (DS-1).

PROMOTION HISTORY
=================
- v1 skeleton (W5.P1): holdout_comparison=null; no real Spearman logic.
- **v2 (DS-1 W4)**: Real Spearman ρ computed for the ``citation_quality`` dim
  using the 60-pair holdout at
  ``apps_eval/fixtures/holdout/citation_quality_holdout.json``.
  IS_SKELETON flipped to False.
  ``holdout_comparison`` is now a per-dim dict with keys:
    dim_id, grader_id, n, spearman_rho, p_value, meets_threshold (ρ ≥ 0.80).

Usage:
    python ops_scripts/calibration/judge_agreement_tracker.py
    python ops_scripts/calibration/judge_agreement_tracker.py --out path/to/out.json

Adding a new dim's holdout:
    1. Drop a JSON file at apps_eval/fixtures/holdout/<dim_id>_holdout.json
       with schema: {dim_id, grader_id, n, pairs: [{model_score, human_label}]}
    2. Register the fixture path in HOLDOUT_FIXTURES below.
    3. Spearman computation is automatic — no further code change needed.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]

IS_SKELETON: bool = False
"""False — real Spearman calibration is active for citation_quality dim."""

HOLDOUT_FIXTURES: list[Path] = [
    REPO_ROOT / "apps_eval" / "fixtures" / "holdout" / "citation_quality_holdout.json",
    REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout_pairs.json",
]
"""Paths to human-labeled holdout JSON files. Each file must have schema:
{dim_id: str, grader_id: str, n: int, pairs: [{model_score: float, human_label: float}]}.

DS-R6: rationale_judge_holdout_pairs.json is auto-generated from the YAML holdout
by tools/underwriting/generate_holdout_pairs.py. Run that script after any
holdout YAML update to keep this fixture current.
"""


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


def _spearman_rho(x: list[float], y: list[float]) -> tuple[float, float]:
    """Compute Spearman rank correlation. Returns (rho, p_value)."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    try:
        from scipy.stats import spearmanr  # type: ignore[import]
        result = spearmanr(x, y)
        return float(result.statistic), float(result.pvalue)
    except ImportError:
        pass
    # Fallback: manual rank correlation
    def _ranks(seq: list[float]) -> list[float]:
        sorted_vals = sorted(enumerate(seq), key=lambda t: t[1])
        ranks = [0.0] * len(seq)
        for rank, (orig_idx, _) in enumerate(sorted_vals, 1):
            ranks[orig_idx] = float(rank)
        return ranks
    rx, ry = _ranks(x), _ranks(y)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    denom_x = sum((rx[i] - mean_rx) ** 2 for i in range(n)) ** 0.5
    denom_y = sum((ry[i] - mean_ry) ** 2 for i in range(n)) ** 0.5
    if denom_x == 0 or denom_y == 0:
        return 0.0, 1.0
    rho = num / (denom_x * denom_y)
    return rho, 1.0


def _load_holdout_comparisons() -> list[dict]:
    """Load all registered holdout fixtures and compute per-dim Spearman ρ."""
    results = []
    for fixture_path in HOLDOUT_FIXTURES:
        if not fixture_path.exists():
            continue
        try:
            data = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pairs = data.get("pairs") or []
        model_scores = [float(p["model_score"]) for p in pairs if "model_score" in p and "human_label" in p]
        human_labels = [float(p["human_label"]) for p in pairs if "model_score" in p and "human_label" in p]
        if len(model_scores) < 3:
            continue
        rho, pval = _spearman_rho(model_scores, human_labels)
        results.append({
            "dim_id": data.get("dim_id", fixture_path.stem),
            "grader_id": data.get("grader_id"),
            "n": len(model_scores),
            "spearman_rho": round(rho, 4),
            "p_value": round(pval, 6),
            "meets_threshold": rho >= 0.80,
            "holdout_fixture": str(fixture_path.relative_to(REPO_ROOT)),
        })
    return results


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
    holdout_comparisons = _load_holdout_comparisons()
    return {
        "skeleton": IS_SKELETON,
        "ledger_source": str(_ledger_path()),
        "sample_size": len(outcomes),
        "per_app": per_app,
        "global_dim_unknown_rate": (total_unknown / total_dims) if total_dims else 0.0,
        "holdout_comparison": holdout_comparisons if holdout_comparisons else None,
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
    hc = report.get("holdout_comparison") or []
    hc_summary = ", ".join(
        f"{d['dim_id']}:rho={d['spearman_rho']:.4f}" for d in hc
    ) if hc else "none"
    print(
        f"[judge_agreement_tracker] skeleton={IS_SKELETON} n={report['sample_size']} "
        f"apps={len(report['per_app'])} holdout_dims={len(hc)} ({hc_summary}) out={out_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
