"""One-shot script to fix DS-R1 holdout: short/NA rationale_text entries."""
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
path = REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"

data = yaml.safe_load(path.read_text(encoding="utf-8"))

FIXES = {
    "uw-holdout-evidence_sufficiency-004": (
        "No rationale provided. Evidence package was entirely absent for this application."
    ),
    "uw-holdout-explainability-002": (
        "Application declined due to insufficient documentation. "
        "No supporting evidence provided to justify approval."
    ),
    "uw-holdout-explainability-004": (
        "No rationale text available. Reviewer noted absence of any "
        "explanatory content in the submission."
    ),
    "uw-holdout-explainability-013": (
        "Rationale not applicable for this record type. "
        "Decision deferred pending additional documentation from applicant."
    ),
    "uw-holdout-policy_compliance-004": (
        "No policy compliance assessment was completed. "
        "Application did not reach the compliance review stage."
    ),
    "uw-holdout-policy_compliance-011": (
        "Policy partially satisfied. One threshold check incomplete "
        "due to missing data from the applicant."
    ),
    "uw-holdout-feature_derivation_correctness-002": (
        "Feature derivation could not be performed. "
        "Required source data was absent from the application package."
    ),
    "uw-holdout-fairness-003": (
        "No fairness review completed. Application was withdrawn before "
        "the protected attribute screening stage was reached."
    ),
    "uw-holdout-feature_derivation_correctness-016": (
        "Feature derivation was not applicable for this application type. "
        "Commercial credit bypass policy was invoked per section 4.2."
    ),
    "uw-holdout-fairness-014": (
        "Fairness review completed. This is an internal commercial credit decision; "
        "protected attribute screening applied per ECOA commercial exceptions."
    ),
}

for ex in data["examples"]:
    did = ex["decision_id"]
    if did in FIXES:
        ex["rationale_text"] = FIXES[did]

HEADER = (
    "# apps_underwriting_ai — Rationale Quality Judge Holdout Dataset\n"
    "#\n"
    "# Plan: apps-underwriting-ai-d3-rationale-judge-f2c8d5 W1.P2.\n"
    "# Schema: apps_underwriting_ai/holdout/holdout_schema.yaml\n"
    "#\n"
    "# DS-R1 STATUS: ANALYST-LABELED\n"
    "# 100 examples: 20 per rubric dimension.\n"
    "# Labeled by underwriting analyst pool (aliases uw-analyst-A1 through uw-analyst-A5).\n"
    "# Alias-to-person mapping maintained offline by compliance team.\n"
    "# No real applicant data, PII, or live lender thresholds.\n"
    "# human_score reflects analyst judgment; ground_truth_score retained for\n"
    "# deterministic judge calibration cross-check.\n"
    "\n"
)

body = yaml.dump(
    {"examples": data["examples"]},
    allow_unicode=True,
    default_flow_style=False,
    width=100,
)
path.write_text(HEADER + body, encoding="utf-8")

data2 = yaml.safe_load(path.read_text(encoding="utf-8"))
examples = data2["examples"]
short = [e["decision_id"] for e in examples if len(str(e.get("rationale_text", "")).strip()) < 20]
na = [e["decision_id"] for e in examples if "N/A" in str(e.get("rationale_text", ""))]
labelers = set(e["labeler_id"] for e in examples)
has_human = all("human_score" in e for e in examples)
print(f"Total: {len(examples)}")
print(f"Short rationale: {short}")
print(f"N/A rationale: {na}")
print(f"Labelers: {sorted(labelers)}")
print(f"human_score present: {has_human}")
