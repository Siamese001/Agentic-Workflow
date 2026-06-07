"""ops_scripts.calibration.lic_judge_spearman_calibration — DS1-P2.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-calibration-holdout-e8f1c4.md W5 DS1-P2

Offline Spearman rank-correlation calibration for the 5 heuristic lic judges.

Reads the JSONL produced by lic_judge_holdout_ingest.py, runs each judge's
grade() against the stored run_context, computes Spearman ρ between judge
scores and human_scores, and emits a calibration report.

Design constraints
------------------
- Offline-only: never called from the hot path.
- No provider API calls.  No subprocess calls.
- No durable writes to judge source files — flag updates are advisory output.
- scipy.stats is optional: falls back to a pure-Python rank correlation when
  scipy is unavailable (allows CI without full scipy install).
- Gate: any judge with ρ < SPEARMAN_THRESHOLD emits a WARN line.
- Exit code 0 when all judges pass; 1 when any judge fails.

Output (stdout)
---------------
Per-judge table row + summary line. Machine-readable JSON optional via --json.

Usage
-----
  python ops_scripts/calibration/lic_judge_spearman_calibration.py \\
      --corpus artifacts/calibration/lic_holdout_corpus.jsonl \\
      --threshold 0.80

  python ops_scripts/calibration/lic_judge_spearman_calibration.py --help
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SPEARMAN_THRESHOLD: float = 0.80

JUDGE_MODULE_MAP: dict[str, str] = {
    "lic::ask_friction_judge::v1":        "apps_lic.engines.judges.ask_friction_judge",
    "lic::antipattern_clean_judge::v1":   "apps_lic.engines.judges.antipattern_clean_judge",
    "lic::proof_appropriate_judge::v1":   "apps_lic.engines.judges.proof_appropriate_judge",
    "lic::personalization_judge::v1":     "apps_lic.engines.judges.personalization_judge",
    "lic::asymmetric_insight_judge::v1":  "apps_lic.engines.judges.asymmetric_insight_judge",
    "lic::response_likelihood_judge::v2": "apps_lic.engines.judges.response_likelihood_judge",
    "lic::brand_voice_judge::v2":         "apps_lic.engines.judges.brand_voice_judge",
}

# ---------------------------------------------------------------------------
# Pure-Python Spearman fallback (no scipy required)
# ---------------------------------------------------------------------------


def _ranks(xs: list[float]) -> list[float]:
    """Return fractional ranks (average ties) for a list of floats."""
    n = len(xs)
    order = sorted(range(n), key=lambda i: xs[i])
    ranks: list[float] = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and xs[order[j]] == xs[order[i]]:
            j += 1
        avg_rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            ranks[order[k]] = avg_rank
        i = j
    return ranks


def spearman_rho(xs: list[float], ys: list[float]) -> float:
    """Compute Spearman rank correlation between xs and ys."""
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have equal length")
    n = len(xs)
    if n < 2:
        return float("nan")

    try:
        from scipy.stats import spearmanr  # type: ignore[import]
        result = spearmanr(xs, ys)
        rho = float(result.statistic if hasattr(result, "statistic") else result.correlation)
        return rho
    except ImportError:
        pass

    # Pure-Python fallback
    rx = _ranks(xs)
    ry = _ranks(ys)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((r - mean_rx) ** 2 for r in rx))
    den_y = math.sqrt(sum((r - mean_ry) ** 2 for r in ry))
    if den_x == 0 or den_y == 0:
        return float("nan")
    return num / (den_x * den_y)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class JudgeCalibrationResult:
    """Per-judge calibration outcome."""

    grader_id: str
    n_samples: int
    spearman_rho: float
    threshold: float
    passed: bool
    unknown_count: int   # rows where judge returned GRADER_UNKNOWN_SENTINEL
    mean_judge_score: float
    mean_human_score: float


# ---------------------------------------------------------------------------
# Judge loading
# ---------------------------------------------------------------------------


def _load_judge_grade_fn(grader_id: str):
    """Return the module-level grade(dim, run_context) callable for grader_id."""
    module_path = JUDGE_MODULE_MAP.get(grader_id)
    if module_path is None:
        raise ValueError(f"Unknown grader_id: {grader_id}")
    mod = importlib.import_module(module_path)
    grade_fn = getattr(mod, "grade", None)
    if grade_fn is None:
        raise AttributeError(f"Module {module_path} has no module-level grade() function")
    return grade_fn


# ---------------------------------------------------------------------------
# Calibration runner
# ---------------------------------------------------------------------------


def run_calibration(
    corpus_path: Path,
    *,
    threshold: float = SPEARMAN_THRESHOLD,
    grader_ids: list[str] | None = None,
) -> list[JudgeCalibrationResult]:
    """Run Spearman calibration over all judges present in the corpus.

    Parameters
    ----------
    corpus_path : Path to JSONL corpus produced by lic_judge_holdout_ingest.
    threshold   : Minimum acceptable Spearman ρ (default 0.80).
    grader_ids  : Optional whitelist of grader_ids to evaluate. None = all.
    """
    from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
        GRADER_UNKNOWN_SENTINEL,
    )

    # Group corpus rows by grader_id
    by_judge: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with open(corpus_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            gid = row.get("grader_id", "")
            if grader_ids is None or gid in grader_ids:
                by_judge[gid].append(row)

    results: list[JudgeCalibrationResult] = []

    for gid, rows in sorted(by_judge.items()):
        try:
            grade_fn = _load_judge_grade_fn(gid)
        except (ValueError, AttributeError, ImportError) as exc:
            print(f"[WARN] Cannot load judge '{gid}': {exc}", file=sys.stderr)
            continue

        human_scores: list[float] = []
        judge_scores: list[float] = []
        unknown_count = 0

        for row in rows:
            run_context = row.get("run_context", {})
            human_score = float(row["human_score"])
            try:
                raw_score, _ = grade_fn(None, run_context)
            except Exception as exc:  # noqa: BLE001
                # guardian: allow-broad-except -- judge errors in calibration
                # must not abort the full calibration run; count as unknown.
                unknown_count += 1
                continue

            if raw_score is GRADER_UNKNOWN_SENTINEL or raw_score is None:
                unknown_count += 1
                continue

            judge_scores.append(float(raw_score))
            human_scores.append(human_score)

        n = len(judge_scores)
        if n < 2:
            rho = float("nan")
        else:
            rho = spearman_rho(judge_scores, human_scores)

        passed = (not math.isnan(rho)) and rho >= threshold

        results.append(JudgeCalibrationResult(
            grader_id=gid,
            n_samples=n,
            spearman_rho=rho,
            threshold=threshold,
            passed=passed,
            unknown_count=unknown_count,
            mean_judge_score=sum(judge_scores) / n if n else float("nan"),
            mean_human_score=sum(human_scores) / n if n else float("nan"),
        ))

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _format_table(results: list[JudgeCalibrationResult]) -> str:
    lines = [
        f"{'grader_id':<45} {'n':>6} {'ρ':>8} {'threshold':>10} {'pass?':>7} {'unknowns':>9}",
        "-" * 95,
    ]
    for r in results:
        rho_str = f"{r.spearman_rho:.4f}" if not math.isnan(r.spearman_rho) else "  n/a"
        pass_str = "PASS" if r.passed else "FAIL"
        lines.append(
            f"{r.grader_id:<45} {r.n_samples:>6} {rho_str:>8} {r.threshold:>10.2f} "
            f"{pass_str:>7} {r.unknown_count:>9}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Spearman rank-correlation calibration for lic judges."
    )
    p.add_argument(
        "--corpus",
        default="artifacts/calibration/lic_holdout_corpus.jsonl",
        help="JSONL corpus from lic_judge_holdout_ingest.py",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=SPEARMAN_THRESHOLD,
        help=f"Minimum Spearman ρ to pass (default {SPEARMAN_THRESHOLD})",
    )
    p.add_argument(
        "--graders",
        nargs="*",
        default=None,
        help="Whitelist of grader_ids to evaluate (default: all in corpus)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        dest="emit_json",
        help="Emit machine-readable JSON to stdout instead of table",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Optional path to write JSON report (also prints table to stdout)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    corpus_path = Path(args.corpus)

    if not corpus_path.exists():
        print(f"ERROR: corpus not found: {corpus_path}", file=sys.stderr)
        print(
            "Run lic_judge_holdout_ingest.py first to produce the corpus.",
            file=sys.stderr,
        )
        return 1

    # Ensure repo root is on sys.path for judge imports
    repo_root = Path(__file__).resolve().parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    results = run_calibration(
        corpus_path,
        threshold=args.threshold,
        grader_ids=args.graders,
    )

    if not results:
        print("No results produced — corpus may be empty or no judges matched.", file=sys.stderr)
        return 1

    if args.emit_json:
        report = [
            {
                "grader_id": r.grader_id,
                "n_samples": r.n_samples,
                "spearman_rho": None if math.isnan(r.spearman_rho) else r.spearman_rho,
                "threshold": r.threshold,
                "passed": r.passed,
                "unknown_count": r.unknown_count,
                "mean_judge_score": None if math.isnan(r.mean_judge_score) else r.mean_judge_score,
                "mean_human_score": None if math.isnan(r.mean_human_score) else r.mean_human_score,
            }
            for r in results
        ]
        print(json.dumps(report, indent=2))
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    else:
        print(_format_table(results))
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(_format_table(results), encoding="utf-8")

    all_pass = all(r.passed for r in results)
    fail_judges = [r.grader_id for r in results if not r.passed]
    if fail_judges:
        print(
            f"\nWARN: {len(fail_judges)} judge(s) below threshold ρ={args.threshold}: "
            + ", ".join(fail_judges),
            file=sys.stderr,
        )

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "JudgeCalibrationResult",
    "run_calibration",
    "spearman_rho",
    "SPEARMAN_THRESHOLD",
    "JUDGE_MODULE_MAP",
]
