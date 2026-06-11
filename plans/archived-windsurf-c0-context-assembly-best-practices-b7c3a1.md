---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\c0-context-assembly-best-practices-b7c3a1.md'
original_relative_path: 'c0-context-assembly-best-practices-b7c3a1.md'
source_sha256: 9d058164a3ea3ac8a64b0457c66e8b27f390a9dc97d54d005a427b0fb9c2a79e
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-23'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# C0 Context Assembly — Best-Practice Gap Analysis & Remediation Plan

- **Plan slug**: `c0-context-assembly-best-practices-b7c3a1`
- **Date**: 2026-04-23
- **Tier**: T3 (cross-layer, multi-file, architectural)
- **Status**: Active (narrowed 2026-04-23) — after scope-overlap audit vs prior plan `anthropic-rag-gaps-7f3c2a`, G1/G7/G9/corpus-gate partially superseded. Remaining owned scope: G1-residual (gateway wiring), G2 rerank revival, G3 tool retrieval, G4 JIT, G5 compaction, G6 TreeRAG, G8 eval axes, G10 Context Platform, G11, G12. See §2a.
- **ADG snapshot**: `artifacts/adg/adg_indexed_04232026_2319.sqlite` (see §10)
- **Scope anchor**: `docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md`

---

## 1. Sources consulted

### External (web, 2024–2025)

| Source | Key takeaways distilled |
|---|---|
| Anthropic — *Contextual Retrieval in AI Systems* (2024) | Situate each chunk with LLM-generated context BEFORE embedding + BM25. Reported **-49% retrieval failure**, **-67% with rerank**. Broad pre-fetch (~150) then **rerank to ~20**. Hybrid over vector-only. |
| Anthropic — *Effective Context Engineering for AI Agents* (2025) | Shift from pre-fetch-everything to **just-in-time retrieval** via lightweight identifiers + agent tools. **Compaction**, **structured note-taking**, **tool-result clearing** for long-horizon. Minimal-set prompt discipline. |
| Anthropic — *Long-context prompting* | Documents top, query bottom. XML tags (`<document>`, `<source>`). Ask model to **quote before synthesizing**. Citations ≠ strict JSON → use two-pass. |
| Google — *RAG & Grounding on Vertex AI* | **Hybrid Vector Search** (dense+keyword) now GA. **Grounding high-fidelity mode** returns per-sentence sources + **grounding confidence score**. Dedicated **check-grounding** fact-check service. |
| OpenAI — *Prompt Caching 101/201, GPT-5 prompt engineering* | Auto-cache for prefixes ≥1024 tokens. Static content (tools, instructions, examples) at the **start**. Cache-aware prompt shape is a first-class design surface. |
| RAGFlow — *2025 year-end review: From RAG to Context* | **Decouple Search (small chunks) from Retrieve (large hydrated fragments)** — TreeRAG / PageIndex pattern. Tool-description retrieval is a first-class problem (MCP choice paralysis). Unify RAG + Memory + Tool-retrieval into one **Context Platform**. |

### Internal

- `docs/reference/03_L0_Routing/C0 - Retrieval/C0 Context Engine.md` (target spec)
- `docs/reference/03_L0_Routing/C0 - Retrieval/Anthropic RAG Best Practices.md` (already distilled in repo)
- `docs/reference/03_L0_Routing/C0 - Retrieval/Retrieval Pipeline.md`
- Implementation files inventoried in §2 below.

---

## 2. Current repo state (DIRECTLY OBSERVED)

C0-relevant surface under `agentic_core/knowledge/retrieval/` and neighbors:

