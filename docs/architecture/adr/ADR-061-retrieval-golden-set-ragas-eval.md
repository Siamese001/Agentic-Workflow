# ADR-061 — Retrieval Golden Set + RAGAS Evaluation Harness

**Status**: Accepted (implemented; scheduled harness available)
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `tools/eval/`, `data/eval/golden/`, `config/retrieval/calibration_manifest.yaml` (new), `agentic_core/L6_observability/utils/evaluation/`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W5.1
**Relates-to**: ADR-045 (acceptance gate referenced), ADR-046, ADR-055, ADR-056, ADR-057, ADR-058, ADR-060

**Current-state note (2026-06-15):** `tools/eval/retrieval_ragas.py` and `tools/eval/cron_retrieval_eval.py` provide deterministic metrics, JSON artifact output, JSONL history append, and advisory gate checks. Rows without retrieved results are counted as unscored inputs so curation gaps are visible rather than converted into synthetic passes.

---

## Context

Five W1–W3 ADRs (045 amend, 055, 056, 057, 058) and one W4 ADR (060) all declare an acceptance gate against a "golden set" or "calibration corpus" — but **no canonical golden set exists yet** in the repo. `tools/eval/retrieval_benchmark.py`, `retrieval_abcd_harness.py`, and `retrieval_eval_curated.py` are present and exercise retrieval with various toggles, but they:

- Read inputs from disparate, non-versioned locations (`tools/eval/_build_smoke_manifest.py` builds an ad-hoc smoke manifest at runtime).
- Do not enforce ground-truth coverage across corpora (code, docs, tests, traces, incidents).
- Do not compute industry-standard RAGAS metrics (context_precision, context_recall, faithfulness, answer_relevancy).
- Are not on a schedule. Regressions surface only when an operator runs them by hand.

Without a frozen golden set + scheduled gate, every other ADR's acceptance criterion is unenforceable — the metrics they promise can be claimed but not audited. This ADR closes that.

## Decision

Adopt a **frozen, versioned, multi-corpus retrieval golden set** plus a **RAGAS-augmented eval harness** that runs nightly and writes outcomes to Notion Wave/Phase Convergence on regression.

### Normative Requirements

1. **Golden-set location + schema** — `data/eval/golden/retrieval/` containing one JSONL file per corpus:
   - `code.jsonl` (≥ 80 query-answer pairs over the canonical code corpus)
   - `docs.jsonl` (≥ 60 pairs over docs/, AGENTS.md, .windsurf/rules/)
   - `tests.jsonl` (≥ 30 pairs)
   - `traces.jsonl` (≥ 20 pairs)
   - `incidents_rca.jsonl` (≥ 20 pairs)

   Per-row schema:
   ```json
   {
     "query_id": "code-001",
     "query": "How does the reranker factory pick the backend?",
     "intent_class": "code_concept",  // for routing rubric (W3.2)
     "expected_chunks": ["agentic_core/knowledge/retrieval/reranker_factory.py:52-67"],
     "expected_answer_summary": "RERANKER env: auto/heuristic/cross_encoder/none.",
     "negative_chunks": ["...intentionally-irrelevant chunk paths..."],
     "tags": ["retrieval", "factory", "env_driven"],
     "added_at": "2026-04-24",
     "curator": "<initials>"
   }
   ```

   Total ≥ **210 pairs** at v1; quarterly re-curation cadence.

2. **Calibration manifest** — `config/retrieval/calibration_manifest.yaml` (new) declares which corpus snapshots, embedder identity (per ADR-055), reranker mode, and query-transform mode each run executes. Pinned by manifest hash so reruns are reproducible.

3. **RAGAS metrics** — `tools/eval/retrieval_ragas.py` (new) computes:
   - `context_precision`   (signal-to-noise of retrieved set)
   - `context_recall`      (does ground-truth chunk appear in top-K)
   - `faithfulness`        (downstream answer derived only from retrieved context)
   - `answer_relevancy`    (downstream answer addresses the query)
   - In-repo metrics: `recall@k` for k ∈ {5, 10, 20}; `mrr@10`; `ndcg@10`.
   Faithfulness/answer_relevancy require an answer-generation step; gated behind `RAGAS_FULL=1` since it costs LLM tokens.

4. **Per-axis sweep** — the harness extends `tools/eval/retrieval_abcd_harness.py` to sweep:
   - `RERANKER ∈ {none, heuristic, cross_encoder, cross_encoder_late}`  (ADR-046, ADR-056)
   - `QUERY_TRANSFORM ∈ {identity, multi_query, hyde, step_back, decomposition, self_query}`  (ADR-058)
   - `RETRIEVAL_REFLECTIVE ∈ {0, 1}`  (ADR-060)
   - `dim_tier ∈ {hot-interactive, warm-analytics, cold-batch, tiny-prefilter}`  (ADR-057)

   Full sweep is large (4 × 6 × 2 × 4 = 192 cells). Default nightly: a **diagonal slice** (one cell per axis-default plus the ADR-recommended cell). Full sweep weekly.

