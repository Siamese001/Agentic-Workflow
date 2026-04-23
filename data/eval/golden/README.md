# Golden Dataset for LLM-as-Judge Calibration (LJH4.1)

Human-labeled evaluation examples used to measure inter-annotator
agreement (Cohen's κ and Krippendorff's α) between LLM judges and
human experts. Required by constitutional rule §22 for every T2/T3
refactor that touches the judge stack.

## Directory Layout

```
data/eval/golden/
├── README.md                          # this file
├── rag/                               # RAG-judge rubrics
│   ├── faithfulness/
│   │   └── *.json
│   ├── answer_relevancy/
│   ├── context_precision/
│   └── groundedness/
├── gov/                               # governance-judge rubrics (GOV-001..003)
└── sec/                               # security-judge rubrics (SEC-001..002)
```

## Example Item Schema

Each item is one JSON file (not JSONL) to keep per-item human annotations
easy to diff and review:

```json
{
  "item_id": "rag-faithfulness-0001",
  "rubric_id": "faithfulness",
  "query": "What year did X happen?",
  "context": "X happened in 1970 according to source A.",
  "answer": "X happened in 1970.",
  "human_labels": [
    {"rater_id": "alice", "score": 5, "notes": "fully supported"},
    {"rater_id": "bob",   "score": 5, "notes": "direct citation"}
  ],
  "gold_score": 5,
  "gold_outcome": "scored",
  "created_at": "2026-04-23T00:00:00Z",
  "license": "CC-BY-4.0 or internal"
}
```

## Acceptance Rules

1. **Minimum 100 items per rubric** before the judge may be considered
   calibrated (LJH4.3 CI gate).
2. **≥2 human raters per item**; Cohen's κ computed between raters
   (inter-rater) must itself be ≥ 0.6, otherwise the rubric prompt is
   ambiguous and must be revised before adding more items.
3. **gold_score** is the consensus; ties break toward the stricter rater.
4. **Unknown items** (insufficient evidence) use ``gold_outcome = "unknown"``
   and ``gold_score = null``. These are kept in the dataset so the judge's
   abstention behavior is measured — not just its numeric accuracy.
5. **No test leakage** — items used in capability/regression suites
   (``tests/eval/``) are NOT added to the golden calibration set.

## Running Calibration

```bash
python tools/eval/judge_calibration.py \
  --gold-dir data/eval/golden/rag/faithfulness \
  --judge-outputs artifacts/eval/judge_runs/latest_faithfulness.jsonl \
  --dimension faithfulness
```

See also: ``agentic_core/evaluation/judges/calibration.py`` for the κ / α
implementations and ``ops_scripts/ci/check_judge_calibration.py`` for
the CI gate.