| C0 stage | Doctrinal component | File(s) present | Status |
|---|---|---|---|
| C0.1 Plan | Scope + policy + ACL + freshness | `knowledge/retrieval/retrieval_plan.py`, `knowledge/gates/preretrieval_gate.py` | ✅ Implemented |
| C0.1 Corpus gate | Skip-RAG when <200k | `knowledge/retrieval/corpus_size_gate.py` | ✅ Implemented |
| C0.2 Dense | Vector recall (ChromaDB) | `L4_state/utils/memory/in_memory_vector_cache.py`, `tools/mcp/vector_db_server.py` | ✅ Implemented |
| C0.2 Sparse | BM25 | `L4_state/memory/semantic/bm25_scorer.py`, `L4_state/utils/memory/bm25_store.py` | ✅ Implemented |
| C0.2 Hybrid fusion | Dense ⊕ sparse merge | `knowledge/retrieval/hybrid_recall_stage.py`, `L3_orchestration/reasoning/engines/hybrid_search_engine.py`, `L4_state/memory/semantic/hybrid_merger.py` | ✅ Implemented (sparse-wins-on-IDs) |
| C0.3 Graph | GraphRAG traversal | `tools/graphdb/agent_integration/phase2/contextual_engine.py` + `docs/reference/.../GraphRAG/` | ⚠️ Partial — engine exists, integration to C0.4 unclear |
| C0.4 Rerank | Cross-encoder / late-interaction | `knowledge/retrieval/senior_librarian_reranker.py` (5.5 KB), `L1_cognition/.../c0_reranker.py`, `advanced_c0_reranker.py` | ⚠️ Shallow — late-interaction reranker archived 2026-04-23; cross-encoder integration unverified |
| C0.4 Parent-child hydrate | Small-search → large-read | `knowledge/retrieval/parent_child_hydrator.py` | ✅ Scaffold present |
| C0.5 Evidence | Support score + citations | `knowledge/retrieval/evidence_contract_builder.py`, `knowledge/retrieval/anthropic_citation_adapter.py`, `knowledge/retrieval/dual_pass_citation_orchestrator.py` | ✅ Implemented |
| Cache | Version-aware exact + semantic | `knowledge/cache/version_aware_cache.py`, `knowledge/dispatcher/cache_decision_engine.py`, 50+ cache files | ✅ Implemented (exact); semantic cache exists |
| Prompt assembly | XML, docs-first, cache markers | `knowledge/retrieval/anthropic_prompt_renderer.py`, `anthropic_cache_control.py`, `knowledge/retrieval/prompt_envelope.py` | ✅ Anthropic-tuned |
| Eval | Retrieval benchmark | `L3_orchestration/reasoning/engines/retrieval_benchmark.py`, `retrieval_coverage_scorer.py`, `L4_state/utils/memory/retrieval_eval_registry.py` | ⚠️ Partial — coverage exists, missing drift + stale-hit + per-sentence support precision |
| Chunking | Policy engine | `knowledge/chunking/chunk_policy_engine.py`, `chunking_modes.py`, `corpus_classifier.py` | ⚠️ No **situate-before-embed** (contextual retrieval preprocessing) |
| Ingestion | Intake + modality | `knowledge/ingestion/intake_clerk.py`, `visual_detector.py` | ⚠️ No per-chunk contextualizer pass |

### What is already strong

- Full C0.1 pre-filter with fail-closed ACL/tenant/freshness/version binds.
- Hybrid dense+sparse with sparse-wins-on-IDs (matches Anthropic guidance).
- Corpus-size gate (≥200k threshold honored per Anthropic guidance).
- Anthropic-native prompt rendering + prompt-caching + two-pass citation orchestrator.
- Layered cache (L1 exact, semantic, version-aware, graph-aware).

---

## 2a. Scope-overlap reconciliation with `anthropic-rag-gaps-7f3c2a` (2026-04-23)

A prior plan `.windsurf/plans/anthropic-rag-gaps-7f3c2a.md` (dated 2026-04-22) covers substantial overlap. Header of that plan still reads "Draft v2 (analysis-only)" but code has shipped on disk. Reconciliation:

| Concern | Prior plan phase | Shipped code | Status in THIS plan |
|---|---|---|---|
| Contextual Retrieval preprocessor | P1.1 | `tools/ingestion/contextual_chunk_builder.py`, `--contextualize` flag on `ingest_docs.py` & `ingest_code.py`, unit tests | **G1 residual** — see below |
| Anthropic XML prompt shape | P1.2 | `knowledge/retrieval/anthropic_prompt_renderer.py` | Superseded — cross-reference |
| `cache_control` on static prefix | P2.1 | `knowledge/retrieval/anthropic_cache_control.py` | Superseded — cross-reference |
| Native Anthropic citations adapter | P2.2 | `knowledge/retrieval/anthropic_citation_adapter.py` | Superseded — cross-reference |
| Two-pass citations+JSON orchestrator | P2.3 | `knowledge/retrieval/dual_pass_citation_orchestrator.py` | G7 partially superseded — per-sentence support score + check-grounding still new |
| Corpus-size gate | P4.1 | `knowledge/retrieval/corpus_size_gate.py` | Superseded — cross-reference |
| Anthropic model-tier policy | P4.2 | `knowledge/retrieval/anthropic_model_tier_policy.py` | Partially superseded; vendor-agnostic tier policy still new (G9 residual) |

### G1 residual — the precise remaining gap

DIRECTLY OBSERVED in `tools/ingestion/ingest_docs.py:563` and `tools/ingestion/ingest_code.py:472`:

```python
context_builder = ContextualChunkBuilder()        # no gateway= injected
```

