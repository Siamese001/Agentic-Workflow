# apps_lic Outreach Holdout Corpus

**Purpose**: Frozen human-labeled golden eval corpus for calibrating and auditing apps_lic outreach judges.

**Status**: Synthetic seed corpus awaiting human labels.

## What This Is

This directory contains a holdout corpus of 80 synthetic outreach messages across a balanced spectrum of quality, channels, recipient classes, and evidence postures. Human labelers score each message on subjective quality dimensions and flag objective guardrail violations.

The adjudicated human labels serve as ground truth for:
- Spearman correlation calibration of LLM judges
- Guardrail false-pass/false-fail auditing
- Judge promotion/demotion decisions via L6 closed-loop router

## What This Is NOT

- **Not a runtime authority**: These labels are L6/eval calibration evidence, not current-run authority.
- **Not training data**: Do not train models on this corpus.
- **Not a live evaluation path**: Judges must still pass current-run evaluation.
- **Not immune to governance**: Any future judge/rubric/prompt/threshold changes must remain inert until promoted through the governed future-run path (UWG → L4 → spine contract update).

## Directory Contents

| File | Purpose |
|------|---------|
| `outreach_holdout_corpus.v1.jsonl` | 80 synthetic outreach messages with metadata |
| `human_label_schema.outreach_quality.v1.json` | JSON schema for label CSV validation |
| `human_labeling_guidelines.md` | Scoring anchors and labeling instructions |
| `human_labels.outreach_quality.v1.csv` | Raw human labels (1+ per holdout item) |
| `adjudicated_scores.outreach_quality.v1.csv` | Median-normalized ground truth scores |
| `calibration_report.outreach_quality.v1.json` | Judge performance vs. human ground truth |

## Workflow

### 1. Human Labeling (L6 Authority)

Labelers follow `human_labeling_guidelines.md` and record judgments in `human_labels.outreach_quality.v1.csv`.

Requirements:
- At least 2 independent labelers per holdout item
- Labeler identity hashed (privacy)
- Batch tracking for provenance

### 2. Validation

```bash
python apps_lic/evals/scripts/validate_holdout_corpus.py
python apps_lic/evals/scripts/validate_human_labels.py
```

### 3. Adjudication

```bash
python apps_lic/evals/scripts/adjudicate_human_labels.py
```

Resolves labeler disagreement via median scoring. Flags items requiring expert review.

### 4. Judge Calibration

```bash
python apps_lic/evals/scripts/score_judges_against_holdout.py
```

Produces Spearman correlations and MAE per dimension. Judges must achieve Spearman ≥ 0.80 for promotion consideration.

## Synthetic Corpus Balance

| Category | Count |
|----------|-------|
| **Quality tiers** | 20 excellent, 20 decent, 20 flawed, 20 hard negatives |
| **Channel** | 40 email, 40 linkedin_inmail |
| **Recipient class** | 20 recruiter, 20 hiring_manager, 20 executive, 20 referral |
| **Outreach mode** | 20 cold, 20 warm, 20 referral, 20 follow_up |
| **Evidence posture** | 20 fully_grounded, 20 partially_grounded, 20 ungrounded, 20 fake_personalization_trap |

## Schema Version

- Corpus: `outreach_holdout_corpus.v1`
- Label schema: `human_label_schema.outreach_quality.v1`
- Frozen: `true` (corpus is immutable once labeled)

## Contact

For adjudication disputes or schema questions, contact the apps_lic eval harness maintainer.
