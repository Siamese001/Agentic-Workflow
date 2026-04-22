# Anthropic RAG Best Practices — Gap Analysis & Wave Queue

**Plan ID:** `anthropic-rag-gaps-7f3c2a`
**Status:** Draft v2 (analysis-only; no code edits) — revised 2026-04-22 after ChromaDB inspection
**Tier:** T3 (cross-layer, >5 files)
**Source doc:** `docs/reference/03_L0_Routing/C0 - Retrieval/Anthropic RAG Best Practices.md`
**ADG Provenance:** backend=sqlite, snapshot=`adg_indexed_04222026_1508.sqlite` (nodes=72,701, edges=541,914)
**ChromaDB state:** 11 collections (9 production + 2 test residue), all BAAI/bge-m3 1024-dim cosine
**Date:** 2026-04-22

---

## Executive Summary

The repo already has a **mature hybrid-retrieval + rerank stack** (BM25 + dense + multiple rerankers + eval harness). The gaps versus Anthropic's 2024–2025 best-practice pattern are **concentrated on the Claude-API-facing boundary**: Anthropic-specific prompt-caching, native citations, XML document shape, Contextual Retrieval chunk-context preprocessing, and the full-context-vs-RAG size gate. Retrieval infrastructure gaps are minor.

**Recommendation:** Execute Wave 1 (Contextual Retrieval + XML prompt shape) and Wave 2 (Anthropic cache_control + native citations) as highest leverage. Defer Wave 3 (eval rubric expansion) and Wave 4 (multi-agent research + thinking) until 1–2 land.

---

## ChromaDB Inventory (DIRECTLY OBSERVED — live query 2026-04-22)

| Collection | Purpose | Key Metadata Fields Observed | Notes |
|---|---|---|---|
| `code_chunks` | Entity-level functions/classes + file chunks | `module`, `name`, `entity_type`, `line_start/end`, `chunk_type`, `docstring`, `file_path`, `layer`, `canonical_digest`, `has_sparse` | Structural context present. `has_sparse: false` on sampled chunk is misleading: `ingest_code.py:417-424` explicitly populates BM25 store post-ingest. |
| `process_docs` | Markdown docs: guides, rules, specs, SVP, reference | `file_path`, `chunk_index`, `doc_type`, `layer`, `canonical_digest` | Positional context only — no section/heading path on sampled chunk. |
| `ext_authority` | Vetted external authority (Lane A + B) — Anthropic docs live here | `heading_path`, `parent_id`, `child_ids`, `topic_bucket`, `collapse_group`, `authority_tier`, `source_band`, `title`, `source_url` | **Section-aware parent/child chunking already implemented** (collection metadata says so; `parent_id`/`child_ids` observed). This is the closest existing analog to Contextual Retrieval. |
| `ext_raw` | Unvetted scraped external knowledge | same schema as ext_authority | `invalid_for_normative_use=True` flag — not used in normative retrieval. |
| `repo_evidence` | Wave B: repo evidence (Lane C+D) | — | `invalid_for_normative_use=True`. |
| `runtime_evidence` | Agent traces, healing records, RCAs | — | — |
| `symbols` | Modules/functions/classes from ADG | `source: adg_sqlite` | — |
| `incidents_rca` | Post-mortems, RCAs | — | — |
| `tests_guardrails` | Test functions + safety layer + policy docs | — | — |
| `test_col`, `dupe_col` | Test residue — cleanup candidate | — | Not production data. |

**Key revision:** The repo already does section-aware parent/child chunking on `ext_authority`, and BM25 is populated during code ingestion via `agentic_core/L4_state/utils/memory/bm25_store.py`. The Contextual Retrieval gap is narrower than v1 stated — the missing piece is specifically **Claude-generated 50–100-token narrative context** prepended to each chunk BEFORE embedding, which Anthropic's research shows reduces failed retrievals by 49% on top of BM25+dense hybrid.

