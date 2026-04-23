# Judge Calibration Gold Set

Scaffolded by plan `llm-as-judge-hardening-anthropic-e7b1a4` (ENH5.5).

This directory holds the human-annotated gold set used to calibrate
LLM-as-Judge backends against expert judgement. Metrics produced:
Cohen's kappa (two raters) and Krippendorff's alpha (N raters) — both
implemented in `agentic_core/evaluation/judges/calibration.py`.

## File layout

| File | Purpose |
|---|---|
| `gold_set.jsonl` | Canonical human-labelled items. Each line is one item record. |
| `judge_runs/<judge_id>-<timestamp>.jsonl` | One jsonl per judge run over the gold set. Filename is `<judge_id>-<UTC ISO timestamp>.jsonl`. |
| `reports/<UTC-date>.json` | Calibration reports emitted by `summarize_judge_vs_human`. |

## Item record schema (jsonl)

Each line is a single JSON object:

```json
{
  "item_id": "stable-unique-id",
  "query": "<user query>",
  "context": "<retrieved context>",
  "answer": "<candidate answer>",
  "faithfulness": 5,
  "answer_relevancy": 4,
  "context_precision": 5,
  "groundedness": "Unknown",
  "annotator": "expert-01",
  "annotation_date": "2026-04-23T00:00:00Z",
  "notes": "optional free text"
}
```

- Integer scores must be in the closed interval `[1, 5]`.
- The string `"Unknown"` (case-insensitive) or `null` marks abstention.
- A minimum of **2 annotators** per item is required before any kappa
  / alpha metric is considered meaningful. Inter-annotator agreement
  < 0.6 is a signal that the rubric itself needs sharpening.

## Populating the gold set

Seeded from three sources:

1. **HITL packets.** Resolved `ask_user_question` decisions from the
   runtime-HITL ledger (ADR-023) that touched factual-correctness
   questions.
2. **Expert sampling.** Randomly sample N=50 items from production
   traces and route to SMEs for labelling.
3. **Adversarial cases.** Hand-picked edge cases that probe known
   failure modes (partial context, contradictory context, ambiguous
   query).

## Minimum viable gold set

- ≥50 items total for the first calibration cycle.
- ≥2 annotators per item.
- All four pointwise dimensions covered on every item.
- At least 10 items with `"Unknown"` as a valid label on some
  dimension (tests whether judges correctly abstain).

## Running a calibration report

```python
from agentic_core.evaluation.judges.calibration import summarize_judge_vs_human

report = summarize_judge_vs_human(
    gold_path="data/judge_calibration/gold_set.jsonl",
    judge_path="data/judge_calibration/judge_runs/gemini-2026-04-23T00.jsonl",
)
print(report.to_dict())
```

Acceptance thresholds for the hardening plan:

| Metric | Minimum |
|---|---|
| Cohen's κ (judge vs human) | ≥ 0.60 per dimension |
| Krippendorff's α | ≥ 0.60 per dimension |
| Judge `unknown_rate` per dim | ≤ dimension's `unknown_budget` in `config/judges/rubrics.yaml` |

Failures on any of the above are recorded by the drift monitor at
`agentic_core/L6_observability/judge_drift.py`.
