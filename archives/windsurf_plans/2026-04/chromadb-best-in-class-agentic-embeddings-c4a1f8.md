# ChromaDB Embeddings — Best-in-Class Agentic Review & Gap Plan

**Plan ID:** `chromadb-best-in-class-agentic-embeddings-c4a1f8`
**Tier:** T3 (architectural, cross-layer, affects L1/L3/L4/L6)
**Created:** 2026-04-24
**Status:** W1–W6 DESIGN-COMPLETE (2026-04-24) — see §12 deliverables index; no code changes
**Scope:** Retrieval-quality and agentic-retrieval techniques (NOT infrastructure plumbing)
**Sibling plan (do not duplicate):** `chromadb-bge-retrieval-hardening-e9aa09.md` handles dual-store consolidation, zero-vector fallbacks, stale ADG joins, schema drift.

---

## 1. Executive Summary

The repo is **infrastructurally mature** (BGE-M3 factory, sovereignty guard, BM25, hybrid fusion, cross-encoder reranker, GraphRAG local/global/drift, late chunking, OTel eval spine, golden/adversarial eval scaffolds). It is **not yet best-in-class on the 2025-2026 agentic-retrieval frontier**. The principal quality gaps are:

1. **No Contextual Retrieval** (Anthropic, Sept 2024) — chunks are embedded naked; industry-standard 35–67 % failure reduction is left on the floor.
2. **BGE-M3 used dense-only** — the model's built-in sparse + ColBERT multi-vector heads are unused, yet they cost <10 % extra compute per forward pass.
3. **Reranker coverage is partial and un-audited** — cross-encoder exists but wiring into `SovereignChromaClient.query`, `SovereignRAGManagerAgent`, and `rag_orchestrator` is not uniform.
4. **Query transformation is shallow** — `multi_query_fusion` exists; no HyDE, no step-back, no query decomposition, no self-query metadata extraction.
5. **No Corrective-RAG / Self-RAG / reflective retrieval loop** — `reflexion_engine` exists at L3 but is not bound to the retriever; retrieval is one-shot.
6. **No Matryoshka / adaptive dimensionality** — static 1024-d everywhere; router cannot trade recall for latency.
7. **Evaluation is ad-hoc** — `retrieval_benchmark.py` and `retrieval_abcd_harness.py` exist but no nightly gate, no RAGAS-style faithfulness loop, no drift detection on production queries.
8. **Embedding versioning is soft** — `embedder_identity` stamped in cache keys but not enforced at collection write; silent model swaps can co-mingle 1024-d BGE with 1536-d OpenAI vectors in the same HNSW index.
9. **Chunking is single-strategy per source** — code=AST (skips zero-arg funcs), docs=token-window (no header-aware, no sentence-window / parent-document for prose).
10. **No agentic-retrieval router** — query class → collection set → retrieval strategy is hardcoded, not learned or LLM-selected.

This plan documents the gap, not the fix. All waves are **design/spec/ADR** deliverables; execution is deferred to downstream plans.

---

## 2. Best-in-Class Agentic Embedding Architecture (2025-2026 reference model)