---

## Methodology

Each of the 11 blueprint items from the source doc was mapped to current repo surfaces via ADG SQLite queries, ChromaDB live queries, and targeted greps. Each row below is classified as:

- **DIRECTLY OBSERVED** — repo has compliant implementation (may need tuning, not building)
- **PARTIAL** — primitive exists but missing Anthropic-specific shape
- **UNRESOLVED** — no evidence of implementation
- **N/A** — not applicable to this repo

---

## Gap Matrix

| # | Anthropic Best Practice | Repo Surface(s) | Classification | Evidence |
|---|---|---|---|---|
| 1 | Full-context + prompt caching decision gate (skip RAG if corpus ≤200k tokens) | None observed | **UNRESOLVED** | `grep "token.*threshold\|corpus_size\|full_context"` returns no gate before RAG entry; `AdaptiveretrievalgateStrategy.py` gates on query, not corpus size. |
| 2 | Contextual Retrieval (Claude-generated 50-100 tok chunk context prepended) | Partial analog: `ext_authority` parent/child + `heading_path`; NOT present on `code_chunks`, `process_docs`, or other production collections; no Claude-generated narrative context anywhere | **PARTIAL** | ChromaDB live query confirmed `ext_authority` carries `parent_id`/`child_ids`/`heading_path`/`collapse_group` — section-aware hierarchical chunking. But: (a) `code_chunks` uses only structural metadata (module/name/line ranges), (b) `process_docs` uses only positional `chunk_index`, (c) no collection has a Claude-generated narrative `chunk_context` field. Anthropic's approach adds narrative grounding that structural/hierarchical metadata alone does not provide. |
| 3a | BM25 lexical retrieval + populated at ingest | `agentic_core/L4_state/memory/bm25_store.py`, `L4_state/memory/semantic/bm25_scorer.py`; ingestion wiring at `tools/ingestion/ingest_code.py:417-424` | **DIRECTLY OBSERVED** | Full BM25 (k1=1.5, b=0.75) + `get_bm25_store().add_documents(bm25_docs)` called after chunk embedding. Not lazy rebuild — populated inline. |
| 3b | Hybrid (dense + BM25 + fusion) retrieval | `L3_orchestration/reasoning/engines/hybrid_search_engine.py`, `search_fusion_engine.py`, `knowledge/retrieval/hybrid_recall_stage.py` | **DIRECTLY OBSERVED** | `HybridSearchResult` dataclass with `vector_score`, `lexical_score`, `combined_score`; 24+10+10 matches. |
| 3c | Broad recall → rerank narrowing | `agentic_core/L1_cognition/reasoning/reranking_engine.py`, `knowledge/retrieval/senior_librarian_reranker.py`, `utils/workflow_engines/reranker.py`, `advanced_c0_reranker.py`, `completeness_reranker.py`, `late_interaction_reranker_util.py` | **DIRECTLY OBSERVED** | 6 distinct reranker implementations. |
| 4 | Prompt shape: documents-first, query-last, XML `<document>`/`<source>` tags | None | **UNRESOLVED** | `grep "<document>\|<document_content>\|<source>"` → 0 hits. `PromptTemplate.py` builds prompts but no XML document wrapper. |
| 5a | Anthropic native `citations` (plain text + chunk) | `citation_enforcement.py`, `ProvenancetrackerStrategy.py` enforce **internal** citation policy | **PARTIAL** | 13+12 matches cover provenance tracking of retrieved chunks, but no `citations.enabled=True` passed to Anthropic Messages API. |
| 5b | `search_result` content blocks | None | **UNRESOLVED** | `grep search_result.*block` → 0 hits. |
| 6 | Two-pass design for strict JSON + citations incompatibility | None observed; `output_schema_validator.py` validates JSON but no dual-pass pipeline | **UNRESOLVED** | No orchestration that runs a grounded-answer-with-citations pass followed by a JSON-shaping pass. |
| 7 | `cache_control` on static prefix (tool defs, system, context, examples) | `prompt_artifact_cache.py`, `prompt_loader.py` (internal disk cache, NOT Anthropic API field) | **UNRESOLVED** | `grep cache_control\|anthropic.*cache\|ephemeral` on .py → 0 matches on Anthropic cache_control field. 4 files reference caching but none mark `cache_control: ephemeral` on request bodies. `HardenedanthropicexecutorStrategy.py` (11 Anthropic API matches) does not pass cache markers. |
| 8a | Extended/adaptive thinking for multi-step tool use | `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py`, `apps_rg/utils/providers_anthropic_client_util.py` | **PARTIAL** | Anthropic client present; unclear if `thinking` param used — needs verification (not observed in 11-match sample). |
| 8b | Interleaved thinking block preservation across tool turns | Needs verification | **UNRESOLVED (pending audit)** | Would surface in executor loop; no observed handling. |
| 9 | Model tier selection (cheap for contextualization, strong for synthesis) | `apps_shared/types/model_router_types.py`, `sovereign_mcp_router.py` | **PARTIAL** | Router exists but no explicit Anthropic tier policy "Haiku for chunk-context, Opus for synthesis". |
| 10 | Multidimensional eval (relevance, fidelity, citation correctness, latency, cost) | `tools/eval/retrieval_benchmark.py`, `apps_eval/engines/evaluation_retrieval_engine.py` | **PARTIAL** | Benchmark covers top_hit_score, citation_completeness, dedup_savings — missing explicit **answer fidelity to source**, **latency SLO**, **per-query cost**. |
| 11 | Multi-agent breadth-first research | `system_learning/arbitration/engine.py`, `apps_research/` | **PARTIAL** | Arbitration + research engines exist; no observed orchestrator–subagent pattern gated on "breadth-first only" criterion. |
| 12 | Anti-pattern audit against the 7 listed | — | **UNRESOLVED (audit not run)** | Deliverable of Wave 3. |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1** | P1.1, P1.2 | **Contextual Retrieval ingestion + XML prompt shape** | 18,000 | Claude Haiku available; ingestion is offline batch; prompt caching applied to source doc during chunk-context generation per Anthropic cookbook | Todo | Every new chunk in `code_chunks`/`process_docs` carries a `chunk_context` field; prompt assembler wraps docs in `<document>/<source>` tags with query-last order. |
| **W2** | P2.1, P2.2, P2.3 | **Anthropic API surface: cache_control + native citations + 2-pass JSON** | 14,000 | `apps_rg/.../HardenedanthropicexecutorStrategy.py` is the single Anthropic entry point; citations feature flag gated per-caller | Todo | `cache_control=ephemeral` on static prefix verified in request bodies; `citations.enabled=True` feature-flagged; dual-pass citation→JSON pipeline wired where strict schema required. |
| **W3** | P3.1, P3.2 | **Eval rubric expansion + anti-pattern audit** | 9,000 | `retrieval_benchmark.py` is extensible; anti-pattern audit is doc-only | Todo | `retrieval_benchmark.py` emits 6-dim scorecard (relevance, fidelity, citation, latency, cost, failure-modes); audit report filed under `docs/reports/plans/`. |
| **W4** | P4.1, P4.2, P4.3 | **Full-context gate + model-tier policy + multi-agent criterion** | 11,000 | Token counting uses Anthropic tokenizer; model router already has tier abstraction | Todo | `AdaptiveretrievalgateStrategy` routes ≤200k-token corpora to full-context path with caching; router enforces Haiku-for-contextualization policy; multi-agent only fires on breadth-first classifier. |