`ContextualChunkBuilder.__init__` resolves `enabled` via `bool(ANTHROPIC_API_KEY) and self._gateway_available()`, and `_gateway_available()` returns `self._gateway is not None`. The gateway is never injected at any production call site. Result: `--contextualize` exercises ONLY the `_heuristic_context` path regardless of API key availability. The Claude-generated contextual-retrieval path is shipped code but **unreachable in production**.

**Owned residual scope for this plan**:

1. Build the Anthropic gateway adapter (`_GatewayProtocol` implementation) with prompt caching (`cache_control=ephemeral`) on the `<document>` prefix — this is what the `contextual_chunk_builder.py` header comment promises as "W2.P2.1" in the prior plan but never landed.
2. Wire the adapter into `ingest_docs.py` and `ingest_code.py` behind the `--contextualize` flag so live-Claude context generation becomes reachable.
3. Add `situated_context: str` to `ChunkManifest` (the metadata carries `chunk_context` via `metadata["chunk_context"]` today but is not on the canonical manifest schema).
4. Re-index once; baseline capture runs on the unreached heuristic path first, then on the Claude path, so the ADR-045 acceptance gate is measurable.

### Prior-plan header correction

The `anthropic-rag-gaps-7f3c2a` header will be updated separately to mark P1.1, P1.2, P2.1, P2.2, P2.3, P4.1, P4.2 as Shipped (code), P1.1-residual (gateway wiring) as Owned-by-this-plan, and P3.1/P3.2/P4.3 as still Todo in the prior plan.

---

## 3. Gaps (DIRECTLY OBSERVED vs best practice)

Each gap is scored by **impact** on C0 outcome quality and **reversibility**.

### G1 (residual) — Contextual Retrieval gateway wiring **[P1, high impact]**

**Updated 2026-04-23 after §2a audit.** The preprocessor class and `--contextualize` flag are SHIPPED; the gateway adapter that makes the Claude path reachable was never wired.

**Anthropic headline**: prepend 50–100 token LLM-generated context to each chunk before both embedding and BM25. **-49%/-67% failure reduction**.

**Repo state**:
- `tools/ingestion/contextual_chunk_builder.py` — SHIPPED (254 lines, Haiku-4-5 default).
- `--contextualize` flag on `ingest_docs.py` (line 519) and `ingest_code.py` — SHIPPED.
- 8+ unit tests pass in `tests/unit/tools/ingestion/test_contextual_chunk_builder.py`.
- **GAP**: `ContextualChunkBuilder()` is instantiated at call sites with no `gateway=` argument → `enabled=False` always → heuristic path only. Live Claude contextualization is unreachable in production.

**Owned residual scope**: gateway adapter + wiring + `ChunkManifest.situated_context` field + baseline measurement. See §2a.

### G2 — Rerank depth and quality **[P1, high impact]**

**Anthropic pattern**: broad recall to ~150, rerank to ~20 using a dedicated cross-encoder or late-interaction model.

**Repo state**: `senior_librarian_reranker.py` is 5.5 KB (looks heuristic). `apps_shared/utils/late_interaction_reranker_util.py` was moved to `archives/adg_dead_code/2026-04-23/`. `advanced_c0_reranker.py` / `c0_reranker.py` under L1 ML decision support — integration wiring into C0.4 unverified by ADG fan-in here.

**Why it matters**: without a strong reranker, recall@150 becomes noise at the prompt window. Anthropic cites rerank as the lift multiplier on top of contextual retrieval.

### G3 — No tool-description / skill retrieval rail **[P1, architectural]**

**2025 best practice** (Anthropic context-engineering, RAGFlow, MCP ecosystem): **the set of tools/skills presented to the agent must itself be retrieved**, not statically concatenated. Otherwise large MCP fleets cause "choice paralysis".

**Repo state**: no `*tool*select*.py` hits. `L4_state/cache/tool_embedding_cache.py` exists but appears to be a caching utility, not a retrieval-backed tool-selector.

**Why it matters**: our MCP fleet (12 servers, 100+ tools) is already in choice-paralysis territory. This is a C0-adjacent gap — tool/skill retrieval belongs in the C0 "context assembly" umbrella.

### G4 — Just-in-time / agentic retrieval pattern not explicit **[P2, medium]**

**Anthropic**: hybrid of pre-fetched context + lightweight identifiers the agent dereferences on demand via tools (`glob`, `grep`, file-path refs). Claude Code pattern.

**Repo state**: `context_retrieval_orchestrator.py` bridges L3 to retrieval but the pipeline reads as strictly pre-fetch. No first-class "identifier + dereferencer tool" pattern documented in the C0 spec.

**Why it matters**: for long agent loops we want cheap identifier carry + lazy fetch to avoid context pollution. Current shape loads candidate heaps up front.