| # | Capability | Industry reference | Repo status |
|---|---|---|---|
| 1 | **Modern embedder** with sparse+dense+multi-vector in one model | BGE-M3, voyage-3, Nomic-embed-v2 MoE, Stella, GTE-Qwen2 | ✅ BGE-M3 (dense only) |
| 2 | **Contextual Retrieval** (LLM-generated chunk-situating prefix before embed) | Anthropic Sept 2024 (49 % ↓ failure vs vanilla; 67 % ↓ with rerank) | ❌ Absent |
| 3 | **Hybrid dense + sparse (BM25)** + RRF fusion | LangChain / LlamaIndex default | ✅ Present (`hybrid_search_engine.py`, `bm25_store.py`) |
| 4 | **Cross-encoder reranker** on top-50 → top-K | bge-reranker-v2-m3, Cohere rerank-3, Voyage rerank-2 | ✅ `cross_encoder_reranker.py` — wiring uneven |
| 5 | **Late chunking** (embed whole doc, pool per chunk) | Jina 2024 | ✅ `late_chunking.py`, `late_chunking_helper.py` |
| 6 | **Multi-vector / late-interaction (ColBERT)** for long-context fidelity | ColBERT v2, BGE-M3 ColBERT head, PLAID | ⚠️ Archived only (`archives/.../late_interaction_reranker_util.py`) |
| 7 | **Matryoshka / adaptive dim** — one model, many truncations | OpenAI text-embedding-3, Nomic, BGE-M3 | ❌ Absent |
| 8 | **Query transformation** — HyDE, multi-query, step-back, decomposition | LangChain / LlamaIndex patterns | ⚠️ Partial (`multi_query_fusion.py` only) |
| 9 | **Self-query** — LLM extracts metadata filter from NL query | LangChain SelfQueryRetriever | ❌ Absent |
| 10 | **Parent-document / small-to-big / sentence-window** | LlamaIndex 2024 patterns | ⚠️ Metadata has `parent_id`; no retrieval-time expansion wired |
| 11 | **GraphRAG** — local + global + drift | Microsoft GraphRAG, Neo4j GraphRAG | ✅ `local_search_engine`, `global_search_engine`, `drift_search_engine` |
| 12 | **Corrective RAG (CRAG) / Self-RAG / reflective retrieval** | Yan 2024 (CRAG), Asai 2023 (Self-RAG) | ❌ Not wired (orchestration reflexion exists but not retrieval-bound) |
| 13 | **Agentic router** — LLM chooses collection set + strategy per query | LlamaIndex RouterQueryEngine, Anthropic agentic search | ❌ Hardcoded routing |
| 14 | **Metadata-filtered pre-retrieval** (layer, artifact_type, freshness) | Chroma `where` native | ⚠️ Supported but not exercised by agents |
| 15 | **Embedding cache + semantic cache (GPTCache)** | GPTCache, Redis vector cache | ✅ `gptcache_client.py`, `tool_embedding_cache.py` |
| 16 | **Deterministic embedder identity + replay** | Evaluation reproducibility | ✅ `create_deterministic_cache_key`, `get_replay_metadata` |
| 17 | **Collection-level embed-model enforcement** | Chroma metadata fence + validator | ⚠️ Stamped but not enforced at write |
| 18 | **PII/secret redaction before embed** | Data hygiene | ✅ `GuardedText` / `embedding_input_guard` |
| 19 | **Nightly retrieval regression** with golden set | RAGAS, TruLens, Ragas CI | ⚠️ Harness exists, no schedule |
| 20 | **Production query telemetry → drift detector** | OpenTelemetry + anomaly | ⚠️ Spans emitted, no drift loop |
| 21 | **Adversarial eval set** | Red-team prompts | ⚠️ `data/eval/adversarial/` exists, population unconfirmed |
| 22 | **Query-time cost/latency budget** per tier | Tiered SLO | ❌ Absent |
| 23 | **Kill-switch + fail-closed** | Operational safety | ✅ `EMBEDDING_ENABLED` |
| 24 | **Observability on retrieval spans** | OTel semconv for RAG | ⚠️ Emitted; no per-stage attribution (embed, search, rerank, expand) |

**Legend:** ✅ present, ⚠️ partial, ❌ absent.

---

## 3. Gap Register (ranked by impact × effort)

### G1 — Contextual Retrieval (P1, high impact, medium effort)
- **Gap:** Chunks embedded as raw text without an LLM-generated situating prefix. Anthropic's published benchmark shows 35 % retrieval-failure reduction (dense), 49 % (dense+BM25), 67 % (dense+BM25+rerank).
- **Repo evidence:** `tools/ingestion/ingest_code.py`, `ingest_docs.py`, `ingest_tests.py` emit raw `chunk.text` as the embedding input.
- **Fix shape:** Add a pre-embed pass where a fast LLM (Claude Haiku / GPT-4o-mini / local Qwen) generates a ≤100-token context prefix: *"This code chunk belongs to `<file>`, class `<cls>`, responsible for `<one-sentence role>`."* Prefix is stored separately so retrieval returns the **original** chunk text but the embedding is **contextualized**.
- **Cost:** ~1 LLM call per chunk at ingest time; amortized via prompt-caching (Anthropic prompt cache cuts 90 %).
- **Deliverable:** ADR + prefix-generator spec + cache contract.

