# ML Evaluation Framework: Precision, Recall & F1 Architecture

Embed a unified ML evaluation framework across `agentic_core/evaluation` and `apps_eval` by adding a classification metric hierarchy (binary + multi-class precision/recall/F1) and wiring it into the existing `OfflineEvaluationRunner`, `apps_eval` benchmark suites, and regression detection.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## ADG Gap Analysis

### What Exists (ADG-confirmed)

| Layer | Module | What it covers |
|---|---|---|
| `L_SHARED` | `agentic_core/evaluation/metrics/base.py` | `EvaluationMetric`, `RetrievalMetric`, `GenerationMetric` ABCs |
| `L_SHARED` | `agentic_core/utils/workflow_engines/precision_at_k.py` | Retrieval `PrecisionAtK` (rank-based) |
| `L_SHARED` | `agentic_core/utils/workflow_engines/recall_at_k.py` | Retrieval `RecallAtK` (rank-based) |
| `L_SHARED` | `agentic_core/utils/workflow_engines/groundedness.py` | `_token_f1` helper (private, generation-only) |
| `L_SHARED` | `agentic_core/utils/workflow_engines/answer_correctness.py` | Token-overlap F1 (generation heuristic) |
| `L_SHARED` | `agentic_core/evaluation/metrics/ragas_metrics.py` | RAGAS: faithfulness, answer_relevancy, context_precision, groundedness |
| `L_SHARED` | `agentic_core/utils/workflow_engines/offline_eval_runner.py` | `OfflineEvaluationRunner` pipeline |
| `L_APP` | `apps_eval/` | Benchmark harness — **0 ML metric suites currently** |

### Confirmed Gaps

1. **No `ClassificationMetric` base** — no abstraction for TP/FP/TN/FN inputs
2. **No binary `Precision`, `Recall`, `F1Score` metrics** — the `_token_f1` in `groundedness.py` is a private token-overlap helper, not a general classification metric
3. **No multi-class precision/recall/F1** with macro/micro/weighted averaging
4. **No `ConfusionMatrix` dataclass** for structured classification results
5. **`agentic_core/evaluation/metrics/__init__.py`** does not export any classification metrics
6. **`apps_eval` has zero benchmark suites** testing classification metric quality
7. **No golden classification dataset** (`agentic_core/evaluation/datasets/` has RAG-only datasets)
8. **`EvaluationReport` schema** (`completeness_metrics.py`) does not include classification F1/precision/recall fields

---

## Architecture: New Components

### Layer 1 — `agentic_core/evaluation/metrics/` (L_SHARED)

```
agentic_core/evaluation/metrics/
├── base.py                 # EXISTING — add ClassificationMetric ABC
├── classification.py       # NEW — BinaryClassificationMetric, MultiClassF1Metric
├── f1_score.py             # NEW — F1Score (binary), thin wrapper, public API
└── __init__.py             # UPDATE — export new symbols
```

**`base.py`** — add `ClassificationMetric(EvaluationMetric)` ABC:
- `compute(prediction: list, ground_truth: list, context=None) -> float`
- `confusion(prediction: list, ground_truth: list) -> ConfusionMatrix`

**`classification.py`** — new file:
- `ConfusionMatrix` frozen dataclass: `tp, fp, tn, fn`; `.precision()`, `.recall()`, `.f1()`, `.accuracy()`
- `BinaryClassificationMetric(ClassificationMetric)`: binary labels, computes TP/FP/TN/FN
- `MultiClassF1Metric(ClassificationMetric)`: per-class F1 + macro/micro/weighted aggregate; `averaging: Literal["macro","micro","weighted"]`

**`f1_score.py`** — thin public wrapper:
- `F1Score(BinaryClassificationMetric)` with `name = "f1_score"`

### Layer 2 — `apps_eval/` (L_APP): New Benchmark Suite

