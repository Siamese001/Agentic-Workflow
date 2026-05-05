"""DS-R6: Generate rationale_judge_holdout_pairs.json from the YAML holdout.

Converts apps_underwriting_ai/holdout/rationale_judge_holdout.yaml into the
{dim_id, grader_id, n, pairs} JSON format expected by judge_agreement_tracker.py.

Runs the deterministic RationaleQualityJudge against each example to produce
model_score values, paired against human_label (= human_score from the YAML).

Output: apps_underwriting_ai/holdout/rationale_judge_holdout_pairs.json
        (one JSON file per rubric dimension, stored in a list under "fixtures").

Re-run after any holdout YAML update:
    python tools/underwriting/generate_holdout_pairs.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_holdout() -> list[dict]:
    try:
        import yaml
    except ImportError:
        raise SystemExit("pyyaml required: pip install pyyaml")
    path = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"
    if not path.exists():
        raise SystemExit(f"Holdout YAML not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("examples", [])


def _run_judge(examples: list[dict]) -> list[dict]:
    from apps_underwriting_ai.engines.judges.rationale_quality_judge import grade
    from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
        GRADER_UNKNOWN_SENTINEL,
    )

    rows = []
    for ex in examples:
        ctx = {
            "output": {
                "rationale": ex.get("rationale_text", ""),
                "evidence_refs": ex.get("evidence_refs", []),
            }
        }
        score, _ = grade(None, ctx)
        if score is GRADER_UNKNOWN_SENTINEL:
            score = 0.0
        rows.append({
            "decision_id": ex["decision_id"],
            "dim_id": ex["dim_id"],
            "model_score": float(score),
            "human_label": float(ex.get("human_score", ex.get("ground_truth_score", 0.0))),
        })
    return rows


def build_pairs_fixture(rows: list[dict]) -> list[dict]:
    from collections import defaultdict

    by_dim: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_dim[r["dim_id"]].append(r)

    fixtures = []
    for dim_id, dim_rows in sorted(by_dim.items()):
        pairs = [
            {"model_score": r["model_score"], "human_label": r["human_label"]}
            for r in dim_rows
        ]
        fixtures.append({
            "dim_id": dim_id,
            "grader_id": "underwriting::rationale_quality_judge::v2",
            "n": len(pairs),
            "pairs": pairs,
        })

    # Also emit a combined fixture across all dims
    all_pairs = [{"model_score": r["model_score"], "human_label": r["human_label"]} for r in rows]
    fixtures.append({
        "dim_id": "all_dims",
        "grader_id": "underwriting::rationale_quality_judge::v2",
        "n": len(all_pairs),
        "pairs": all_pairs,
    })
    return fixtures


def main() -> int:
    examples = _load_holdout()
    print(f"[generate_holdout_pairs] Loaded {len(examples)} examples from holdout YAML")

    rows = _run_judge(examples)
    fixtures = build_pairs_fixture(rows)

    out_path = (
        REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout_pairs.json"
    )
    out_path.write_text(json.dumps(fixtures, indent=2), encoding="utf-8")
    print(f"[generate_holdout_pairs] Written {len(fixtures)} fixture entries to {out_path}")

    # Print Spearman summary
    all_fixture = next((f for f in fixtures if f["dim_id"] == "all_dims"), None)
    if all_fixture:
        pairs = all_fixture["pairs"]
        model_scores = [p["model_score"] for p in pairs]
        human_labels = [p["human_label"] for p in pairs]
        rho = _manual_spearman(model_scores, human_labels)
        threshold_ok = "OK" if rho >= 0.80 else "BELOW THRESHOLD"
        print(f"[generate_holdout_pairs] Global Spearman rho={rho:.4f} (threshold=0.80) [{threshold_ok}]")
    return 0


def _manual_spearman(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0

    def ranks(seq: list[float]) -> list[float]:
        sorted_idx = sorted(range(n), key=lambda i: seq[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and seq[sorted_idx[j + 1]] == seq[sorted_idx[j]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[sorted_idx[k]] = avg
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


if __name__ == "__main__":
    sys.exit(main())