### G2 — BGE-M3 sparse + ColBERT heads unused (P2, high impact, low effort)
- **Gap:** BGE-M3 produces dense **and** lexical-weighted sparse **and** ColBERT multi-vector in a single forward pass. Only the dense head is stored. Losing the sparse head duplicates BM25 work less accurately; losing ColBERT forfeits long-chunk fidelity.
- **Fix shape:** Extend `BGEM3EmbeddingClient` to return `{dense, sparse, colbert}`; store dense in Chroma, sparse in `bm25_store` (replacing plain BM25 counts), and ColBERT vectors in a sidecar (`artifacts/chromadb/colbert/`) for rerank-time late interaction.
- **Deliverable:** ADR on multi-head BGE + index layout spec.

### G3 — Reranker coverage audit + unification (P1, medium impact, low effort)
- **Gap:** `cross_encoder_reranker.py`, `senior_librarian_reranker.py`, `bge_reranker_adapter.py`, `completeness_reranker.py`, and `reranker_factory.py` all coexist. `HybridSearchEngine` exposes a pluggable `RerankerFn`, but `SovereignChromaClient.query`, `rag_orchestrator.py`, and `SovereignRAGManagerAgent` do not route through it uniformly. See ADR-046 (rerank revival) for prior scope.
- **Fix shape:** Inventory every retrieval call-site (ADG query), pick one reranker (bge-reranker-v2-m3), enforce via factory, retire duplicates.
- **Deliverable:** Inventory matrix + single-reranker ADR revision.

### G4 — Query transformation breadth (P2, medium impact, medium effort)
- **Gap:** Only `multi_query_fusion` present. No **HyDE** (hypothetical-answer embedding for code where query/answer vocabulary diverges), no **step-back** (abstract reformulation for multi-hop), no **decomposition** (long queries → sub-queries → fused results), no **self-query** (LLM extracts `where={layer:"L3"}` from NL).
- **Fix shape:** Add four strategies under `agentic_core/L1_cognition/reasoning/query_transforms/`, selected by a lightweight classifier (rule-based first, LLM-gated later).
- **Deliverable:** Strategy catalog spec + routing rubric.

### G5 — Corrective / Self / reflective retrieval (P2, high impact, high effort)
- **Gap:** Retrieval is single-pass. No mechanism to grade retrieved context, trigger re-query, or fall back to web/ADG when corpus insufficient. `reflexion_engine` at L3 is orchestration-scoped, not retrieval-scoped.
- **Fix shape:** Wrap retrieval in a CRAG loop: grade each chunk (relevant / ambiguous / irrelevant), on ambiguous → expand via knowledge-graph hop or HyDE; on irrelevant → re-retrieve with reformulated query; cap iterations (≤3) with token budget.
- **Deliverable:** CRAG/Self-RAG loop spec + grader rubric + stop-condition matrix.

### G6 — Matryoshka / adaptive dimensionality (P3, medium impact, low effort)
- **Gap:** Every embedding is 1024-d. Cold paths (anomaly triage, background audit) don't need full fidelity; hot paths (interactive) tolerate higher cost.
- **Fix shape:** Use BGE-M3's native dim truncation (128/256/512/1024) or move select collections to OpenAI-3-large with Matryoshka. Router picks dim based on query SLO.
- **Deliverable:** Tier × dim matrix, Chroma collection-per-dim plan.

### G7 — Evaluation cadence + RAGAS (P1, medium impact, low effort)
- **Gap:** `tools/eval/retrieval_benchmark.py`, `retrieval_abcd_harness.py`, `retrieval_eval_curated.py` exist but no scheduled run, no RAGAS faithfulness / answer-relevancy / context-precision metrics, no dashboard.
- **Fix shape:** Nightly pytest-scheduled eval on a frozen golden set (≥200 query-answer pairs across code / docs / tests / traces / incidents), RAGAS + repo-native metrics, OTel span per query, Notion writeback on regression.
- **Deliverable:** Golden-set spec + CI schedule + dashboard page.

### G8 — Embedding versioning enforcement (P2, medium impact, low effort)
- **Gap:** `SovereignChromaClient.get_collection` stamps `embedding_model` + `embedding_dim` on `get_or_create`. If the collection already exists with different model, the stamp is silently stale and `validate_collection.py` only warns.
- **Fix shape:** On every `add_documents`, re-read collection metadata; if `(model, dim)` mismatches the active embedder, raise `EmbeddingProvenanceMismatchError` — no silent co-mingling.
- **Deliverable:** Enforcement-point spec + error taxonomy.

