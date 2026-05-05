"""Diagnose Spearman mismatches between judge and human_score."""
import yaml
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.engines.judges.rationale_quality_judge import grade
from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import GRADER_UNKNOWN_SENTINEL

path = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"
data = yaml.safe_load(path.read_text(encoding="utf-8"))

mismatches = []
for ex in data["examples"]:
    ctx = {"output": {"rationale": ex.get("rationale_text", ""), "evidence_refs": ex.get("evidence_refs", [])}}
    score, _ = grade(None, ctx)
    if score is GRADER_UNKNOWN_SENTINEL:
        score = 0.0
    hs = float(ex.get("human_score", 0.0))
    diff = abs(float(score) - hs)
    if diff > 0.25:
        did = ex["decision_id"]
        text_preview = str(ex.get("rationale_text", ""))[:60]
        print(f"{did}: judge={score:.3f} human={hs:.3f} diff={diff:.3f} | {text_preview!r}")
        mismatches.append((did, float(score), hs))

print(f"\nTotal mismatches (diff>0.25): {len(mismatches)}")