### G5 — Compaction + tool-result clearing + structured note-taking absent from C0 **[P2, medium]**

**Anthropic**: long-horizon tasks need compaction (summarize-and-restart), tool-result clearing, and agent-written notes persisted outside the window.

**Repo state**: no compaction stage in C0 spec; tool-result clearing not present in `evidence_contract_builder.py`. Memory MCP exists but is for Cursor Agent's own cross-session recall — not agent runtime compaction inside an app loop.

### G6 — Search/Retrieve granularity decoupling partial (TreeRAG pattern) **[P2, medium]**

**RAGFlow 2025**: embed small (100–256 tok) for precision; hydrate large (1024+ tok or parent subtree) for the LLM.

**Repo state**: `parent_child_hydrator.py` scaffold exists. Chunking modes exist. But there is no explicit **tree/TOC** structure generated at ingest, and no navigation from recalled small chunk to neighboring/parent node during hydration.

### G7 (residual) — Per-sentence grounding + check-grounding pass **[P2, medium]**

**Updated 2026-04-23 after §2a audit.** The dual-pass citation orchestrator and Anthropic citation adapter are SHIPPED by prior plan P2.2/P2.3.

**Google high-fidelity mode**: per-sentence citations, **grounding confidence score**, separate check-grounding service.

**Repo state**:
- `knowledge/retrieval/anthropic_citation_adapter.py` + `dual_pass_citation_orchestrator.py` — SHIPPED.
- `evidence_contract_builder.py` computes aggregate support.
- **GAP (residual)**: per-sentence (not per-chunk) support granularity, numeric grounding-confidence score emitted on the evidence contract, and the post-synthesis check-grounding pass before C6 dispatch.

### G8 — Eval suite coverage incomplete **[P2, measurement]**

**Best-practice eval axes**: Recall@K, MRR/NDCG, citation precision, per-sentence support rate, abstain correctness, stale-hit rate, retrieval drift post-reindex, latency P50/P95, cost per turn.

**Repo state**: `retrieval_benchmark.py` + `retrieval_coverage_scorer.py` exist. Confirm coverage of **citation precision**, **abstain correctness**, **stale-hit rate**, **drift** — likely partial. `retrieval_profile.py` family provides profile-level harness but drift vs new index is not obviously measured.

### G9 — Vendor-agnostic prompt-cache abstraction **[P3, low-medium]**

**OpenAI** auto-caches ≥1024-token prefixes; **Anthropic** requires explicit `cache_control=ephemeral`; **Google** has implicit + explicit.

**Repo state**: Anthropic adapter `anthropic_cache_control.py` SHIPPED by prior plan P2.1. Still missing a vendor-agnostic abstraction so OpenAI and Gemini paths honor the same static-prefix discipline.

### G10 — Memory + RAG + Tool-retrieval unification **[P3, architectural, long-lead]**

**RAGFlow/Theory Ventures 2025 thesis**: unify document RAG, dynamic memory, and tool/skill retrieval into one declarative Context Platform.

**Repo state**: three stores are separate (knowledge/retrieval for docs, `memory` MCP for Cursor Agent, MCP registry for tools). No declarative **ContextAssemblyManifest** that a caller can ship to say "give me context for task X" and have the platform decide the mix.

### G11 — Contextual-retrieval ingest cost discipline (prompt cache on parent doc) **[P2, cost]**

**Anthropic**: contextualization is only affordable because the parent doc is prompt-cached while many chunk contexts are generated from it. Repo does not have an `ingestion/contextualizer.py` that uses `anthropic_cache_control` against the full source doc during chunk-context generation.

### G12 — Deterministic replay for retrieval **[P3, observability]**

Pipeline stamps `replay_key` + `policy_hash` per result (`hybrid_recall_stage.py`). Confirm all downstream stages (rerank, hydrate, evidence contract) carry the key end-to-end so a full C0 run is replayable offline from a single key.

---

## 4. Guiding invariants for remediation (non-negotiable)

1. **No regression of C0.1 pre-filter**: ACL/tenant/freshness/version gates must still run fail-closed.
2. **ADG graph-layer primary**: any refactor MUST emit `## ADG_HOTSPOT_REPORT` + `## ADG_GRAPH_LAYER_EVIDENCE` per constitutional §22.
3. **Anthropic-first compliance** for Claude path (contextual retrieval + two-pass citations + XML tags) — already established; do not weaken.
4. **Vendor parity**: OpenAI and Gemini paths MUST receive equivalent cache-shape and grounding-score contract.
5. **Deterministic replay**: `replay_key` + `policy_hash` propagation end-to-end, including new contextualizer and reranker stages.
6. **No new broad-exception catches** (constitutional §15); guardian exemptions require Author-Gate.

