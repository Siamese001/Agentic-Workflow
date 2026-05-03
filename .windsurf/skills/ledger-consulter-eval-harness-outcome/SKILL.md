---
name: ledger-consulter-eval-harness-outcome
description: Consult the eval_harness_outcome ledger for precedent before acting. Per-run AppSpecificEvaluator results from the v6 Exit pipeline — bound/passed/score/hitl_policy/disposition per app. Evidence surface for audit BLOCKER #10 feedback loop and the apps_* harness-parity CI gate (plan apps-eval-harness-parity-f8d4a2 W5.P6/P7). Inherits the contract from `ledger-consulter`. Use when debugging why an app-specific eval failed, tuning per-dim thresholds, evaluating a rubric-status flip (draft→active), or reviewing whether a HITL escalation path is firing correctly.
trigger: model_decision
---

# Ledger Consulter — eval_harness_outcome

## Purpose

Per-run AppSpecificEvaluator results from the v6 Exit pipeline — one row per
Exit invocation carries the full ASE snapshot (bound / app_id / task_class /
rubric_ref / threshold_ref / overall_score / hitl_policy / dim counts /
fail_reasons) plus the X2 disposition that consumed it (ALLOW / DENY /
ESCALATE / ABSTAIN / RETRY).

Every row in `artifacts/ledgers/eval_harness_outcome.sqlite` captures the
per-invocation evidence that the v6 Exit pipeline executed the domain rubric
AND that X2 consumed its result. Before changing a rubric threshold, flipping
a contract status, or tuning the HITL policy on a threshold profile, look up
precedent for the affected `(app_id, task_class)` pair.

## When To Invoke

- Before flipping `apps_underwriting_ai` contract status `draft → active`
  (plan W2.P4) — query how many bound runs actually executed and what their
  pass-rate was
- Before adjusting any `threshold_profile.min_required_score` or
  `dimension.min_required_score` (plan W4.P3)
- Before demoting or closing a fail-open LLM-judge dim (plan W4.P2)
- When debugging why a specific app / task_class produced unexpected DENYs
  or ESCALATEs from the Exit pipeline
- During per-app calibration to decide whether a dim is deterministically
  pass/failing (ready for tighter threshold) vs thrashing

## Minimal Query

```python
from tools.ledgers import LedgerConsulter

verdict = LedgerConsulter("eval_harness_outcome").lookup(
    query_text="apps_rg resume_generation pass-rate",
    filters={"event_kind": "app_eval_bound"},
    limit=50,
)
```

## Verdict → Action

| `verdict.strength` | Required behavior |
|---|---|
| `strong`       | Bias current decision toward precedent; cite specific rows in the Author-Gate packet. |
| `suggestive`   | Surface precedent in Author-Gate packet or plan body; note the sample size; do not auto-bias. |
| `none`         | State explicitly: `Precedent: ledger had no match (novel case or insufficient data).` Consider deferring the decision until more runs have accumulated. |

## Key Dimensions To Inspect

- `score_band` distribution over the last N runs — balance across `pass` /
  `deny` / `escalate` / `unknown` / `unbound`
- `prediction_json.fail_reasons` — which dims repeatedly FAIL vs UNKNOWN
- `outcome_json.rationale` — distribution of `app_specific_eval_failed` vs
  `hitl_required_on_low` vs `hitl_required_always`
- `prediction_json.dim_unknown_count` — high values indicate missing
  `output["dim_scores"]` upstream (producer not wired)

## Wave / Sunset

- **Wave**: W5.P7 (plan `apps-eval-harness-parity-f8d4a2`)
- **Writer hook**: `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py`
  (helper `_emit_eval_harness_outcome`; invoked at step 5b in the Exit flow,
  fail-soft so writer errors never crash Exit)
- **Sunset criterion**: all 8 runtime apps green on
  `check_app_domain_harness_parity` AND 4 consecutive weekly rollups show
  zero fail-open LLM-judge dims

## See Also

- Base skill: `.windsurf/skills/ledger-consulter/SKILL.md`
- Writer API: `tools/ledgers/writer.py`
- Schema: `.windsurf/schemas/eval_harness_outcome_ledger.schema.sql`
- Parity gate: `ops_scripts/ci/check_app_domain_harness_parity.py`
- Plan: `.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`
- Intelligence-ledger family: `.windsurf/plans/intelligence-ledgers-ten-a7c3e2.md`
- ADR-050 (ledger-family contract)
