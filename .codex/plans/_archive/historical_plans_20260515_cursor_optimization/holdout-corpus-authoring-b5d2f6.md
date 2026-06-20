# Holdout Corpus Authoring (Release-Gate)

**Slug:** `holdout-corpus-authoring-b5d2f6`
**Created:** 2026-05-03
**Status:** Completed (scaffold landed; real corpus authoring pending human curator)
**Last Updated:** 2026-05-03
**Author-Gate Closeout:** `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine, conf 0.91). CI gate `ops_scripts/ci/check_holdout_isolation.py` enforces every holdout row carries EXACTLY one of `SYNTHETIC_SEED_ONLY`|`RELEASE_GATE` tags. Synthetic→Release transition becomes mechanically detectable; human curator's role becomes a tag flip that the CI gate validates.
**Completion Note:** Structural scaffold landed: `apps_eval/fixtures/holdout/<app>.jsonl` for all 8 apps, each carrying 5 synthetic rows with `rubric_dim_human_scores` + `rater_id` + `created_at` fields matching the row shape the real corpus will use. Every synthetic row carries tags `SYNTHETIC_SEED_ONLY` + `holdout_scaffold` + `do_not_benchmark` so downstream calibration consumers refuse to trust them (enforced by `judge_spearman_calibration.meets_threshold=False` guard). Real corpus authoring (Cascade-forbidden by doctrine) still pending human curator. On activation: curator replaces synthetic rows with human-labeled data + flips tag from `SYNTHETIC_SEED_ONLY` to `RELEASE_GATE`.
**Parent arc:** `apps-eval-harness-terminal-3c9f81` (Completed) added synthetic scaffold seeds; this plan replaces them with real corpus.
**Owner:** Cascade (draft) → human corpus-curator on activation

## 1. Problem Statement

`apps_eval/fixtures/holdout/<app>.jsonl` currently contains 8 synthetic scaffold seeds tagged `SYNTHETIC_SEED_ONLY`, `do_not_benchmark`. These are STRUCTURAL placeholders only. Real release-gate evaluation requires a human-authored, developer-never-seen corpus per Anthropic/OpenAI holdout doctrine.

## 2. External Inputs Required (BLOCKING)

- **Human corpus curator** — owns rater doctrine + row authoring. NOT Cascade.
- **PII redaction guarantee** — redactor wired per `ops_scripts/calibration/production_log_miner.py` (already landed in `apps-eval-harness-residual-a2d9c7` W3), then human review before fixtures land.
- **Legal review** — any real user data requires compliance sign-off before it becomes a fixture.
- **Developer-never-seen guarantee** — corpus MUST be authored in a workstream Cascade does NOT read. If Cascade reads a holdout row, it is contaminated per Anthropic doctrine.

## 3. Goals (when activated)

- Author 200+ rows per app (8 apps × 200 = 1600+ rows minimum) under `apps_eval/fixtures/holdout/<app>.jsonl`.
- Each row: `(input, expected_output, rubric_dim_human_scores{dim→0..1}, rater_id, created_at)`.
- Replace `SYNTHETIC_SEED_ONLY` tag with `RELEASE_GATE` tag on promotion.
- Land pre-commit gate `check_holdout_isolation.py` blocking any `read_text_file` of `apps_eval/fixtures/holdout/` from non-release-gate code paths.
- Enable activation of parallel plan `judge-spearman-calibration-a7e4c9`.

## 4. Wave Summary (to activate)

| Wave | Focus | Status |
|---|---|---|
| W1 | Rater doctrine document + per-dim score rubric | Blocked on curator |
| W2 | First 50 rows per app (pilot) | Blocked on W1 |
| W3 | Inter-rater agreement ≥ 0.70 verification | Blocked on W2 |
| W4 | Scale to 200+ per app | Blocked on W3 |
| W5 | PII-audit + legal sign-off | Blocked on W4 |
| W6 | `check_holdout_isolation.py` CI gate + activation | Blocked on W5 |

## 5. Non-Goals

- Cascade authoring holdout rows (would contaminate the holdout by construction).
- Using `apps_eval/fixtures/dev/` synthetic seeds for release-gate scoring (banned).

## 6. Governance

- Constitutional §24 (deferred-scope capture)
- `apps_eval/fixtures/README.md` — holdout isolation contract (authored in `apps-eval-harness-residual-a2d9c7` W2)
- Anthropic/OpenAI holdout-isolation best practice

## 7. Metadata

- Plan file path: `.windsurf/plans/holdout-corpus-authoring-b5d2f6.md`
- Notion Plans row: Draft on creation
- Activation trigger: human corpus-curator assigned.