Add `ml_metrics_validation` suite to `apps_eval`:
```
apps_eval/
├── engines/
│   └── scenario_runner.py    # UPDATE — add ml_metrics_validation suite scenarios
├── config/
│   └── agent_spec_config.py  # UPDATE — add suite config + scorecard dimension
```

**New scenarios** (deterministic, no LLM calls):
| Scenario ID | What it tests |
|---|---|
| `binary_precision_perfect` | P=1.0 when all positives correct |
| `binary_recall_perfect` | R=1.0 when all positives retrieved |
| `binary_f1_harmonic_mean` | F1 = 2PR/(P+R) invariant holds |
| `multiclass_macro_f1` | Macro-average = per-class mean |
| `multiclass_weighted_f1` | Weighted F1 proportional to class support |
| `confusion_matrix_invariants` | TP+FP+TN+FN == total samples |

**New scorecard dimension**: `ml_metric_correctness` (weight 2.0)

### Layer 3 — Golden Dataset

```
agentic_core/evaluation/datasets/
└── classification_eval_set.json   # NEW
```

Schema:
```json
{
  "name": "classification_eval_set",
  "version": "1.0.0",
  "description": "...",
  "examples": [
    {
      "query": "routing_decision_binary",
      "predictions": ["pos","pos","neg","neg"],
      "ground_truth": ["pos","pos","pos","neg"],
      "expected_precision": 1.0,
      "expected_recall": 0.6667,
      "expected_f1": 0.8
    }
  ]
}
```

### Layer 4 — `__init__.py` + `EvaluationReport` extension

- **`agentic_core/evaluation/metrics/__init__.py`**: export `ClassificationMetric`, `ConfusionMatrix`, `BinaryClassificationMetric`, `MultiClassF1Metric`, `F1Score`
- **`agentic_core/utils/workflow_engines/completeness_metrics.py`**: add `f1_score`, `precision`, `recall` fields to `EvaluationReport`

---

## Implementation Phases

### Phase 1 — Core Metric Classes
1. Add `ClassificationMetric` ABC to `agentic_core/evaluation/metrics/base.py`
2. Create `agentic_core/evaluation/metrics/classification.py` — `ConfusionMatrix`, `BinaryClassificationMetric`, `MultiClassF1Metric`
3. Create `agentic_core/evaluation/metrics/f1_score.py` — `F1Score` wrapper
4. Update `agentic_core/evaluation/metrics/__init__.py` exports

### Phase 2 — Golden Dataset
5. Create `agentic_core/evaluation/datasets/classification_eval_set.json`

### Phase 3 — apps_eval Integration
6. Add `ml_metrics_validation` suite scenarios to `apps_eval/engines/scenario_runner.py`
7. Register suite in `apps_eval/config/agent_spec_config.py` with `ml_metric_correctness` dimension

### Phase 4 — Schema Extension
8. Add `f1_score`, `precision`, `recall` to `EvaluationReport` in `completeness_metrics.py`
9. Update `EvaluationDeltaReport` with corresponding delta fields

### Phase 5 — Tests
10. `tests/unit/agentic_core/evaluation/metrics/test_classification_metrics_adg.py`
    - `ConfusionMatrix` invariants
    - `BinaryClassificationMetric` edge cases (all-positive, all-negative, empty)
    - `MultiClassF1Metric` macro/micro/weighted correctness
    - `F1Score` harmonic mean contract
11. `tests/apps_eval/test_ml_metrics_suite_adg.py` — scenario runner integration

---

## Design Constraints

- **Zero external dependencies** — all deterministic, pure Python (no sklearn)
- **Layer law**: classification metrics live in `L_SHARED` (`agentic_core/evaluation/metrics/`); they do NOT import from L0–L5
- **`_token_f1` stays private** in `groundedness.py` — the new `F1Score` is a separate classification-domain class, not a refactor of the existing helper
- **Averaging modes**: `macro` (unweighted mean), `micro` (aggregate TP/FP/FN), `weighted` (support-weighted mean)
- All new classes follow existing frozen-dataclass + `to_dict()`/`from_dict()` convention

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