**W1 token budget:** 18,000 🟡 (medium — touches ingestion + prompt assembly)
**W2 token budget:** 14,000 🟢
**W3 token budget:** 9,000 🟢
**W4 token budget:** 11,000 🟢

Token estimation deferred to W1 kickoff (run `python tools/utils/planning/token_estimator.py` at that time; UNRESOLVED for now, acceptable because plan is analysis-only per user scope selection).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | Contextual chunk-context preprocessor (Claude-generated narrative context) | new: `tools/ingestion/contextual_chunk_builder.py`; mods: `tools/ingestion/ingest_code.py`, `ingest_docs.py`, `ingest_runtime.py`, `knowledge/canonical/chunk_manifest.py` | Claude rate limits during bulk ingest; MUST use prompt-caching on source document per Anthropic cookbook (makes per-chunk context affordable). Ingestion is idempotent via `canonical_digest` — re-ingestion only regenerates context for new/changed chunks. Scope: start with `process_docs` + `code_chunks` (ext_authority already has hierarchical context via parent/child chunking — lower priority). | 10,000 | Todo |
| **P1.2** | XML document prompt assembler | mods: `apps_research/types/PromptTemplate.py`, `apps_exec/types/PromptTemplate.py`, `knowledge/retrieval/prompt_envelope.py` | Must preserve citation-boundary guarantee; query must appear AFTER all `<document>` blocks | 8,000 | Todo |
| **P2.1** | `cache_control` on static prompt prefix | mods: `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py`, `apps_rg/utils/providers_anthropic_client_util.py`, `apps_rg/utils/agent_executor_util.py` | Must identify stable prefix boundary per call site; 5-min vs 1-hour TTL choice per workflow | 5,000 | Todo |
| **P2.2** | Native Anthropic citations wiring | same files as P2.1 + new `agentic_core/knowledge/retrieval/anthropic_citation_adapter.py` | Must map Anthropic citation responses back to internal `provenance_confidence` schema | 5,000 | Todo |
| **P2.3** | Two-pass citations+JSON orchestrator | new: `agentic_core/knowledge/engine/dual_pass_citation_orchestrator.py`; consumer update in `prompt_governance/security/validators/output_schema_validator.py` | Preserve audit trail across both passes; second pass must not re-query retrieval | 4,000 | Todo |
| **P3.1** | 6-dim retrieval eval rubric | mods: `tools/eval/retrieval_benchmark.py`, `apps_eval/engines/evaluation_retrieval_engine.py` | Need latency & cost instrumentation hooks in executor | 5,000 | Todo |
| **P3.2** | Anti-pattern audit report | new: `docs/reports/plans/anthropic-rag-antipattern-audit.md` | ADG-driven file enumeration against 7 anti-patterns from source doc | 4,000 | Todo |
| **P4.1** | Corpus-size gate (skip RAG ≤200k tok) | mods: `apps_shared/enforcement/AdaptiveretrievalgateStrategy.py`, new `tools/retrieval/corpus_size_estimator.py` | Tokenizer parity with Anthropic; requires full-corpus token count caching | 4,000 | Todo |
| **P4.2** | Model-tier policy for Anthropic | mods: `apps_shared/types/model_router_types.py`, `sovereign_mcp_router.py` | Backward compat with existing routing keys | 3,000 | Todo |
| **P4.3** | Multi-agent breadth-first criterion | mods: `system_learning/arbitration/engine.py`, new `agentic_core/L3_orchestration/reasoning/breadth_first_classifier.py` | Must gate multi-agent cost explosion; classifier needs eval | 4,000 | Todo |