### G9 — Chunking strategy breadth (P2, medium impact, medium effort)
- **Gap:** Code = AST but skips zero-arg functions + method-less classes (already noted in sibling plan). Docs = token-window; no header-aware, no sentence-window, no parent-document. Traces = JSONL per line — no event-window grouping.
- **Fix shape:** (a) AST chunker: retain skipped entities as "thin chunks" with parent-class context; (b) Docs: markdown-aware chunker with H1/H2 lineage in metadata; (c) Traces: causal-window grouping (parent-span + children).
- **Deliverable:** Chunker catalog + per-source ADR.

### G10 — Agentic router (collection + strategy selection) (P3, high impact, high effort)
- **Gap:** Callers hardcode collection names (`code_chunks`, `docs`, `adg_graph`). No router decides which collections + which strategy (hybrid vs graph vs late-chunking vs rerank-only) for a given query.
- **Fix shape:** Lightweight LLM or rule-classifier at L0/L1 boundary maps query intent → `{collections: [...], strategy: <...>, budget: <ms>}`. Fits the existing v33 process map.
- **Deliverable:** Router contract + intent taxonomy.

### G11 — Observability per retrieval stage (P3, medium impact, low effort)
- **Gap:** OTel spans emitted by factory; no per-stage attribution (embed → dense-search → sparse-search → fuse → rerank → expand). Anomaly debugging currently requires code reading.
- **Fix shape:** OTel semconv for RAG: `gen_ai.retrieval.stage`, `gen_ai.retrieval.top_k`, `gen_ai.retrieval.score_dist`, `gen_ai.rerank.latency_ms`.
- **Deliverable:** Span schema + `otel_mcp` ingestion contract.

### G12 — Adversarial + drift eval (P3, medium impact, medium effort)
- **Gap:** `data/eval/adversarial/` directory exists but population/cadence unknown. No production-query drift detector to flag embedding staleness (e.g., new framework names not in corpus).
- **Fix shape:** Populate adversarial set (100 red-team queries: paraphrase, typo, code-in-prose, prose-in-code, ambiguous intent); monthly drift run comparing production query embeddings vs corpus centroid.
- **Deliverable:** Adversarial corpus spec + drift metric definition.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Foundations: contextual-retrieval wiring audit + reranker unification + embed-model enforcement ADR | ~18 000 | Sibling plan's dual-store consolidation completes first | ✅ DESIGN-COMPLETE | ADR-045 audit + ADR-046 amendment spec + ADR-055 drafted |
| W2 | W2.1, W2.2 | Model fidelity: BGE-M3 multi-head + Matryoshka | ~14 000 | W1 complete; BGE-M3 multi-head export validated | ✅ DESIGN-COMPLETE | ADR-056 + ADR-057 drafted |
| W3 | W3.1, W3.2 | Query intelligence: HyDE + step-back + decomposition + self-query + routing rubric | ~16 000 | Classifier scaffolding in L1 | ✅ DESIGN-COMPLETE | ADR-058 + routing rubric drafted |
| W4 | W4.1, W4.2 | Reflective retrieval: CRAG loop + retrieval-bound Reflexion | ~20 000 | W1-W3 complete; grader LLM available | ✅ DESIGN-COMPLETE | ADR-060 + reflexion-binding spec drafted |
| W5 | W5.1, W5.2, W5.3 | Evaluation + observability: golden set, nightly CI, RAGAS, per-stage OTel, drift | ~15 000 | eval harnesses stabilized | ✅ DESIGN-COMPLETE | ADR-061 + cron/dashboard report + ADR-062 drafted |
| W6 | W6.1, W6.2 | Agentic router + chunker breadth | ~12 000 | W1-W5 outputs converge on routing contract | ✅ DESIGN-COMPLETE | ADR-063 + ADR-064 drafted |

**Token legend:** 🟢 GREEN <25k · 🟡 YELLOW 25–40k · 🔴 RED >40k. All waves GREEN.

