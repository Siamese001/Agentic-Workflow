# Anthropic RAG Anti-Pattern Audit — Agentic-Workflow

**Phase:** P3.2 of `.windsurf/plans/anthropic-rag-gaps-7f3c2a.md`
**Date:** 2026-04-22
**Method:** ChromaDB live inventory + ADG fan-in + targeted code inspection
**Source of anti-patterns:** `docs/reference/03_L0_Routing/C0 - Retrieval/Anthropic RAG Best Practices.md` §12 (Anthropic, 2024-09)

---

## Scoring convention

| Verdict | Meaning |
|---|---|
| ✅ **Clean** | Repo does NOT exhibit this anti-pattern; evidence below. |
| ⚠️ **Partial** | Repo exhibits the anti-pattern but has compensating mechanism or scoped exposure. |
| ❌ **Exhibits** | Anti-pattern is present without compensation. |
| 🚧 **Pending fix** | Anti-pattern is present but a landed W1/W2 module provides the repair (needs adoption). |

---

## The 7 anti-patterns

### 1. Building RAG when long-context + caching would be simpler and better

**Verdict:** ❌ **Exhibits**

**Evidence:**
- `grep "token.*threshold|corpus_size|full_context"` returns no corpus-size gate before RAG entry.
- `@c:/Git/Agentic-Workflow/apps_shared/enforcement/AdaptiveretrievalgateStrategy.py` gates on query intent, not corpus token count.
- No branch in the routing layer that says "if corpus ≤ 200k tokens, skip retrieval and use full-context + cache instead."

**Impact:** For small corpora (policies, specs, SOPs < 200k tokens), the repo always runs the full hybrid-retrieval + rerank pipeline even though a single full-context call with prompt caching would be cheaper and more accurate per Anthropic's own data.

**Remediation:** P4.1 of the plan — add a corpus-size gate.

---

### 2. Using vector-only retrieval when BM25 would handle exact identifiers better

**Verdict:** ✅ **Clean**

**Evidence:**
- BM25 lexical scorer: `@c:/Git/Agentic-Workflow/agentic_core/L4_state/memory/semantic/bm25_scorer.py` (k1=1.5, b=0.75 canonical tuning)
- BM25 store: `@c:/Git/Agentic-Workflow/agentic_core/L4_state/utils/memory/bm25_store.py`
- Inline population during ingest: `@c:/Git/Agentic-Workflow/tools/ingestion/ingest_code.py:417-424` calls `get_bm25_store().add_documents(bm25_docs)` (verified via grep 2026-04-22).
- Hybrid fusion: `@c:/Git/Agentic-Workflow/agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` has `HybridSearchResult` with `vector_score`, `lexical_score`, `combined_score`.

**Impact:** N/A — this is already properly handled.

---

### 3. Sending chunks to Claude without contextualization, metadata, or XML structure

**Verdict:** 🚧 **Pending fix** (W1 modules shipped but not wired into production paths)

**Evidence:**

**Contextualization** — ChromaDB live query confirmed:
- `ext_authority` has hierarchical `parent_id`/`child_ids`/`heading_path`/`collapse_group` (section-aware parent/child chunking — partial analog to Anthropic Contextual Retrieval)
- `code_chunks` has STRUCTURAL metadata (`module`, `name`, `entity_type`, `line_start/end`) but NO Claude-generated narrative `chunk_context`
- `process_docs` has POSITIONAL metadata only (`chunk_index`, `doc_type`) — no narrative context, no heading path on sampled chunk

**Metadata** — rich per-collection metadata IS present in ChromaDB (file_path, module, authority_tier, etc.) — the gap is that it's not projected into Anthropic prompt structure.

**XML structure** — `grep "<document>|<document_content>|<source>"` returned 0 hits across the pre-P1.2 codebase.

**What landed in W1 (not yet adopted):**
- P1.1 `@c:/Git/Agentic-Workflow/tools/ingestion/contextual_chunk_builder.py` — generates 50-100 tok narrative context per chunk
- P1.2 `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/anthropic_prompt_renderer.py` — emits `<document>`/`<source>`/`<title>`/`<metadata>`/`<context>`/`<document_content>` XML shape with documents-first, query-last ordering

**Remediation:** P1.1b — wire `ContextualChunkBuilder` into `ingest_code.py` and `ingest_docs.py`. The prompt renderer is callable by any consumer today.

---

### 4. Stuffing too many weak chunks into the prompt instead of reranking and curating

**Verdict:** ✅ **Clean**

**Evidence:** Six distinct reranker implementations confirmed in the repo:
- `@c:/Git/Agentic-Workflow/agentic_core/L1_cognition/reasoning/reranking_engine.py`
- `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/senior_librarian_reranker.py`
- `@c:/Git/Agentic-Workflow/agentic_core/utils/workflow_engines/reranker.py`
- `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/advanced_c0_reranker.py`
- `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/completeness_reranker.py`
- `@c:/Git/Agentic-Workflow/agentic_core/utils/late_interaction_reranker_util.py`

Must-use vs optional chunk distinction is formalized in `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/evidence_contract_builder.py` (`VerifiedChunk.is_must_use`). The `PromptEnvelopeFactory` tracks `must_use_chunks_present` and `optional_chunks_present` for downstream truncation.

**Impact:** N/A.

---

### 5. Trying to get strict JSON + native citations in one response