---

## ADG_HOTSPOT_REPORT

**Scope:** Files most at-risk when W1–W2 land, ranked by fan-in × layer multiplier.

| Rank | File | Layer | Mult | Est. Fan-In (imports) | Archetype | Surfaces Touched | Impact |
|---|---|---|---|---|---|---|---|
| 1 | `apps_rg/enforcement/HardenedanthropicexecutorStrategy.py` | L5 | ×2.0 | TBD (query at W2 kickoff) | SAFETY_GATEKEEPER | Execution, Security, Observability | Highest — single Anthropic entry point |
| 2 | `agentic_core/knowledge/retrieval/prompt_envelope.py` | L1 | ×1.0 | TBD | CENTRAL_DEPENDENCY | Execution | High — assembles prompts for many callers |
| 3 | `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` | L3 | ×1.75 | TBD | ORCHESTRATOR | Execution, State | Medium — reranker changes route through here |
| 4 | `tools/ingestion/ingest_code.py` | (tools) | ×1.0 | TBD | CENTRAL_DEPENDENCY | Write (to vector store) | Medium — ingestion pipeline fan-in |
| 5 | `apps_shared/enforcement/AdaptiveretrievalgateStrategy.py` | L5 | ×2.0 | TBD | SAFETY_GATEKEEPER | Execution, Security | Medium — gates whether RAG runs at all |