---

## 5. Wave structure

| Wave | Phase IDs | Focus | Est. Tokens (DERIVED) | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W0** | W0.1–W0.3 | Baseline capture + ADR drafts + calibration corpus | 🟢 ~8k | ADG green; Haiku or equivalent available for contextualization LLM | Todo | Baseline eval numbers and 3 ADRs committed; contextualization corpus identified |
| **W1** | W1.1–W1.3 | G1 Contextual Retrieval ingest stage + G11 cost discipline | 🟡 ~25k | Prompt-caching usable at ingest; chunking pipeline accepts a pre-embed hook | Todo | Per-chunk situated context produced; A/B recall@K lifts ≥ +20% on calibration set |
| **W2** | W2.1–W2.2 | G2 Rerank depth (cross-encoder revive) + 150→20 flow | 🟡 ~18k | Cross-encoder model available; archived late-interaction reranker reviewable | Todo | MRR@20 ≥ baseline +15%; latency P95 within 400 ms budget |
| **W3** | W3.1–W3.3 | G6 Tree/hierarchy at ingest + G7 grounding confidence + check-grounding | 🟡 ~22k | Document structure extractor usable; citation adapter extendable | Todo | Per-sentence citations + numeric support score on 100% of answers |
| **W4** | W4.1–W4.2 | G3 Tool/skill retrieval rail + G5 compaction & tool-result clearing | 🟡 ~28k | `tool_embedding_cache.py` repurposable; agent loop exposes compaction hook | Todo | Tool-set for a task comes from retrieval, not static list; long-horizon agent loops show zero context overflow on calibration scenarios |
| **W5** | W5.1–W5.2 | G4 JIT identifier pattern + G10 unified ContextAssemblyManifest | 🔴 ~32k | W1–W4 merged; apps_* can migrate to manifest progressively | Todo | One declarative manifest drives doc/memory/tool retrieval for at least one app (e.g. `apps_research`) |
| **W6** | W6.1–W6.2 | G8 Eval completeness + G12 replay parity + G9 vendor-agnostic cache | 🟢 ~15k | retrieval_benchmark harness extendable | Todo | All eval axes automated in CI; full C0 replay from key validated; OpenAI + Gemini paths honor cache boundaries |

Token legend: 🟢 ≤15k, 🟡 15–30k, 🔴 >30k. Estimates are DERIVED from similar-shape past waves (e.g. `high-wave1-p1-zero-a13f7c`).

---

