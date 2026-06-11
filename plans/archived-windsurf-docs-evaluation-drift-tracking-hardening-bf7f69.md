---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\evaluation-drift-tracking-hardening-bf7f69.md'
original_relative_path: 'evaluation-drift-tracking-hardening-bf7f69.md'
source_sha256: 2bf4dcc2a1ceae152e47ba20d37c273ee0b119a1f92b677e0bb9bcf97b04cddf
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Evaluation & Drift Tracking Hardening

Locks in a deterministic, interview-grade evaluation and drift tracking system covering retrieval quality, embedding health, LLM output quality, shadow drift, and end-to-end RAGAS-style metrics — all persisted to L4 and observable over time.

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


## Current State (AST Scan Findings)

### Files in scope
| File | Role |
|------|------|
| `agentic_core/evaluation/__init__.py` | `OfflineEvaluationRunner`, `ReplayEvaluationRunner`, `EvaluationReport` |
| `agentic_core/evaluation/runners/offline_eval_runner.py` | Offline batch evaluation |
| `agentic_core/evaluation/runners/replay_eval_runner.py` | Replay against snapshots |
| `agentic_core/evaluation/schemas/evaluation_result_schema.py` | `EvaluationResult`, `EvaluationReport` |
| `agentic_core/evaluation/metrics/base.py` | Base metric interface |
| `agentic_core/evaluation/retrieval/l4_registries.py` | L4D–L4G: chunk manifests, eval registry |
| `agentic_core/evaluation/retrieval/completeness.py` | `ContextCompletenessScore` |
| `agentic_core/evaluation/datasets/` | `rag_eval_set.json`, `hallucination_eval_set.json`, etc. |
| `agentic_core/utils/workflow_engines/drift_monitor.py` | `RetrievalDriftMonitor`, `EmbeddingDriftMonitor` |
| `agentic_core/utils/workflow_engines/snapshots.py` | `DriftAlert`, `RetrievalDriftSnapshot` |
| `agentic_core/L6_observability/engines/drift_detector.py` | C0 context hash drift |
| `system_learning/engines/shadow_drift_analyzer.py` | `ShadowDriftAnalyzer`, `DriftSummary` |
| `system_learning/pipelines/meta_learning_pipeline.py` | W4-A–W4-E pipeline |
| `tests/evaluation/` | Phases 1–6 test files |

### Critical Gaps Found

**Gap 1 — `datetime.utcnow()` in `drift_monitor.py` (non-deterministic)**
`_utcnow()` returns wall-clock ISO string. All `DriftAlert.timestamp` and `RetrievalDriftSnapshot.timestamp` fields are non-deterministic. Tests cannot assert exact timestamps; snapshot-based regression is impossible.

**Gap 2 — Three siloed drift systems with no unified registry**
- `DriftDetector` (L6): C0 context hash comparison.
- `RetrievalDriftMonitor` (utils/workflow_engines): retrieval hit rate, score std.
- `ShadowDriftAnalyzer` (system_learning): cosine similarity from shadow embedder.
No unified `DriftRegistry` that aggregates all three into a queryable timeline.

**Gap 3 — Eval datasets exist but no runner executes them end-to-end**
`evaluation/datasets/*.json` contain `rag_eval_set.json`, `hallucination_eval_set.json`, etc. `OfflineEvaluationRunner` exists but unclear if it processes these files and emits `EvaluationReport` to L4.

**Gap 4 — No RAGAS-style LLM-quality metrics**
Current metrics: `retrieval_hit_rate`, `score_distribution_std`, `top_k_stability`. Missing:
- Faithfulness (answer supported by retrieved context)
- Answer relevancy (answer addresses the question)
- Context precision (fraction of retrieved chunks that are relevant)
- Groundedness score

**Gap 5 — `DriftSummary.drift_flag` threshold (0.92) is a hard-coded magic constant**
Not configurable via `RetrievalProfile` or any L4 config. Cannot be tuned from the meta-learning pipeline.