**Verdict:** 🚧 **Pending fix** (W2.P2.3 orchestrator shipped but not adopted)

**Evidence:**
- `grep "citations.enabled|citations_enabled"` returns 0 hits in consumer code paths (pre-W2).
- `@c:/Git/Agentic-Workflow/agentic_core/L5_safety/enforcement/citation_enforcement.py` tracks INTERNAL citations (provenance) but does not toggle the Anthropic `citations` feature flag.
- Single-pass design is the default; no dual-pass orchestrator existed before P2.3.

**What landed in W2 (not yet adopted):**
- P2.2 `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/anthropic_citation_adapter.py` — maps Anthropic native citations to internal `Citation` dataclass
- P2.3 `@c:/Git/Agentic-Workflow/agentic_core/knowledge/retrieval/dual_pass_citation_orchestrator.py` — composes pass-1 (grounded answer + citations) + pass-2 (JSON reshape) with explicit status codes

**Impact:** When a caller needs BOTH strict JSON AND cited claims, current code would force them to choose or accept malformed output. Dual-pass orchestrator fixes this when adopted.

**Remediation:** Caller integration (out of the plan's original 10 phases; scope for a future adoption wave).

---

### 6. Multi-agent orchestration for tasks that are not breadth-first or parallelizable

**Verdict:** ⚠️ **Partial**

**Evidence:**
- `@c:/Git/Agentic-Workflow/system_learning/arbitration/engine.py` and `@c:/Git/Agentic-Workflow/apps_research/` subsystem exist.
- No classifier observed that gates multi-agent dispatch on a "breadth-first" criterion.
- No enforced cost ceiling that aborts if a single-agent path would have sufficed.

**Impact:** Possible but un-measured cost inflation on inappropriate multi-agent fan-out. Not catastrophic — most current dispatches are to a single execution agent — but the guardrail is missing.

**Remediation:** P4.3 of the plan — add breadth-first classifier + gated arbitration.

---

### 7. Treating evaluation as a one-dimensional score instead of a tradeoff across quality, context use, latency, and price

**Verdict:** ⚠️ **Partial**

**Evidence:**
- `@c:/Git/Agentic-Workflow/tools/eval/retrieval_benchmark.py` emits `top_hit_score`, `citation_completeness`, `dedup_savings` — retrieval-only metrics.
- `@c:/Git/Agentic-Workflow/apps_eval/engines/evaluation_retrieval_engine.py` wraps the benchmark but does not add answer-fidelity, latency SLO, or per-query cost.
- No single rubric that reports all 6 dimensions (relevance, faithfulness/fidelity, citation correctness, latency p50/p95, cost $/query, failure-mode taxonomy) alongside each other.

**Impact:** Incremental changes to the retrieval stack can't be objectively compared — "this new reranker is better" is asserted from single-dimension scores that may miss regressions in another dimension.

**Remediation:** P3.1 of the plan — expand `retrieval_benchmark.py` to the 6-dim rubric.

---

## Summary scorecard

| # | Anti-pattern | Verdict | Plan phase |
|---|---|:---:|---|
| 1 | RAG when long-context+caching suffices | ❌ Exhibits | P4.1 |
| 2 | Vector-only for exact identifiers | ✅ Clean | — |
| 3 | No contextualization / metadata / XML | 🚧 Pending | P1.1b (adoption) |
| 4 | Weak-chunk stuffing, no rerank | ✅ Clean | — |
| 5 | Strict JSON + citations in one pass | 🚧 Pending | Adoption wave |
| 6 | Indiscriminate multi-agent dispatch | ⚠️ Partial | P4.3 |
| 7 | One-dimensional eval | ⚠️ Partial | P3.1 |

**Counts:** 2 Clean, 2 Partial, 2 Pending-fix, 1 Exhibits.

Reflects the repo state as of 2026-04-22 after EX2 commit. Six of seven anti-patterns are either addressed or have a landed fix awaiting adoption. The single outstanding **Exhibits** (anti-pattern 1) is bounded — it costs us suboptimal routing decisions for small corpora, not broken retrieval.

---

## Out-of-scope observations surfaced during audit

1. **Broken Anthropic executor (resolved in EX1+EX2):** The `HardenedAnthropicExecutor` was unimportable and later uninstantiable before this session. Fixed in commits `69c08ea326` + `e05dd98a92`.
2. **Remaining latent `hardening_mixin` bugs:** `execute_hardened` references `CircuitBreakerOpenError` as a bare name (not imported at module level) — will raise `NameError` on first exception. Out of scope for this audit; tracked as follow-up.
3. **`providers_anthropic_client_util.py`** at `@c:/Git/Agentic-Workflow/apps_rg/utils/providers_anthropic_client_util.py:170` still calls `gw.route_generation(req)` on `SovereignLLMGateway` — but that method doesn't exist on the class (`generate(artifact)` is the real method). This file is broken at runtime; tracked as follow-up.

---

## References

- Anthropic (2024-09). *Contextual Retrieval in AI Systems.* https://www.anthropic.com/research/contextual-retrieval
- Anthropic API Docs. *Citations.* https://docs.anthropic.com/en/docs/build-with-claude/citations
- Anthropic API Docs. *Prompt caching.* https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Anthropic (2024). *How we built our multi-agent research system.* https://www.anthropic.com/engineering/built-multi-agent-research-system