## 6. Phase-level summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W0.1 | Baseline retrieval eval snapshot | `L3_orchestration/reasoning/engines/retrieval_benchmark.py`, `retrieval_coverage_scorer.py`, new `artifacts/retrieval_baseline/<ts>.json` | Eval harness may not cover all axes; baseline corpus selection; BLOCKED until W0.2 corpus freeze + query population | 3k | Blocked-on-W0.2 |
| W0.2 | Calibration corpus selection | `config/retrieval/calibration_manifest.yaml` (landed, status=draft) | Query set still empty — must be populated and frozen before W0.1 runs | 2k | In-Progress (skeleton landed) |
| W0.3 | ADR drafts (Contextual Retrieval, Rerank, Context Platform) | `docs/architecture/adr/ADR-045-contextual-retrieval.md`, `ADR-046-rerank-revival.md`, `ADR-047-context-platform.md` (all Proposed) | Need sign-off to move from Proposed → Accepted | 3k | Done (Proposed) |
| W1.1 | Add `ingestion/contextualizer.py` with prompt-cached Haiku pass | `knowledge/ingestion/contextualizer.py` (new), `knowledge/chunking/chunking_modes.py` | Batch throughput; failure handling per chunk | 9k | Todo |
| W1.2 | Extend `ChunkManifest` with `situated_context`, re-embed | `knowledge/canonical/chunk_manifest.py`, embedding pipeline | Schema migration; back-compat for old chunks | 8k | Todo |
| W1.3 | Re-index BM25 over contextualized chunks | `L4_state/utils/memory/bm25_store.py` | BM25 corpus rebuild cost | 8k | Todo |
| W2.1 | Revive cross-encoder reranker | `archives/adg_dead_code/2026-04-23/apps_shared/utils/late_interaction_reranker_util.py` → `agentic_core/knowledge/retrieval/cross_encoder_reranker.py`, `senior_librarian_reranker.py` | Model loading; latency; GPU/CPU policy | 12k | Todo |
| W2.2 | Wire 150→20 flow in `hybrid_recall_stage.py` and evidence builder | `knowledge/retrieval/hybrid_recall_stage.py`, `senior_librarian_reranker.py`, `evidence_contract_builder.py` | Backpressure; parallelism | 6k | Todo |
| W3.1 | Ingest-time tree/TOC extractor | new `knowledge/ingestion/tree_extractor.py`, `chunk_manifest.py` parent/sibling refs | Works only on structured docs; heuristic fallback | 8k | Todo |
| W3.2 | Parent-child hydrator TOC navigation | `knowledge/retrieval/parent_child_hydrator.py` | Dedup when small chunks share parent | 6k | Todo |
| W3.3 | Grounding confidence score + check-grounding pass | `knowledge/retrieval/evidence_contract_builder.py`, new `knowledge/retrieval/check_grounding_pass.py`, `anthropic_citation_adapter.py` | Second model call latency; strict JSON compatibility | 8k | Todo |
| W4.1 | Tool/skill retrieval rail | new `agentic_core/knowledge/retrieval/tool_selector.py` backed by `L4_state/cache/tool_embedding_cache.py`; integration with MCP registry + `apps_shared/enforcement/AdaptiveretrievalgateStrategy.py` | Cold-start; tool metadata quality | 16k | Todo |
| W4.2 | Compaction + tool-result clearing hooks | new `agentic_core/L3_orchestration/reasoning/engines/context_compaction.py`; `evidence_contract_builder.py` tool-result lifecycle | Preserve citation provenance across compaction | 12k | Todo |
| W5.1 | JIT identifier pattern primitives | new `agentic_core/knowledge/retrieval/identifier_refs.py`; dereferencer tools at L2 | Safety: agent must not follow unscoped refs | 16k | Todo |
| W5.2 | `ContextAssemblyManifest` declarative shape | new `config/schemas/context_assembly_manifest.schema.json`, new `agentic_core/knowledge/engine/context_platform.py`; migrate `apps_research` | Large blast radius at apps layer; stage behind feature flag | 16k | Todo |
| W6.1 | Full eval axis coverage | `retrieval_benchmark.py`, new `tools/eval/retrieval_drift.py`, new `tools/eval/stale_hit_rate.py`, CI workflow | Golden set labels for citation precision / abstain | 8k | Todo |
| W6.2 | Vendor-agnostic cache + replay parity | new `knowledge/retrieval/vendor_cache_adapter.py`, `anthropic_cache_control.py` refactor to implement adapter; replay-key propagation audit | Vendor-quirk matrix | 7k | Todo |

---

## 7. Exit criteria (gate to close the plan)

- [ ] All 12 gaps have either landed code or a dated deferral with `DEFERRED_SCOPE:` marker.
- [ ] ADR Registry rows for Contextual Retrieval, Rerank Revival, Context Platform (W0.3) — Status=Accepted.
- [ ] Retrieval eval suite shows, on the calibration corpus (vs W0.1 baseline):
  - Recall@20 +20% or better
  - MRR@20 +15% or better
  - Citation precision ≥ 0.9 per-sentence
  - Abstain correctness ≥ 0.95
  - Latency P95 within explicit budget per tenant class
- [ ] Constitutional compliance: §22 graph-layer evidence, §24 deferred-scope markers, §17 memory writeback, no new P1 anti-patterns.
- [ ] At least one app (candidate: `apps_research`) migrated to `ContextAssemblyManifest` end-to-end.

---

## 8. Out of scope for this plan

- Multi-modal (vision/audio) retrieval beyond current `visual_detector.py` usage — separate plan.
- Vector-store swap (ChromaDB → another) — independent migration, do not couple.
- L5 safety overlay on retrieved content — already governed by `L5_safety/enforcement/retrieval/retrieval_safety_gate.py`, no changes here.
- Rewriting L1 semantic cache topology — only admission-gate integration touched in W6.2.

---

## 9. Fact grading

