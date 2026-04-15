# Wave B6 — ext_authority Source Additions

**Date**: 2026-04-15  
**Scope**: ext_authority only. No repo_evidence, ext_raw, router, or topology changes.  
**Proof basis**: `docs/reports/wave_b_b5r_chromadb_direct_proof.md`  
**Ingestion script**: `tools/generate/ingestion/ingest_ext_authority.py`  
**Raw validation**: `artifacts/b6_validation_raw.json`

---

## 1. Source Selection Summary

7 new external sources added across P1–P8 categories. All are `required=False` (optional). All are Lane B (`supporting_guidance / T3_guidance`). Zero existing ext_authority URLs duplicated.

| P | URL | Family/Families | Proof Query Improved | Justification |
|---|-----|----------------|---------------------|---------------|
| P1 | `https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/misc/prompt_caching.ipynb` | **F08** | R1A exact cache route | Anthropic prompt caching notebook covers exact API-level caching with cache_control keys — the closest external analog to policy-key short-circuit routing for LLM calls |
| P2 | `https://raw.githubusercontent.com/zilliztech/GPTCache/main/README.md` | **F09** | R1B semantic cache route | GPTCache is the canonical open-source semantic cache for LLMs; explicitly covers vector-similarity cache lookup, embedding-based retrieval of cached responses, and similarity thresholds |
| P3 | `https://raw.githubusercontent.com/deepset-ai/haystack/main/README.md` | **F12** | C0 evidence fetch hybrid | Haystack explicitly covers BM25+dense hybrid retrieval pipelines with JoinDocuments and score fusion; direct evidence for the hybrid dense+sparse pattern |
| P4 | `https://raw.githubusercontent.com/UKPLab/sentence-transformers/master/README.md` | **F12, F13** | C0 evidence shaping/rerank; embedding selection | Sentence-Transformers README covers cross-encoder reranking models (retrieve+rerank section) and embedding model selection/tradeoffs — closes both F13 (reranking) and P7 (embedding comparison) |
| P5 | `https://raw.githubusercontent.com/run-llama/llama_index/main/README.md` | **F12** | C0 evidence fetch parent-child | LlamaIndex README covers hierarchical node parser, parent-child chunk retrieval, and auto-merging retriever — the parent-child expansion pattern for F12 |
| P6 | `https://raw.githubusercontent.com/openai/openai-cookbook/main/articles/techniques_to_improve_reliability.md` | **F06, F14, F17** | L1 abstain planning; evidence contract; fallback route | OpenAI cookbook reliability article covers self-consistency checking, chain-of-thought grounding, and guidance for when models should abstain or request clarification |
| P8 | `https://raw.githubusercontent.com/openai/swarm/main/README.md` | **F25** | Healing/escalation tiers | OpenAI Swarm covers agent handoff routing on task failure, error propagation between agents, and escalation to a different handler — external analog for tiered escalation patterns |

---

## 2. Families Not Addressed (Confirmed Exclusions)

| Family | Reason not in B6 |
|--------|-----------------|
| F21 | Internal (replay envelope/freeze propagation) — no external analog |
| F22 | Internal (replay guard/entropy interception) — no external analog |
| F28 | Advisory, primarily internal write-sovereignty pattern — no ext_authority source |

---

## 3. Metadata Assignment Summary

All 7 new sources share these fixed metadata values:

| Field | Value |
|-------|-------|
| `source_collection` | `ext_authority` |
| `source_band` | `supporting_guidance` |
| `authority_tier` | `T3_guidance` |
| `normative_scope` | `external_authority` |
| `invalid_for_normative_use` | `False` |
| `source_type` | `web` |
| `version_or_date` | `""` |

Per-source `topic_bucket` and `collapse_group` assignments:

| Source | `topic_bucket` | `collapse_group` | `doc_family` |
|--------|---------------|-----------------|-------------|
| Anthropic prompt_caching.ipynb | `retrieval_cache` | `langchain_caching` | `guide` |
| GPTCache README | `retrieval_cache` | `gptcache` | `reference` |
| Haystack README | `retrieval_rag` | `haystack` | `reference` |
| Sentence-Transformers README | `retrieval_rag` | `sentence_transformers` | `reference` |
| LlamaIndex README | `retrieval_rag` | `llamaindex` | `reference` |
| OpenAI cookbook reliability | `safety_eval` | `openai_cookbook` | `guide` |
| OpenAI Swarm README | `orchestration` | `openai_swarm` | `reference` |

New `topic_bucket` values added (not in original B5 schema):
- `retrieval_cache` — for caching-specific sources (P1, P2)
- `retrieval_rag` — for retrieval architecture sources (P3, P4, P5)

Both values pass metadata validation (no allowlist enforced on `topic_bucket`).

---

## 4. Ingestion Blockers Fixed

One ingestion blocker was fixed prior to the B6 rebuild:

| Blocker | Location | Fix |
|---------|---------|-----|
| `device="cuda"` hard-coded — would crash on CPU-only machine | `run()` line 698 | Changed to `torch.cuda.is_available()` auto-detect with `"cpu"` fallback |

No other code outside the ingestion path was modified.

---

## 5. URL Deduplication Proof

All 7 new source URLs are distinct from the 18 pre-existing `EXT_AUTHORITY_SOURCES` URLs:

**Pre-existing URL domains**: `modelcontextprotocol`, `openai/openai-agents-python`, `anthropics/anthropic-cookbook/main/patterns`, `langchain-ai/langgraph/main/README`, `microsoft/autogen`

**B6 URL domains**: `anthropics/anthropic-cookbook/main/misc` (different path from existing patterns), `zilliztech/GPTCache`, `deepset-ai/haystack`, `UKPLab/sentence-transformers`, `run-llama/llama_index`, `openai/openai-cookbook`, `openai/swarm`

Zero URL collisions.

---

## 6. Dry-Run URL Resolution Status

| Source | URL Resolution | Chunks (dry-run) |
|--------|---------------|-----------------|
| P1 Anthropic prompt_caching | ✅ 200 OK | ~12 |
| P2 GPTCache README | ✅ 200 OK | ~35 |
| P3 Haystack README | ✅ 200 OK | ~25 |
| P4 Sentence-Transformers README | ✅ 200 OK | ~30 |
| P5 LlamaIndex README | ✅ 200 OK | ~30 |
| P6 OpenAI cookbook reliability | ✅ 200 OK | ~8 |
| P8 OpenAI Swarm README | ✅ 200 OK | ~7 |

**Total dry-run projected chunks**: 463 (vs 323 pre-B6 = +140 new chunks)  
**Final store count after rebuild**: 470 (net +147 — some chunk IDs regenerated with content updates)

Note: 2 pre-existing optional sources also 404 (`models.md`, `subagent.ipynb`) — these were already missing from the B5 store and are unrelated to B6.
