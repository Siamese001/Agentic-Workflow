# ADR-060 — Corrective-RAG / Self-RAG Reflective Retrieval Loop

**Status**: Proposed
**Date**: 2026-04-24
**Deciders**: Agentic-Workflow maintainers
**Impact Layers**: `agentic_core/L1_cognition/reasoning/`, `agentic_core/L3_orchestration/reasoning/engines/reflexion_engine.py`, `agentic_core/knowledge/retrieval/`, `agentic_core/knowledge/engine/rag_orchestrator.py`
**Plan**: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md` W4.1
**Relates-to**: ADR-045 (contextual retrieval), ADR-046 (rerank), ADR-056 (multi-head), ADR-058 (query transforms), ADR-023 (runtime HITL — distinct from this dev-loop pattern)

---

## Context

Today every retrieval call in the repo is **single-pass**: one query in, one ranked top-K out, one prompt assembled. There is no mechanism that:

- Grades whether the retrieved chunks actually answer the query.
- Reformulates and re-retrieves when the first pass is insufficient.
- Falls back to alternate evidence sources (knowledge graph hop, web, ADG SQLite) when the corpus does not contain the answer.

This is the published gap closed by **CRAG** (Corrective Retrieval-Augmented Generation; Yan et al., 2024) and **Self-RAG** (Asai et al., 2023). Both define a feedback loop around the retriever:

```
[query] → retrieve → grade (relevant / ambiguous / irrelevant) →
   if relevant   → continue with top-K
   if ambiguous  → expand (rewrite, hop, or HyDE) → retrieve again
   if irrelevant → abort + signal "no evidence" or fall back to web/KG