| Claim | Grade | Basis |
|---|---|---|
| G1 (contextual retrieval absent) | DIRECTLY OBSERVED | grep over `agentic_core/knowledge/` for `contextual.{0,20}retriev|situate.{0,20}chunk` returned only Anthropic prompt/cache helpers, no ingest situator |
| G2 (rerank shallow) | DERIVED | `senior_librarian_reranker.py` size 5.5 KB + archived `late_interaction_reranker_util.py`; functional depth needs confirmation with ADG fan-in before W2.1 |
| G3 (no tool retrieval) | DIRECTLY OBSERVED | `find_by_name *tool*select*.py` in `agentic_core` = 0 results |
| G4, G5 (JIT + compaction) | DERIVED | Not found in C0 spec or engine list; confirm via ADG fan-in on `context_retrieval_orchestrator.py` before W4/W5 |
| G6 (tree navigation partial) | DIRECTLY OBSERVED | `parent_child_hydrator.py` present (8.6 KB) but no tree extractor at ingest |
| G7 (grounding score) | UNRESOLVED | `evidence_contract_builder.py` not fully inspected here; verify in W0.1 baseline |
| G8 (eval gaps) | DERIVED | benchmark + coverage scorer exist; completeness of axes needs confirmation in W0.1 |
| G9 (vendor-agnostic cache) | DIRECTLY OBSERVED | only `anthropic_cache_control.py` present |
| G10 (unified platform) | DIRECTLY OBSERVED | three separate retrieval surfaces, no single manifest |
| G11 (ingest cost) | DERIVED | no `contextualizer.py` exists; cost analysis depends on final batch size |
| G12 (replay parity) | UNRESOLVED | verify in W6.2 audit |

UNRESOLVED items MUST be resolved during W0 before the dependent wave executes.

---

## 10. ADG evidence (populated 2026-04-23)

- **Snapshot**: `artifacts/adg/adg_indexed_04232026_2319.sqlite` (regenerated 2026-04-23 23:19)
- **Query tool**: `tools/debug/_c0_plan_hotspot_query.py`
- **Raw output**: `artifacts/retrieval_baseline/c0_plan_hotspots_04232026_2319.txt`
- **ADG Provenance**: backend=sqlite, snapshot=adg_indexed_04232026_2319.sqlite

Impact formula (constitutional §23.d):
`impact = violation_count × (1 + log10(1 + fan_in)) × layer_multiplier`
Layer multipliers: L0/L5 = 2.0, L3/L4 = 1.75, L1/L2 = 1.0, L6 = 0.75, L_PG (knowledge module) treated as 1.0.

## ADG_HOTSPOT_REPORT

All rows observed against the snapshot above. Surfaces per constitutional §23.c (5 ADG surfaces).

| File | Archetype | Layer | Fan-in (imports) | Fan-out (imports) | Violations (P2/LOW) | Impact | Surfaces crossed |
|---|---|---|---:|---:|---:|---:|---|
| `agentic_core/L4_state/utils/memory/bm25_store.py` | STATE_NODE / CHOKEPOINT_BRIDGE | L4 | 9 | 75 | 2 | **7.00** | State, Execution |
| `agentic_core/L3_orchestration/reasoning/engines/retrieval_benchmark.py` | ORCHESTRATOR | L3 | 1 | 6 | 3 | **6.83** | Observability |
| `agentic_core/knowledge/retrieval/parent_child_hydrator.py` | ORCHESTRATOR | L_PG | 1 | 7 | 4 | **5.20** | Execution |
| `agentic_core/knowledge/ingestion/intake_clerk.py` | ORCHESTRATOR | L_PG | 2 | 14 | 2 | **2.95** | State (ingest write) |
| `agentic_core/knowledge/retrieval/anthropic_citation_adapter.py` | CENTRAL_DEPENDENCY | L_PG | 2 | 5 | 1 | **1.48** | Observability |
| `agentic_core/knowledge/retrieval/hybrid_recall_stage.py` | ORCHESTRATOR | L_PG | 1 | 11 | 1 | **1.30** | Execution |
| `agentic_core/knowledge/retrieval/dual_pass_citation_orchestrator.py` | ORCHESTRATOR | L_PG | 1 | 18 | 1 | **1.30** | Observability, Execution |

**Zero-violation but high-fan-in CENTRAL_DEPENDENCY nodes in plan scope** (no impact yet but
any new defect lands amplified — approach with care):

| File | Archetype | Layer | Fan-in | Fan-out | Note |
|---|---|---|---:|---:|---|
| `agentic_core/L3_orchestration/reasoning/engines/hybrid_search_engine.py` | CENTRAL_DEPENDENCY / CHOKEPOINT_BRIDGE | L3 | **16** | 14 | W2.2 modifies — any new violation amplifies ×17 |
| `agentic_core/knowledge/retrieval/prompt_envelope.py` | CENTRAL_DEPENDENCY | L_PG | 8 | 10 | W1/W6 may extend |
| `agentic_core/knowledge/retrieval/evidence_contract_builder.py` | ORCHESTRATOR | L_PG | 6 | 8 | W3.3 modifies (grounding score) |

### P-view membership

**All plan files are CLEAN** across `v_p0_*`, `v_p1_*`, `v_p2_*`, `v_p3_*` views (15 P-views present in snapshot, 0 hits). The C0 surface is not in any architectural-violation backlog today. This is protective — wave execution must not introduce new P-view rows.

### Posture summary