**Gap 6 — `EmbeddingDriftMonitor` not wired to `ShadowDriftAnalyzer`**
Two separate systems detect embedding drift independently. `ShadowDriftAnalyzer` tracks primary-vs-shadow cosine. `EmbeddingDriftMonitor` tracks norm distribution and version mismatch. Neither feeds the other.

**Gap 7 — No LLM-as-Judge evaluation harness**
No evaluation path that sends `(query, context, answer)` triples to a judge LLM and scores faithfulness/relevancy on a 1–5 scale.

**Gap 8 — `ReplayEvaluationRunner` not verified against historical L4 snapshots**
Unclear if `ReplayEvaluationRunner` actually loads snapshots from L4 or just re-runs queries from scratch.

**Gap 9 — No drift threshold alerting connected to any notification/action surface**
`check_alerts()` returns `list[DriftAlert]` but nothing consumes them. Alerts are computed and discarded.

---

## Phase 1 — Deterministic Timestamps + Unified Drift Registry (Wave 1)

**Scope:** `drift_monitor.py`, new `drift_registry.py`

**Wave 1-A: Inject timestamps — remove `datetime.utcnow()`**
- Replace `_utcnow()` in `drift_monitor.py` with an injected `now_iso: str` parameter on `measure()` and `check_alerts()`.
- Default value: `None` → callers must supply or use `DriftClock.utcnow()` utility (thin wrapper, injectable in tests).
- All `DriftAlert.alert_id` must use `uuid.UUID(int=deterministic_seed)` in tests (inject `id_factory`).

**Wave 1-B: `DriftRegistry` — unified timeline**
Create `agentic_core/L6_observability/engines/drift_registry.py`:
```python
@dataclass
class DriftRegistryEntry:
    source: Literal["retrieval", "embedding", "shadow", "c0_context"]
    timestamp_iso: str
    metric_name: str
    current_value: float
    threshold_value: float
    drift_flag: bool
    severity: Literal["info", "warning", "critical"]
    deterministic_digest: str
```
- `DriftRegistry.record(entry)` appends to an in-memory list and persists to `L4_state/stores/drift_timeline.jsonl` (append-only).
- `DriftRegistry.query(since_iso, source_filter)` returns filtered entries.
- All three drift systems (`DriftDetector`, `RetrievalDriftMonitor`, `ShadowDriftAnalyzer`) emit `DriftRegistryEntry` after each measurement.

**Acceptance criteria:**
- `measure()` called with explicit `now_iso="2024-01-01T00:00:00Z"` → all timestamps in snapshot equal that value.
- `DriftRegistry.record()` + `DriftRegistry.query()` round-trip test.
- `query(source_filter="retrieval")` returns only retrieval entries.

---

## Phase 2 — RAGAS-Style Metrics Implementation (Wave 2)

**Scope:** `agentic_core/evaluation/metrics/`

**Wave 2-A: `FaithfulnessMetric`**
- Input: `(query: str, context_chunks: list[str], answer: str)`.
- Method: For each sentence in `answer`, check if it can be attributed to at least one `context_chunk` using cosine similarity ≥ threshold (0.75).
- Output: `faithfulness_score = (attributable_sentences / total_sentences)` in [0, 1].
- Deterministic: fixed BGE-m3 embeddings; no LLM call required for this tier.

**Wave 2-B: `AnswerRelevancyMetric`**
- Input: `(query: str, answer: str)`.
- Method: Cosine similarity between BGE embedding of `query` and `answer`.
- Output: float in [0, 1].

**Wave 2-C: `ContextPrecisionMetric`**
- Input: `(query: str, retrieved_chunks: list[str], ground_truth_relevant_ids: set[str], chunk_ids: list[str])`.
- Method: `precision = |relevant ∩ retrieved| / |retrieved|`.
- Output: float in [0, 1].