5. **Acceptance gates** (per ADR, in priority order):
   - ADR-045: Recall@20 with `--contextualize` ≥ heuristic-baseline + 20 % on `docs.jsonl` and `code.jsonl`.
   - ADR-055: zero `EmbeddingProvenanceMismatchError` events in nightly run.
   - ADR-056: Recall@20 (`cross_encoder_late`) ≥ Recall@20 (`cross_encoder`) + 5 %.
   - ADR-057: Recall@20 floors per `hot/warm/cold/tiny` tier (1.00 / 0.97 / 0.93 / 0.85).
   - ADR-058: per-transform recall lift floors (HyDE +5 %, step_back +4 %, decomposition +10 % on compound subset, self_query precision +8 % no recall regression > 2 %).
   - ADR-060: Recall@20 (`reflective=on`) ≥ baseline + 3 %; abstain-precision ≥ 0.85.

6. **Schedule** — pytest scheduler under `tools/eval/cron_retrieval_eval.py`:
   - Nightly diagonal slice (≈ 5 minutes wall-clock on local Qwen GPU box).
   - Weekly full sweep (≈ 1 hour).
   - On-demand via `python tools/eval/cron_retrieval_eval.py --slice|--full`.

7. **Reporting** — every run writes:
   - JSON: `artifacts/eval/retrieval/<run_id>.json`
   - JSONL append: `artifacts/eval/retrieval/history.jsonl`
   - Notion: on regression vs. last green run, post a row to Wave/Phase Convergence with prefix `[EVAL-REGRESSION]` and a summary of which gates failed.
   - OTel: spans per cell with `gen_ai.eval.metric.*` attributes.

8. **Reproducibility** — calibration manifest hash + golden-set hash + corpus snapshot id (ADR-055 dim-locked collection metadata) form the run's `replay_id`. Two runs with identical `replay_id` MUST produce identical metric values modulo the LLM-faithfulness step.

### Non-Goals

- Authoring an end-to-end answer-quality benchmark (HumanEval-style). Out of scope; this is retrieval-only.
- Replacing the existing `evaluation_record.py` / `evaluation_signal_integrator.py` infrastructure. They handle agent-loop evaluation; this ADR augments them with a retrieval axis.
- Building a bespoke RAGAS port. Use the upstream `ragas` package when present; pure-numpy fallback for the 3 numeric metrics when not.

## Consequences

**Positive**
- Every other ADR in the parent plan gains a real, audited acceptance gate.
- Operator gets a single Notion row per regression; no manual harness running.
- Reproducible: `replay_id` traces every claimed metric to its inputs.

**Negative / costs**
- Curation labor: one engineer-day for the initial 210 pairs; ~½ day quarterly to refresh.
- Nightly run consumes ~5 min GPU time on the local box. Weekly full ~1 hr. Bounded.
- RAGAS faithfulness step costs LLM tokens (gated behind `RAGAS_FULL=1`; nightly defaults off).

**Risks**
- **R1 — golden set drifts away from corpus.** Mitigation: quarterly refresh; W5.3 drift detector flags decreasing answer-presence rate.
- **R2 — flaky LLM-graded metrics on nightly.** Mitigation: `RAGAS_FULL` off by default; faithfulness only on weekly.
- **R3 — nightly noise triggers false alerts.** Mitigation: 3-run rolling median for regression detection; alert only on consistent regression.

## Validation

- `pytest tests/unit/tools/eval/test_retrieval_ragas.py` — RAGAS metric implementations match published examples within ε.
- `pytest tests/integration/test_cron_retrieval_eval.py` — diagonal slice runs end-to-end on a 10-pair fixture.
- One green nightly run + one demonstrated regression-detection (synthetic).

Rollback: disable the cron entry; harness modules stay in place. Acceptance gates degrade to manual.

## Alternatives Considered

1. **Keep ad-hoc smoke manifest.** Today's posture; every ADR's acceptance gate stays unenforceable. Rejected.
2. **Use TruLens or Arize Phoenix.** External dependencies, telemetry endpoints, and license review. Defer; revisit if RAGAS proves insufficient.
3. **Golden set in Notion.** Pretty but brittle; CI cannot read Notion deterministically. Rejected.
4. **Auto-generate golden set from production queries.** No ground-truth answer; would need post-hoc human labeling — the same labor at the wrong tier.

## References

- Es et al., *RAGAS: Automated Evaluation of Retrieval Augmented Generation* (2023)
- In-repo: `tools/eval/retrieval_benchmark.py`, `retrieval_abcd_harness.py`, `retrieval_eval_curated.py`
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
