"""CI gate: check_rationale_judge_calibration.

Plan: apps-underwriting-ai-d3-rationale-judge-f2c8d5 W3.P1.

Verifies that the RationaleQualityJudge achieves Spearman ≥ 0.80
against the synthetic holdout dataset, ensuring calibration does not
regress as the judge model evolves.

Exit codes
----------
0   All calibration checks pass.
1   One or more checks fail (Spearman too low or dataset malformed).
2   Configuration error (missing holdout file, import failure, YAML
    unavailable) — advisory mode exits 0 with a WARNING to avoid
    blocking CI in environments where pyyaml is not installed.

Environment variables
---------------------
RATIONALE_JUDGE_CALIB_FAIL_CLOSED=1
    If set, errors that would otherwise be advisory (exit 2) become
    hard failures (exit 1).

RATIONALE_JUDGE_CALIB_BYPASS=1
    Skip all checks and exit 0 — for scripted batch runs or
    acknowledged exploratory sessions.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_BYPASS = os.getenv("RATIONALE_JUDGE_CALIB_BYPASS", "").strip() == "1"
# DS-R5 flip 2026-05-06: default fail-closed now that heuristic v2 judge is
# confirmed at global Spearman=0.812 >= 0.80. Override with
# RATIONALE_JUDGE_CALIB_FAIL_CLOSED=0 to revert to advisory.
_FAIL_CLOSED = os.getenv("RATIONALE_JUDGE_CALIB_FAIL_CLOSED", "1").strip() == "1"

_HOLDOUT_PATH = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"

_GLOBAL_SPEARMAN_MIN = 0.80
_PER_DIM_SPEARMAN_MIN = 0.70


def _advisory_exit(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr)
    if _FAIL_CLOSED:
        sys.exit(1)
    sys.exit(0)


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


def _run_calibration_check() -> int:
    try:
        import yaml
    except ImportError:
        _advisory_exit("pyyaml not installed — skipping rationale judge calibration check")
        return 0

    if not _HOLDOUT_PATH.exists():
        _advisory_exit(f"Holdout file not found: {_HOLDOUT_PATH}")
        return 0

    try:
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
            GRADER_UNKNOWN_SENTINEL,
        )
        from apps_underwriting_ai.engines.judges.rationale_quality_judge import (
            IS_CALIBRATED,
            IS_STUB,
            grade,
        )
    except ImportError as exc:
        _advisory_exit(f"Import failure — cannot load rationale judge: {exc}")
        return 0

    data = yaml.safe_load(_HOLDOUT_PATH.read_text(encoding="utf-8"))
    examples: list[dict[str, Any]] = data.get("examples", [])

    errors: list[str] = []

    if IS_STUB:
        errors.append("FAIL: RationaleQualityJudge.IS_STUB is True — judge is not promoted")
    if not IS_CALIBRATED:
        errors.append("FAIL: RationaleQualityJudge.IS_CALIBRATED is False")

    if len(examples) < 100:
        errors.append(
            f"FAIL: Holdout has {len(examples)} examples; require ≥ 100"
        )

    def _score_example(ex: dict[str, Any]) -> float:
        ctx = {
            "output": {
                "rationale": ex.get("rationale_text", ""),
                "evidence_refs": ex.get("evidence_refs", []),
            }
        }
        s, _ = grade(None, ctx)
        return 0.0 if s is GRADER_UNKNOWN_SENTINEL else float(s)

    all_judge = [_score_example(e) for e in examples]
    all_gt = [float(e["ground_truth_score"]) for e in examples]

    global_rho = _spearman(all_judge, all_gt)
    if global_rho < _GLOBAL_SPEARMAN_MIN:
        errors.append(
            f"FAIL: global Spearman={global_rho:.3f} < threshold={_GLOBAL_SPEARMAN_MIN}"
        )
    else:
        print(f"OK: global Spearman={global_rho:.3f} >= {_GLOBAL_SPEARMAN_MIN}")

    dims = sorted({e["dim_id"] for e in examples})
    for dim in dims:
        subset = [e for e in examples if e["dim_id"] == dim]
        j = [_score_example(e) for e in subset]
        g = [float(e["ground_truth_score"]) for e in subset]
        rho = _spearman(j, g)
        if rho < _PER_DIM_SPEARMAN_MIN:
            errors.append(
                f"FAIL: dim={dim} Spearman={rho:.3f} < threshold={_PER_DIM_SPEARMAN_MIN}"
            )
        else:
            print(f"OK: dim={dim} Spearman={rho:.3f} >= {_PER_DIM_SPEARMAN_MIN}")

    if errors:
        for msg in errors:
            print(msg, file=sys.stderr)
        return 1
    return 0


def main() -> None:
    if _BYPASS:
        print("BYPASS: RATIONALE_JUDGE_CALIB_BYPASS=1 — skipping calibration check")
        sys.exit(0)
    sys.exit(_run_calibration_check())


if __name__ == "__main__":
    main()