**Wave 2-D: `GroundednessMetric`**
- Input: `(answer: str, context_chunks: list[str])`.
- Method: claim extraction (regex-based sentence splitting) → per-claim cosine similarity check.
- Conservative: if no context → groundedness = 0.0.

**Acceptance criteria:**
- All 4 metrics are deterministic: identical inputs → identical scores.
- `FaithfulnessMetric` test: answer with a sentence verbatim from context → score ≥ 0.9.
- `FaithfulnessMetric` test: answer with hallucinated sentence → score < 0.5.
- Edge cases: empty answer → 0.0; empty context → 0.0.

---

## Phase 3 — Evaluation Runner Wired to Datasets + L4 Persistence (Wave 3)

**Scope:** `offline_eval_runner.py`, `replay_eval_runner.py`

**Wave 3-A: `OfflineEvaluationRunner` — full pipeline**
- Load `evaluation/datasets/rag_eval_set.json` (and others) by convention.
- For each example: retrieve with `SovereignRagOrchestrator`, compute all 4 Phase-2 metrics.
- Aggregate into `EvaluationReport` with mean ± std for each metric.
- Persist `EvaluationReport` to `L4_state/stores/eval_reports/` as JSON (content-hash keyed).
- Emit `DriftRegistryEntry` for each metric that falls below threshold.

**Wave 3-B: `ReplayEvaluationRunner` — snapshot comparison**
- Load a previous `EvaluationReport` from L4 as baseline.
- Re-run the same query set and compare metric values.
- If any metric drops > 5% relative to baseline → emit `DriftAlert` with `severity="warning"`.
- If any metric drops > 15% → `severity="critical"`.

**Acceptance criteria:**
- `OfflineEvaluationRunner.run(dataset_path)` produces `EvaluationReport` with all 4 metrics.
- Report persisted to L4 and reloadable by `ReplayEvaluationRunner`.
- Regression test: second run on identical data → same report (determinism).
- Drift test: inject degraded retrieval results → `ReplayEvaluationRunner` emits `DriftAlert`.

---

## Phase 4 — LLM-as-Judge Harness (Wave 4) — DataArt Interview Focus

**Scope:** New `agentic_core/evaluation/judges/llm_judge.py`

**Wave 4-A: `LLMJudge` protocol + `GeminiJudge` implementation**
```python
class LLMJudge(Protocol):
    def score(self, query: str, context: str, answer: str) -> JudgeScore:
        ...

@dataclass(frozen=True)
class JudgeScore:
    faithfulness: float       # 1–5
    answer_relevancy: float   # 1–5
    context_precision: float  # 1–5
    groundedness: float       # 1–5
    reasoning: str
    judge_model: str
    deterministic_digest: str
```

**Wave 4-B: `GeminiJudge` implementation**
- Structured prompt: role = evaluator, rubric = 1–5 scale with anchors.
- Parse JSON response. If parse fails → retry once with stripped markdown.
- Response hashed for determinism verification (`deterministic_digest`).
- Temperature = 0.0 for Gemini call (maximum determinism).

**Wave 4-C: Judge integration into `OfflineEvaluationRunner`**
- Optional `judge: LLMJudge | None = None` param.
- When provided, include `JudgeScore` in `EvaluationReport` per example.
- Aggregate judge scores alongside metric scores.
- Persist `JudgeScore` objects to L4.

**Wave 4-D: `NullJudge` for testing**
- Deterministic stub: always returns fixed scores (e.g., all 3.0).
- Used in all unit tests to avoid Gemini API calls.

**Acceptance criteria:**
- `GeminiJudge.score(...)` with mocked Gemini → parses JSON → returns `JudgeScore`.
- Determinism test: same `(query, context, answer)` with mocked response → same `deterministic_digest`.
- Aggregation test: `OfflineEvaluationRunner` with `NullJudge` → `EvaluationReport.judge_scores` populated.
- Schema completeness: `JudgeScore` has all 4 required fields + `reasoning` + `judge_model`.