---

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files/specs) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Contextual Retrieval ADR | New ADR `ADR-???-contextual-retrieval.md`; prefix-generator spec; prompt-cache contract | Picking a cheap LLM; cache invalidation on reembed | 9 000 | Todo |
| W1.2 | Reranker unification + embed-model fence | Inventory matrix of 5 rerankers; revise ADR-046; new `EmbeddingProvenanceMismatchError` spec | Retiring duplicates without breaking callers | 9 000 | Todo |
| W2.1 | BGE-M3 multi-head integration ADR | Sparse+ColBERT head storage layout; `bm25_store` replacement plan | ColBERT sidecar index size; query-time late interaction cost | 8 000 | Todo |
| W2.2 | Matryoshka tiering spec | Tier × dim matrix; per-collection policy; Chroma collection-per-dim proposal | Migration of existing 1024-d corpus | 6 000 | Todo |
| W3.1 | Query transforms catalog | HyDE, step-back, decomposition, self-query specs under `L1_cognition/reasoning/query_transforms/` | Classifier accuracy vs LLM cost | 9 000 | Todo |
| W3.2 | Transform routing rubric | Intent → transform mapping; fallback matrix | Avoiding combinatorial explosion | 7 000 | Todo |
| W4.1 | CRAG loop spec | Grader rubric (relevant/ambiguous/irrelevant), expansion hops, stop conditions | Grader LLM latency; loop cap | 11 000 | Todo |
| W4.2 | Reflexion↔retriever binding | Map L3 `reflexion_engine` hooks to retrieval loop; contract with `SovereignRAGManagerAgent` | Layer gravity (L3 → L1 call) | 9 000 | Todo |
| W5.1 | Golden-set + RAGAS spec | ≥200 query-answer pairs; RAGAS metrics; curator process | Building ground truth; maintainer load | 7 000 | Todo |
| W5.2 | Nightly CI + Notion dashboard | pytest-schedule, regression gate, Wave/Phase DB writeback | Flaky embeddings in CI | 4 000 | Todo |
| W5.3 | RAG OTel semconv + drift metric | Per-stage attributes; `otel_mcp` ingest rule; drift definition | Cardinality / cost | 4 000 | Todo |
| W6.1 | Chunker catalog ADR | AST-thin-chunks, markdown-header-aware, sentence-window, trace-causal-window | Metadata schema expansion | 7 000 | Todo |
| W6.2 | Agentic router contract | Intent taxonomy; query → {collections, strategy, budget}; evaluation harness | Integration with v33 process map | 5 000 | Todo |

---

## 6. Dependency Map

```
Sibling plan (e9aa09) ─── consolidates stores ───▶ W1 ─▶ W2 ─▶ W3 ─▶ W4
                                                  │          │
                                                  └─▶ W5 ◀───┘
                                                           │
                                                           ▼
                                                          W6
```

- **W1** blocks everything (fences + reranker contract).
- **W2** independent of W3; both blocked on W1.
- **W4** blocked on W1+W2+W3.
- **W5** can start after W1; runs in parallel.
- **W6** last (needs outputs of W3+W4 for router intent taxonomy).

---

## 7. Out of Scope

- Infrastructure consolidation (owned by `chromadb-bge-retrieval-hardening-e9aa09`).
- ADG → ChromaDB anti-pattern (structural graph questions stay in SQLite; see `docs/reference/AST Dependency Graphs (ADG)/ADG ChromaDB Antipattern.md`).
- Vector DB replacement (Qdrant / Weaviate / Milvus) — ADR-018 binds us to ChromaDB; revisiting is a separate T3 plan.
- Embedding model replacement (keeping BGE-M3 for determinism + offline).

---

## 8. Success Metrics (aggregate)

| Metric | Today (measured where possible) | Target post-W1–W6 |
|---|---|---|
| Retrieval failure rate on golden set (top-5 not containing gold doc) | Unmeasured | ≤ 5 % |
| RAGAS context-precision on golden set | Unmeasured | ≥ 0.85 |
| RAGAS context-recall | Unmeasured | ≥ 0.90 |
| Retrieval p95 latency (hot path, interactive) | Unmeasured | ≤ 600 ms |
| Retrieval p95 latency (cold path, background) | Unmeasured | ≤ 3 s |
| Silent zero-vector / dim-mismatch incidents/month | ≥ 1 (evidence in sibling plan) | 0 (hard fail) |
| Drift alert coverage | 0 % | 100 % of production collections |

---