Full fan-in ranks to be populated at wave kickoff via `adg_edge_fanin(relation_type="imports")`.

---

## ADG_GRAPH_LAYER_EVIDENCE

Materialized views and P-views relevant to this plan (to be queried at wave kickoff):

1. `mv_graph_reverse_dependency_hotspots` — confirm rank-1 HardenedanthropicexecutorStrategy fan-in before modifying its signature.
2. `mv_graph_chokepoint_bridges` — identify whether `prompt_envelope.py` is a chokepoint between retrieval and prompt assembly.
3. `mv_dependency_cone_risk` — size of blast radius for XML-wrap change in `PromptTemplate.py` (apps_research + apps_exec both import it).
4. `v_p1_mis_layered_infra` — verify no new mis-layer introduced by `anthropic_citation_adapter.py` (knowledge layer calling L5 Anthropic executor).
5. `v_p2_duplicated_adapters` — confirm proposed `dual_pass_citation_orchestrator.py` does not duplicate existing orchestrator patterns.

**Semantic edges used (planned):** `resolves_callsite` for Anthropic client invocations; `writes_to` for chunk_context field on vector store; `flows_to` for citation propagation across the dual-pass boundary.

---

## Dependencies Between Waves

- W1.P1.1 → W2.P2.1 (contextual chunks must exist before cache_control-marked prefix is stable)
- W1.P1.2 → W2.P2.2 (XML shape must land before native citations wire through the same template)
- W2.P2.1+P2.2 → W2.P2.3 (dual-pass depends on both cache + citations being wired)
- W3 and W4 independent of W1/W2 and may run in parallel after W1.P1.2 lands

---

## Risks & Open Questions (UNRESOLVED)

1. **Tokenizer parity** — Anthropic's tokenizer differs from tiktoken; P4.1 needs `anthropic.count_tokens` wiring. **UNRESOLVED** until wave kickoff.
2. **Prompt cache billing** — 1.25× write cost, 0.1× read cost. Needs cost-model update in P3.1 eval rubric.
3. **Contextual Retrieval cost at scale** — source doc notes prompt caching is what makes it cheap. Must verify current Anthropic client supports caching on input document across many chunk-contextualization calls.
4. **Existing provenance schema compatibility** — `ProvenancetrackerStrategy.py` has its own citation format. P2.2 adapter must be lossless both directions.
5. **Model router backward compat** — P4.2 tier policy must not break existing callers that request a specific model by name.

---

## Non-Goals

- Building a new vector store (ChromaDB stays)
- Replacing any existing reranker (all 6 stay)
- Migrating off internal `prompt_artifact_cache.py` (complements Anthropic `cache_control`, not replaces)
- Removing existing `citation_enforcement.py` (native citations become an input to it, not a replacement)

---

## Next Action

User selects which wave to execute next. Recommended: **W1** (highest retrieval quality impact per the 49%/67% failed-retrieval reductions Anthropic cites) or **W2** (lowest risk, single-file-cluster scope). W3 is viable as a parallel-track "understand before we change" wave if preferred.