---

## Phase 5 — Shadow Drift → `DriftRegistry` Integration + Alert Routing (Wave 5)

**Scope:** `shadow_drift_analyzer.py`, `drift_monitor.py`, `meta_learning_pipeline.py`, `drift_registry.py`

**Wave 5-A: Externalize drift threshold from `ShadowDriftAnalyzer`**
- Replace hard-coded `0.92` with `drift_threshold: float = 0.92` constructor parameter.
- Source threshold from `RetrievalProfile.drift_threshold` (L4-governed).
- Write to `DriftSummary.drift_threshold` field (add to dataclass).

**Wave 5-B: All three drift systems emit to `DriftRegistry`**
- After `ShadowDriftAnalyzer.analyze_batch()` → `registry.record(DriftRegistryEntry(source="shadow", ...))`.
- After `RetrievalDriftMonitor.measure()` → `registry.record(DriftRegistryEntry(source="retrieval", ...))`.
- After `DriftDetector.register_context_hash()` (if drift detected) → `registry.record(DriftRegistryEntry(source="c0_context", ...))`.

**Wave 5-C: Alert routing — `DriftAlert` → `MetaLearningBus`**
- When `DriftRegistry` receives a `severity="critical"` entry → enqueue `MetaLearningChangePackage` with `kind="drift_critical"` onto `MetaLearningBus`.
- Proposal-only: never auto-mutates routing thresholds.

**Acceptance criteria:**
- `DriftRegistry` populated after each measurement type.
- `query(source_filter="shadow")` returns only shadow entries.
- Critical drift alert → `MetaLearningBus` size increases by 1.
- Threshold externalization test: `ShadowDriftAnalyzer(drift_threshold=0.85)` flags drift at p95_cosine=0.87.

---

## Evaluation Architecture Summary (DataArt Interview Reference)

```
Query → SovereignRagOrchestrator
         ├─ Dense Search (BGE-m3 + InMemoryVectorStore)
         ├─ BM25 Sparse Search (ASTAwareTokenizer + rank_bm25)
         └─ RRF Fusion → top-k chunks

Evaluation Layer:
  OfflineEvaluationRunner
    ├─ FaithfulnessMetric      (BGE cosine attribution)
    ├─ AnswerRelevancyMetric   (query-answer cosine)
    ├─ ContextPrecisionMetric  (retrieved ∩ relevant / retrieved)
    ├─ GroundednessMetric      (claim attribution)
    └─ LLMJudge (GeminiJudge) (1–5 structured rubric)

Drift Tracking Layer:
  RetrievalDriftMonitor → hit_rate, score_std, top_k_stability
  EmbeddingDriftMonitor → norm_std, similarity_mean, version_mismatch
  ShadowDriftAnalyzer   → p95_cosine < threshold → drift_flag
  DriftDetector (L6)    → C0 context hash comparison
                        → All emit to DriftRegistry (L4 timeline)
                        → Critical alerts → MetaLearningBus (advisory)

ReplayEvaluationRunner → compare vs L4 baseline → regression alerts
```

**Evidence file:** `docs/reports/sub/phase_evaluation_drift_tracking_evidence.md`

---

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Non-deterministic `datetime.utcnow()` in snapshots | High | Phase 1: inject `now_iso`; remove wall-clock call |
| Gemini API quota exhaustion in judge harness | Medium | `NullJudge` for CI; `GeminiJudge` only in overnight runs |
| RAGAS metric mismatch vs. ground truth labels | Medium | `rag_eval_set.json` annotated with human labels; precision computable |
| L4 persistence volume growth (append-only JSONL) | Low | Monthly rotation policy; store only last 30-day window |
| Shadow drift threshold not governing: hard-coded 0.92 | High | Phase 5-A: externalize immediately (single-line fix) |
| `DriftAlert.alert_id` non-deterministic (UUID4) | Medium | Inject `id_factory` in tests; production keeps UUID4 |

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