## 9. Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | Contextual Retrieval ingest cost balloons (1 LLM call per chunk × ~100 K chunks) | Claude Haiku with prompt caching (90 % discount); incremental re-ingest only on `canonical_digest` change |
| R2 | BGE-M3 ColBERT sidecar index size | Quantize to int8; store only for top-tier collections (code, docs) |
| R3 | CRAG loop p95 latency regression | Hard loop cap (≤3); shadow mode before enable; per-query token budget |
| R4 | Golden-set drift / maintainer burden | Quarterly refresh cadence; auto-flag stale queries via production-query centroid |
| R5 | Reranker-factory churn breaks callers | W1.2 starts with inventory; retire only after callers migrated |
| R6 | Agentic router increases non-determinism | Shadow mode + A/B against hardcoded baseline; rollback trigger on RAGAS regression |

---

## 10. References

- `docs/architecture/adr/ADR-018-chromadb-as-canonical-vector-store.md`
- `docs/architecture/adr/ADR-046-rerank-revival.md`
- `docs/reference/AST Dependency Graphs (ADG)/ADG ChromaDB Antipattern.md`
- `.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md` (sibling — infra)
- `.windsurf/plans/adg-chromadb-retrieval-assessment-8a3f2b.md` (prior assessment)
- `.windsurf/plans/c0-context-assembly-best-practices-b7c3a1.md`
- `.windsurf/plans/hybrid-search-adg-seed-rerank-c58e21.md`
- External: Anthropic Contextual Retrieval (Sept 2024), Jina Late Chunking (2024), Yan CRAG (2024), Asai Self-RAG (2023), Microsoft GraphRAG (2024), ColBERT v2 / PLAID.

---

## 11. Next Actions (no code)

1. Review this plan; mark accepted waves.
2. For each accepted wave, spawn an ADR skeleton under `docs/architecture/adr/`.
3. W1.1 (Contextual Retrieval) recommended first — highest impact × lowest risk, independent of multi-head work.

## 12. W1–W3 Deliverables Index (landed 2026-04-24)

| Wave.Phase | Deliverable | Location | Kind |
|---|---|---|---|
| W1.1 | Contextual Retrieval wiring evidence audit | `docs/reports/plans/contextual-retrieval-wiring-evidence-audit.md` | Report — found 3 residual gaps; ADR-045 stands |
| W1.2 | Reranker unification inventory + ADR-046 amendment text | `docs/reports/plans/reranker-unification-inventory.md` | Inventory + amendment proposal |
| W1.3 | Embedding model enforcement ADR | `docs/architecture/adr/ADR-055-embedding-model-enforcement.md` | Net-new ADR |
| W2.1 | BGE-M3 multi-head ADR | `docs/architecture/adr/ADR-056-bge-m3-multi-head.md` | Net-new ADR |
| W2.2 | Matryoshka / adaptive-dim ADR | `docs/architecture/adr/ADR-057-matryoshka-adaptive-dim.md` | Net-new ADR |
| W3.1 | Query transforms catalog ADR | `docs/architecture/adr/ADR-058-query-transforms-catalog.md` | Net-new ADR |
| W3.2 | Query-transform routing rubric | `docs/reports/plans/query-transform-routing-rubric.md` | Rubric spec |
| W4.1 | CRAG / Self-RAG reflective retrieval ADR | `docs/architecture/adr/ADR-060-corrective-rag-reflective-retrieval.md` | Net-new ADR |
| W4.2 | Reflexion ↔ retriever binding | `docs/reports/plans/reflexion-retriever-binding.md` | Layer-gravity spec |
| W5.1 | Golden set + RAGAS evaluation harness ADR | `docs/architecture/adr/ADR-061-retrieval-golden-set-ragas-eval.md` | Net-new ADR |
| W5.2 | Nightly retrieval-eval cron + Notion dashboard | `docs/reports/plans/retrieval-eval-cron-and-dashboard.md` | Operations spec |
| W5.3 | RAG OTel semconv + drift metric ADR | `docs/architecture/adr/ADR-062-rag-otel-semconv-and-drift.md` | Net-new ADR |
| W6.1 | Chunker catalog ADR | `docs/architecture/adr/ADR-063-chunker-catalog.md` | Net-new ADR |
| W6.2 | Agentic retrieval router ADR | `docs/architecture/adr/ADR-064-agentic-retrieval-router.md` | Integration ADR |

