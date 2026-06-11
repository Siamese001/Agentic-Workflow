---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-underwriting-ai-d3-rationale-judge-f2c8d5.md'
original_relative_path: '_archive\\2026-05\\apps-underwriting-ai-d3-rationale-judge-f2c8d5.md'
source_sha256: 17f7c77bca0aa2abd5153e20bba53de354d485c9423e7b862c55c8602850f988
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: apps-underwriting-ai-d3-rationale-judge-f2c8d5

> **Status:** Not Started  
> **Parent plan:** apps-underwriting-ai-deferred-scope-e8b2f4 (Completed)  
> **Notion:** TBD on registration

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.2 | Human holdout dataset authoring | ~8k | 20+ labeled decisions per rubric dim; Spearman baseline ≥ 0.60 | Not Started | holdout YAML at apps_underwriting_ai/holdout/rationale_judge_holdout.yaml; schema valid |
| W2 | P2.1–P2.3 | Real LLM rationale judge implementation | ~15k | W1 holdout available; Anthropic API key in env | Not Started | IS_STUB=False; grade() returns float 0–1; Spearman ≥ 0.80 vs holdout |
| W3 | P3.1 | Calibration CI gate + weekly report | ~6k | W2 passing | Not Started | ops_scripts/ci/check_rationale_judge_calibration.py green; weekly report skeleton |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Holdout dataset schema | apps_underwriting_ai/holdout/__init__.py, holdout_schema.yaml | Schema must cover 5 rubric dims + ground-truth float label | ~3k | Not Started |
| P1.2 | Holdout examples authoring | apps_underwriting_ai/holdout/rationale_judge_holdout.yaml | Requires human judgment; minimum 20 labeled examples per dim | ~5k | Not Started |
| P2.1 | Rationale judge stub → real | apps_underwriting_ai/engines/judges/rationale_quality_judge.py | Currently IS_STUB=True returning GRADER_UNKNOWN_SENTINEL; needs Anthropic client | ~6k | Not Started |
| P2.2 | Spearman calibration test | tests/governance/test_apps_underwriting_ai_rationale_judge.py | Requires holdout YAML to be present; pytest fixture loads it | ~5k | Not Started |
| P2.3 | Rubric integration wire-up | apps_underwriting_ai/engines/rubric_output_mapper.py | Add rationale_quality dim to dim_scores output | ~4k | Not Started |
| P3.1 | Calibration CI gate | ops_scripts/ci/check_rationale_judge_calibration.py | Advisory; fail-closed via env var; skips if API key absent | ~6k | Not Started |

---

## D3 Deferred Scope Detail

### Why deferred

`apps_underwriting_ai/engines/judges/rationale_quality_judge.py` (if it exists) currently
returns `GRADER_UNKNOWN_SENTINEL` — a no-op stub. Flipping it to a real LLM-as-judge
grader requires:

1. A human-labeled holdout dataset (ground-truth scores for ≥20 decision examples per
   rubric dimension) to measure Spearman correlation ≥ 0.80.
2. An Anthropic API key in the environment for the judge's inference calls.
3. A CI gate that validates Spearman is not regressing below 0.80 on the holdout set.

The blocker is **the human holdout dataset** — Cascade cannot author ground-truth labels
for regulated lending decisions. This must come from a human domain expert.

### Acceptance criteria

- `IS_STUB = False` in `rationale_quality_judge.py`.
- `grade(decision_text, rubric_context)` returns a float in [0.0, 1.0].
- Spearman correlation ≥ 0.80 between judge scores and holdout ground-truth labels
  across all 5 rubric dimensions.
- `ops_scripts/ci/check_rationale_judge_calibration.py` runs and emits a pass/warn/fail
  verdict. Advisory by default; `RATIONALE_JUDGE_CALIBRATION_FAIL_CLOSED=1` for strict
  mode.
- Weekly calibration report in `docs/reports/underwriting_judge/`.

### Holdout dataset requirements

- File: `apps_underwriting_ai/holdout/rationale_judge_holdout.yaml`
- Minimum: 20 labeled examples per rubric dimension (100 total).
- Fields per example: `decision_id`, `rationale_text`, `evidence_refs`, `dim_id`,
  `ground_truth_score` (float 0–1), `labeler_id`, `labeled_at`.
- Must NOT contain real applicant data, PII, or live lender thresholds.
- Synthetic examples following the same pattern as the 4 demo fixture packets are
  acceptable.

### Non-goals

- No real applicant data.
- No production credit decisions.
- No changes to agentic_core core routing, Exit v6, or UWG logic.
- No per-decision regulatory citations (out of scope for the stub → real upgrade).

---

## Gap Register

| ID | Gap | Severity | Resolution Wave |
|---|---|---|---|
| GD3 | Rationale quality judge is GRADER_UNKNOWN_SENTINEL stub | MEDIUM | W2 (blocked on W1 holdout) |
| GD3a | No human-labeled holdout dataset for Spearman calibration | HIGH | W1 (human action required) |
| GD3b | No calibration CI gate or weekly report | LOW | W3 |

---

## Source

Captured from `apps-underwriting-ai-deferred-scope-e8b2f4` D3 item.  
Parent plan Notion: `35727693-f55c-817c-b786-ea6ebe24289c` (Completed 2026-05-05).