- **Global hotspot rank**: C0 files are NOT present in `mv_hotspot_centrality`, `mv_graph_reverse_dependency_hotspots`, `mv_graph_critical_path_blast_radius`, `mv_dependency_cone_risk`, `mv_path_criticality_rollup`, `mv_debt_concentration_hotspots` (top-K cutoffs filter them out). C0 is **not a repo-wide hotspot**.
- **Local chokepoints exist** (bm25_store, hybrid_search_engine) — must not be weakened.
- **All active violations are P2/LOW antipatterns** (14 total across 7 files). W1–W6 MUST NOT increase this count; every guardian exemption requires Author-Gate approval per §constitutional 8.

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized views cited (≥3 required by §22)

| View | Status for plan scope | What it proves |
|---|---|---|
| `mv_graph_chokepoint_bridges` | 2 hits: `bm25_store.py`, `hybrid_search_engine.py` | Both are bridges whose removal fragments the module graph — any W1/W2 change to them MUST preserve bridge role. Specifically: BM25 re-index (W1.3) is schema-compatible additive; senior_librarian_reranker delegation (W2.1) must keep `HybridRecallStage → reranker` edge intact. |
| `mv_graph_reverse_dependency_hotspots` | 0 hits for plan files | C0 files do not hit the top-K reverse-dep list — no centrality surprise landing W1 code. |
| `mv_graph_critical_path_blast_radius` | 0 hits for plan files | Edits to the C0 surface do not propagate along a critical path. |
| `mv_hotspot_centrality` | 0 hits | Confirms no C0 file is a global centrality hotspot. |
| `mv_dependency_cone_risk` | 0 hits | No upstream cone risk on changes. |
| `mv_debt_concentration_hotspots` | 0 hits | No concentrated debt in C0 scope. |
| `mv_exemptions_near_critical_paths` | 0 hits | No guardian exemptions adjacent to critical paths here. |

### Semantic edges relied on

Plan scope uses these non-trivial edge relations (from `edges.relation_type` in the snapshot):

- `imports` — all fan-in/fan-out above derived from this relation.
- `calls` — present in edges but recorded at 0 for plan files (call resolution is currently import-anchored in this snapshot); runtime call-graph analysis at W2/W3 must not assume zero callers means zero runtime usage.
- `flows_to`, `emits_side_effect`, `resolves_callsite`, `reads_through` — present in the edge model (`[('resolves_callsite', 56490), ('emits_side_effect', 30542), ...]` from regen log). W2.1 and W3.3 will emit new `emits_side_effect` edges for the cross-encoder model load and check-grounding pass respectively; both require `# guardian:` annotations with specific justifications if they cannot be narrowed.

### P-view cross-reference

All 15 P-views in the snapshot were queried against all 21 plan files. **Zero hits.** No file in plan scope currently sits in any of:

`v_p0_apps_direct_infra`, `v_p0_write_bypass_uwg`, `v_p1_mis_layered_infra`, `v_p1_zero_caller_infra`, `v_p1_not_on_spine`, `v_p2_duplicated_adapters`, `v_p2_mixed_usage`, `v_p3_isolated_experimental`, `v_p3_*` (11 additional).

### Wave-ordering rationale from ADG

- **W1 (Contextual Retrieval)** writes to `bm25_store` (STATE_NODE, L4, impact 7.00) and `chunk_manifest` (6 fan-in). Schema migration MUST be additive — no breaking field removal.
- **W2 (Rerank Revival)** writes to `hybrid_search_engine` (L3 CENTRAL_DEPENDENCY, 16 fan-in) and `senior_librarian_reranker` (1 node, 0 fan-in — safe to reshape). The hybrid-search chokepoint is the highest-risk edit surface in the plan.
- **W3 (TreeRAG + Grounding)** writes to `evidence_contract_builder` (6 fan-in ORCHESTRATOR) — additive fields on the evidence contract; downstream consumers on C0.5/C6 must be audited for schema compatibility before W3.3 lands.
- **W4/W5 (Platform + Tool rail)** introduce net-new modules (`context_platform.py`, `tool_selector.py`, `context_compaction.py`) and can be staged behind a feature flag; no direct edits to current chokepoint nodes.

### Rollback posture

- All waves are individually revertible: feature-flag-gated or schema-versioned (new indexes under new `schema_version_bind` per `retrieval_plan.py`).
- If W2 cross-encoder regresses latency, revert path is to restore the heuristic `senior_librarian_reranker` as the sole reranker — `hybrid_search_engine` integration stays intact.
- If W1 degrades retrieval quality, revert path is to point the schema-version bind back at the previous index generation; no ChunkManifest rollback required (additive field is left unused).