**Re-scoping note:** W1.1 + W1.2 were re-framed during execution once ADR-045 (Contextual Retrieval) and ADR-046 (Rerank Revival) were found to already exist. W1.1 became a wiring-evidence audit for ADR-045; W1.2 produced an inventory matrix with amendment text for ADR-046. ADR-046 amended on disk + Notion patched 2026-04-24. Net-new ADRs span 055–064 (10 ADRs total).

**Blocked from this wave (tracked here, owned elsewhere):**
- Execution of the ADRs (actual code landing) — separate plans per ADR acceptance, see §13 NEXT_STEP markers.

---

## 13. Next Steps

NEXT_STEP: plan=NEW:adr-045-ingest-docs-qwen-wiring title=Mirror build_context_gateway helper into ingest_docs.py priority=P2 est_tokens=4000 reason=W1.1 audit found ingest_docs bypasses ADR-045 local-LLM default; docs corpus only contextualized when Anthropic key set
NEXT_STEP: plan=NEW:adr-055-embedding-model-enforcement-impl title=Implement ADR-055 fail-closed embed-model checks priority=P2 est_tokens=12000 reason=ADR drafted W1.3; sibling plan e9aa09 documents active silent vector-dim corruption
NEXT_STEP: plan=NEW:adr-046-reranker-factory-ci-gate title=Land check_reranker_factory_use CI gate priority=P3 est_tokens=5000 reason=W1.2 inventory confirms direct reranker imports bypass the canonical factory across 5+ call sites
NEXT_STEP: plan=NEW:w5-retrieval-eval-harness title=Golden-set plus RAGAS nightly retrieval eval priority=P2 est_tokens=15000 reason=All five new ADRs (045 amend, 055-058) declare W5 acceptance gates; harness is the common prerequisite
NEXT_STEP: plan=NEW:adr-056-bge-m3-multi-head-impl title=Implement ADR-056 sparse plus ColBERT heads priority=P3 est_tokens=18000 reason=Free retrieval-quality gains from already-paid model forward pass
NEXT_STEP: plan=NEW:adr-058-query-transforms-impl title=Implement ADR-058 query transforms catalog priority=P3 est_tokens=16000 reason=HyDE plus step-back plus decomposition plus self-query close the largest query-side gap
NEXT_STEP: plan=NEW:adr-060-reflective-retrieval-impl title=Implement ADR-060 CRAG reflective retrieval loop priority=P3 est_tokens=18000 reason=Closes silent-confabulation failure mode via grader plus abstain ladder
NEXT_STEP: plan=NEW:adr-061-golden-set-curation title=Curate first 210-pair retrieval golden set priority=P2 est_tokens=8000 reason=Every other ADR acceptance gate is unenforceable until the golden set exists
NEXT_STEP: plan=NEW:adr-062-rag-otel-semconv-impl title=Implement RAG OTel constants module plus drift cron priority=P3 est_tokens=10000 reason=Connects ingest-side ADRs to live retrieval health signal
NEXT_STEP: plan=NEW:adr-063-chunker-catalog-impl title=Implement chunker catalog plus 5 new chunkers priority=P3 est_tokens=14000 reason=Closes 10-15 percent ADG node-loss gap and unlocks parent-document hydration
NEXT_STEP: plan=NEW:adr-064-agentic-router-impl title=Implement agentic retrieval router with shadow mode priority=P3 est_tokens=12000 reason=Single integration point for ADRs 045 through 063; without it knobs leak to agent layer

DEFERRED_SCOPE: plan=chromadb-best-in-class-agentic-embeddings-c4a1f8 wave=W1 phase=W1.1-followup layer=L_TOOLS fan_in=3 surface=None coverage_gap_pct=40.0 est_tokens=4000 reason=ingest_docs bypasses ADR-045 backend matrix
DEFERRED_SCOPE: plan=chromadb-best-in-class-agentic-embeddings-c4a1f8 wave=W1 phase=W1.1-followup-b layer=L_TOOLS fan_in=5 surface=State coverage_gap_pct=55.0 est_tokens=8000 reason=Newer tools/generate/ingestion scripts have no contextualization wiring
DEFERRED_SCOPE: plan=chromadb-best-in-class-agentic-embeddings-c4a1f8 wave=W1 phase=W1.2-adg-audit layer=L_APP fan_in=9 surface=None coverage_gap_pct=30.0 est_tokens=3000 reason=ADG fan-in required before Tier-A reranker retirement per agent-deletion-gate
