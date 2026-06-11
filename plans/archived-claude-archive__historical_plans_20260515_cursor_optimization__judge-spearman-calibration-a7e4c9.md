---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\judge-spearman-calibration-a7e4c9.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\judge-spearman-calibration-a7e4c9.md'
source_sha256: cfcc3472807ed67ee84e2b17baf6943bb452bf4095106aedc35b1c4d73bcfeb4
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Judge Spearman ≥ 0.80 Calibration

**Slug:** `judge-spearman-calibration-a7e4c9`
**Created:** 2026-05-03
**Status:** Completed (scaffold landed; activation pending real corpus)
**Last Updated:** 2026-05-03
**Author-Gate Closeout:** `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine, conf 0.91). CI gate `ops_scripts/ci/check_calibration_evidence_authenticity.py` blocks any commit where `artifacts/calibration/judge_spearman.json` claims `meets_threshold=true` while any result has `is_synthetic_smoke=true`. Synthetic smoke runs can never falsely claim production readiness.
**Completion Note:** Calibration scaffold landed at `ops_scripts/calibration/judge_spearman_calibration.py`. Consumes `apps_eval/fixtures/holdout/<app>.jsonl` rows with `rubric_dim_human_scores`, runs scipy.stats.spearmanr per judge, emits `artifacts/calibration/judge_spearman.json`. HARD GUARD: when any row carries the `SYNTHETIC_SEED_ONLY` tag, `meets_threshold` is forced to `False` regardless of computed ρ — prevents synthetic smoke from falsely claiming production readiness. Current synthetic smoke run: 4/4 judges import cleanly, n=5 per judge, ρ meaningless (synthetic_smoke=true). Real calibration activates when `holdout-corpus-authoring-b5d2f6` lands human-labeled corpus.
**Parent arc:** `apps-eval-harness-{parity-f8d4a2,deferred-e4a1b7,residual-a2d9c7,final-8f3e21,terminal-3c9f81}` (all Completed)
**Owner:** Cascade (draft) → human owner on activation

## 1. Problem Statement

All 4 judges (`executive_positioning`, `response_likelihood`, `brand_voice`, `win_theme_alignment`) are promoted to v2 deterministic heuristics. Per `author-gate-svp-calibration.md`, production readiness requires Spearman rank correlation ≥ 0.80 between judge score and human-labeled holdout. This plan lands the calibration infrastructure when the holdout corpus exists.

## 2. External Inputs Required (BLOCKING)

This plan CANNOT start until ALL of the following are provided:

- **Human-labeled holdout corpus** — minimum 100 rows per judge, each row: `(input, output_text, human_score_0_1, human_rater_id)`. Two-rater agreement ≥ 0.70 required.
- **LLM-call budget** — for `llm_as_judge` variants; approximate $50-200 per judge at Opus pricing for calibration sweep.
- **Rater doctrine** — rubric defining what each 0.0 / 0.25 / 0.5 / 0.75 / 1.0 score means per dim.

## 3. Goals (when activated)

- Compute Spearman ρ between v2 deterministic scores and human holdout; publish per-judge correlation report.
- If ρ < 0.80 for a judge, prototype an LLM-judge v3 variant and re-measure.
- Gate promotion of any v3 variant via Author-Gate with calibration evidence.
- Emit `judge_agreement` rows into the `eval_harness_outcome` ledger.

## 4. Wave Summary (to activate)

| Wave | Focus | Status |
|---|---|---|
| W1 | Holdout ingest + label schema validator | Blocked on external input |
| W2 | Spearman computation per judge (scipy.stats.spearmanr) | Blocked on W1 |
| W3 | LLM-judge v3 prototypes for judges below 0.80 | Blocked on W2 + LLM budget |
| W4 | Author-Gate calibration evidence bundle per v3 promotion | Blocked on W3 |
| W5 | Verification — tests + parity gate + ledger rows | Blocked on W4 |

## 5. Non-Goals

- Changing v2 deterministic judges' scoring logic (unless ρ < 0.50, in which case a separate RCA plan is needed).
- Calibration against synthetic fixtures (`SYNTHETIC_SEED_ONLY` rows are explicitly banned from calibration).

## 6. Governance

- `author-gate-svp-calibration.md` — Red/Yellow/Green bands on judge calibration
- `judge-calibration-cadence.md` — recalibration schedule
- Constitutional §24 (deferred-scope capture — this IS the pickup)
- Constitutional §25 (MCP serialization)

## 7. Metadata

- Plan file path: `.windsurf/plans/judge-spearman-calibration-a7e4c9.md`
- Notion Plans row: Draft on creation
- Activation trigger: human operator supplies holdout corpus under `apps_eval/fixtures/holdout/` with real (non-synthetic) labels.