```

The repo already has the **upstream parts**: a reflexion engine at L3
(`reflexion_engine.py`, 91 matches) for orchestration-side reflection, GraphRAG local/global/drift engines for KG hop, ADG SQLite for structural fallback, and (post-ADR-058) query transforms for reformulation. None of these are wired into a retrieval-time loop. The reflexion engine is scoped to *agent task* reflection — not retrieval-evidence reflection.

CRAG's own ablation reports +3–8 % EM and +5–11 % F1 on Knowledge-NQ vs. vanilla RAG, with the largest gains on out-of-distribution queries — exactly the queries Cursor Agent fields when the corpus lags behind a fast-moving codebase.

## Decision

Adopt a **Corrective-RAG-style reflective loop** as the canonical retrieval shape for L1 cognition queries that opt in. Loop is bounded, observable, and budget-capped.

### Normative Requirements

1. **Loop shape** (canonical):
   ```
   step 1: initial_retrieve(query)        → candidates_t0
   step 2: grade(query, candidates_t0)    → {relevant, ambiguous, irrelevant} per chunk
   step 3: decide loop control:
            relevant ≥ k_min   → return; no further loops
            ambiguous-only     → expand_then_retrieve, increment t
            irrelevant-only    → fallback_or_abstain
   step 4: if iteration cap not reached and decision = expand → goto step 1 with rewritten query
   ```
   Loop cap: hard 3 iterations. Budget cap: per-iteration latency ≤ 800 ms; total wall-clock ≤ 3 s.

2. **Grader contract** — `agentic_core/L1_cognition/reasoning/retrieval_grader.py` (new). Single method `grade(query, chunks) -> list[GradeVerdict]` returning per-chunk `{verdict: "relevant"|"ambiguous"|"irrelevant", score: 0..1, rationale: str≤120}`. Backed by:
   - Default: a small fast LLM (Qwen-14B via the L3 vLLM gateway, mirroring ADR-045 backend selection).
   - Fallback: a heuristic (lexical-overlap × cross-encoder rerank score) when LLM unavailable.
   - Cache: keyed by `(query_hash, chunk_id, grader_identity)` — avoids re-grading the same chunk on retries.

3. **Expansion strategies** (chosen by the grader's verdict distribution):
   - **All ambiguous** → run ADR-058 query transform (HyDE preferred for code/NL gap; step-back for abstract why).
   - **Mostly irrelevant** → graph hop: query the structural ADG (`adg_edge_fanin` / `adg_nodes_by_layer`) and fold matched nodes' source paths into the next retrieval as a `where={file_path: prefix_match}` filter.
   - **Mixed** → multi-query fusion of original + grader-rationale-derived rewrite.
   Each expansion step records what it tried and why in the OTel span.

4. **Fallback ladder** — when the loop exhausts without convergence:
   - Tier 1: return the best candidates with an `evidence_quality: "weak"` marker — caller decides whether to abstain.
   - Tier 2: emit a `RetrievalAbstainSignal` (new dataclass) — the prompt assembler refuses to fabricate without evidence and surfaces a "no support" response. Closes the silent-confabulation failure mode.

5. **Self-RAG reflection tokens (deferred to v2)** — Self-RAG's full reflective-token output (`[Retrieve]`, `[ISREL]`, `[ISSUP]`, `[ISUSE]`) requires a fine-tuned generator. Out of scope for v1; the grader contract above is structurally compatible with adding reflection tokens later.

6. **Wire-up under existing engines** — `agentic_core/knowledge/engine/rag_orchestrator.py` exposes a `reflective: bool = False` flag on its query API. False keeps current behaviour; True enters the loop. The future agentic router (W6.2 / ADR-064) sets the flag based on query intent.

7. **Reflexion-engine binding** — see W4.2 spec at `docs/reports/plans/reflexion-retriever-binding.md`. The L3 reflexion engine remains task-scoped; this ADR binds a *retrieval-scoped* reflexion variant under L1 reasoning. The two share the dataclass shape (`ReflectionTrace`) but not the executor.

8. **Telemetry** — every loop iteration emits an OTel span:
   - `gen_ai.retrieval.loop_iter = <int>`
   - `gen_ai.retrieval.grade_verdict_dist = "{relevant:n, ambiguous:n, irrelevant:n}"`
   - `gen_ai.retrieval.expansion_strategy = <name|none>`
   - `gen_ai.retrieval.loop_cap_reason = <converged|cap|budget|abstain>`
   Pipes into `otel_mcp.healing_chain` for cross-session anomaly mining.

### Non-Goals

- A reflective generator (Self-RAG-style fine-tune). Generator-side reflection is downstream concern; this ADR is retrieval-side.
- Replacing ADR-058 transforms — the loop *uses* them, doesn't replace.
- Replacing GraphRAG. The loop calls into it as a fallback, not as a substitute.
- Runtime HITL (ADR-023) — that pauses for human approval; this loop is fully autonomous.

## Consequences

**Positive**
- Closes the largest documented agentic-retrieval gap beyond ingest-side ADR-045.
- Failure attribution becomes mechanical: span records *why* retrieval gave up.
- Abstain signal is the cleanest defense against confabulation we can wire without changing the generator.
- Reflexion patterns reused; no new orchestration concepts.

**Negative / costs**
- One extra LLM call per chunk for grading. Mitigated by parallel-batched grading on local Qwen and by the cache.
- Worst-case retrieval latency triples (3 iterations × ≤ 800 ms). Mitigated by hard caps and by the agentic router opting in only when query intent justifies it.
- Adds a new failure mode: misgrading. Mitigated by W5.1 acceptance gate that compares loop-on vs loop-off recall on the golden set per query class.

**Risks**
- **R1 — grader hallucinates relevance.** Mitigation: per-chunk score plus rationale logged; W5.1 quarterly audit on a 100-query human-graded subset; rollback knob `RETRIEVAL_REFLECTIVE=0`.
- **R2 — loop budget drained on hot path.** Mitigation: P95 budget alerts in OTel; hard cap is enforced before any LLM call.
- **R3 — abstain signal disrupts existing callers.** Mitigation: opt-in flag; default off until W5.1 demonstrates parity-or-better.

## Validation

- `pytest tests/unit/agentic_core/L1_cognition/reasoning/test_retrieval_grader.py` — grader determinism, cache, fallback path.
- `pytest tests/integration/test_reflective_retrieval_loop.py` — loop-cap enforcement, expansion-strategy selection, abstain signal.
- W5.1 golden-set acceptance: Recall@20 ≥ baseline + 3 %, abstain-precision ≥ 0.85 (when abstain fires, ground truth confirms no evidence existed).

Rollback: `RETRIEVAL_REFLECTIVE=0` env var disables the loop globally; orchestrator falls back to single-pass.

## Alternatives Considered

1. **Single-pass forever.** Status quo. Concedes published gains; leaves silent confabulation open.
2. **Skip grading, just rewrite-and-retry on empty top-K.** Cheap but only catches the most obvious failure; published evidence shows grading is the lever.
3. **Use the reflexion engine directly without a retrieval-scoped variant.** Wrong layer; reflexion engine reasons about agent task outcomes, not chunk relevance.
4. **Self-RAG full reflection-token generator.** Highest ceiling but requires fine-tune. Defer until ADR-058 + ADR-060 v1 establish the harness.

## References

- Yan et al., *Corrective Retrieval Augmented Generation* (2024)
- Asai et al., *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* (ICLR 2024)
- Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning* (NeurIPS 2023)
- In-repo: `agentic_core/L3_orchestration/reasoning/engines/reflexion_engine.py`, `agentic_core/knowledge/engine/rag_orchestrator.py`
- Sibling spec: `docs/reports/plans/reflexion-retriever-binding.md` (W4.2)
- Parent plan: `.windsurf/plans/chromadb-best-in-class-agentic-embeddings-c4a1f8.md`
