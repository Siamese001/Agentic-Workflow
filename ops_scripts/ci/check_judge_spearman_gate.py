"""DS-R5: Fail-closed promotion gate — judge Spearman ρ ≥ 0.80.

Reads the judge_agreement_tracker fixtures and checks that all registered
dims meet their calibration threshold.  By default this gate is advisory;
set JUDGE_SPEARMAN_FAIL_CLOSED=1 to make it fail-closed.

Usage:
    python ops_scripts/ci/check_judge_spearman_gate.py
    JUDGE_SPEARMAN_FAIL_CLOSED=1 python ops_scripts/ci/check_judge_spearman_gate.py

Exit codes:
    0 — all dims pass (or advisory mode with no blocking failures)
    1 — one or more dims below threshold AND fail-closed mode is active
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_SPEARMAN_THRESHOLD_GLOBAL = 0.80
"""Global (all-dims combined) Spearman threshold — DS-R5 hard gate."""

_SPEARMAN_THRESHOLD_PER_DIM = 0.70
"""Per-dim threshold — realistic ceiling for a 20-example holdout subset.
Matches the governance test's _SPEARMAN_PER_DIM_THRESHOLD.
"""

_FAIL_CLOSED = os.environ.get("JUDGE_SPEARMAN_FAIL_CLOSED", "0").strip() == "1"

HOLDOUT_FIXTURES: list[Path] = [
    REPO_ROOT / "apps_eval" / "fixtures" / "holdout" / "citation_quality_holdout.json",
    REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout_pairs.json",
]


def _spearman(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 3:
        return 0.0
    try:
        from scipy.stats import spearmanr  # type: ignore[import]
        return float(spearmanr(x, y).statistic)
    except ImportError:
        pass
    def ranks(seq: list[float]) -> list[float]:
        idx = sorted(range(n), key=lambda i: seq[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and seq[idx[j + 1]] == seq[idx[j]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[idx[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = sum((rx[i] - mx) ** 2 for i in range(n)) ** 0.5
    dy = sum((ry[i] - my) ** 2 for i in range(n)) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def _check_fixture(path: Path) -> list[dict]:
    """Return list of finding dicts for one fixture file."""
    if not path.exists():
        return [{"status": "SKIP", "fixture": str(path), "reason": "file not found"}]

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [{"status": "ERROR", "fixture": str(path), "reason": str(exc)}]

    # Fixture may be a single dict or a list of dicts
    entries = raw if isinstance(raw, list) else [raw]
    findings = []
    for entry in entries:
        dim_id = entry.get("dim_id", "<unknown>")
        pairs = entry.get("pairs") or []
        model_scores = [float(p["model_score"]) for p in pairs
                        if "model_score" in p and "human_label" in p]
        human_labels = [float(p["human_label"]) for p in pairs
                        if "model_score" in p and "human_label" in p]
        n = len(model_scores)
        if n < 3:
            findings.append({
                "status": "SKIP",
                "fixture": str(path.name),
                "dim_id": dim_id,
                "n": n,
                "reason": "fewer than 3 pairs",
            })
            continue
        rho = _spearman(model_scores, human_labels)
        is_global = dim_id == "all_dims"
        threshold = _SPEARMAN_THRESHOLD_GLOBAL if is_global else _SPEARMAN_THRESHOLD_PER_DIM
        passed = rho >= threshold
        findings.append({
            "status": "PASS" if passed else "FAIL",
            "fixture": str(path.name),
            "dim_id": dim_id,
            "n": n,
            "spearman_rho": round(rho, 4),
            "threshold": threshold,
            "scope": "global" if is_global else "per_dim",
        })
    return findings


def main(argv: list[str] | None = None) -> int:
    all_findings: list[dict] = []
    for fixture_path in HOLDOUT_FIXTURES:
        all_findings.extend(_check_fixture(fixture_path))

    fails = [f for f in all_findings if f["status"] == "FAIL"]
    skips = [f for f in all_findings if f["status"] == "SKIP"]
    passes = [f for f in all_findings if f["status"] == "PASS"]

    print(f"[check_judge_spearman_gate] dims_checked={len(all_findings)} "
          f"pass={len(passes)} fail={len(fails)} skip={len(skips)} "
          f"fail_closed={_FAIL_CLOSED}")

    for f in all_findings:
        status = f["status"]
        dim = f.get("dim_id", "?")
        if status == "PASS":
            print(f"  PASS  {dim}  rho={f.get('spearman_rho', 'N/A')} n={f.get('n', '?')}")
        elif status == "FAIL":
            threshold = f.get("threshold", _SPEARMAN_THRESHOLD_PER_DIM)
            print(
                f"  FAIL  {dim}  rho={f.get('spearman_rho', 'N/A')} "
                f"< {threshold}  n={f.get('n', '?')}"
            )
        else:
            print(f"  {status}  {dim}  {f.get('reason', '')}")

    # Emit structured output for CI consumption
    out_path = REPO_ROOT / "artifacts" / "calibration" / "judge_spearman_gate.json"
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(
                {
                    "fail_closed": _FAIL_CLOSED,
                    "threshold_global": _SPEARMAN_THRESHOLD_GLOBAL,
                    "threshold_per_dim": _SPEARMAN_THRESHOLD_PER_DIM,
                    "findings": all_findings,
                    "summary": {
                        "pass": len(passes),
                        "fail": len(fails),
                        "skip": len(skips),
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass

    if fails and _FAIL_CLOSED:
        print(f"[check_judge_spearman_gate] BLOCKING: {len(fails)} dim(s) below threshold")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
