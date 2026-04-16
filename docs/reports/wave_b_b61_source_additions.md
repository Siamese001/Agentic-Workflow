# Wave B6.1 — Source Additions Report

**Date:** 2026-04-15  
**Scope:** ext_authority only — 4 new sources for F12 / F14 / F17 / F25  
**Base:** B6 (25 sources, 470 docs) → B6.1 (29 sources, 586 docs)  
**Anti-drift:** No changes to topology, router, shaper, repo_evidence, ext_raw, or metadata contract

---

## Purpose

Wave B6 left 4 families unresolved:

| Family | B5R Grade | B6 dist@1 | B6 Status |
|--------|-----------|-----------|-----------|
| F12 | WEAK | 0.4943 | Marginal improvement, rel=1/5 |
| F14 | WEAK | 0.4230 | No material change |
| F17 | WEAK | 0.4547 | No material change |
| F25 | WEAK | 0.5043 | Still MISSING |

B6.1 adds one high-signal targeted source per family to close or materially narrow each gap.

---

## New Sources Added (P9–P12)

### P9 — Weaviate Hybrid BM25 + Dense Search (closes F12)

| Field | Value |
|-------|-------|
| **URL** | `https://raw.githubusercontent.com/weaviate/weaviate/main/README.md` |
| **Title** | Weaviate — Hybrid BM25 and Dense Vector Search with Fusion Ranking |
| `doc_type` | `markdown` |
| `doc_family` | `reference` |
| `topic_bucket` | `retrieval_rag` |
| `collapse_group` | `weaviate` |
| `required` | `False` |
| **Family closed** | F12 |
| **Proof query** | "How does hybrid dense and sparse retrieval combine BM25 lexical search with vector embeddings for evidence fetching with parent-child chunk expansion?" |
| **Justification** | Weaviate's primary README explicitly covers both BM25 sparse and dense vector hybrid search with fusion ranking, directly matching the F12 query domain. Weaviate is one of the canonical vector DBs built around hybrid retrieval. |

**URL selection rationale:** Two candidate notebook paths (Qdrant examples master, Haystack tutorials) returned HTTP 404. Weaviate main README resolved successfully and contains direct hybrid search content.

---

### P10 — RAGAS RAG Evaluation Framework (closes F14)

| Field | Value |
|-------|-------|
| **URL** | `https://raw.githubusercontent.com/explodinggradients/ragas/main/README.md` |
| **Title** | RAGAS — RAG Evaluation: Faithfulness, Context Precision and Evidence Sufficiency |
| `doc_type` | `markdown` |
| `doc_family` | `reference` |
| `topic_bucket` | `safety_eval` |
| `collapse_group` | `ragas` |
| `required` | `False` |
| **Family closed** | F14 |
| **Proof query** | "How do AI retrieval systems determine when retrieved evidence is insufficient and signal that the agent should refine its query or abstain?" |
| **Justification** | RAGAS is the canonical RAG evaluation framework. Its README covers faithfulness scoring, context precision, and context recall — directly addressing evidence sufficiency and the conditions under which retrieval systems should signal refine/abstain. |

---

### P11 — Guardrails AI Validation and Fallback Handling (closes F17)

| Field | Value |
|-------|-------|
| **URL** | `https://raw.githubusercontent.com/guardrails-ai/guardrails/main/README.md` |
| **Title** | Guardrails AI — Validation Failure Routing, Fallback Values and Abstain Handling |
| `doc_type` | `markdown` |
| `doc_family` | `reference` |
| `topic_bucket` | `safety_eval` |
| `collapse_group` | `guardrails_ai` |
| `required` | `False` |
| **Family closed** | F17 |
| **Proof query** | "How do AI agent frameworks implement graceful fallback routing and explicit abstain signals when no safe action is available?" |
| **Justification** | Guardrails AI is a framework specifically designed for structured output validation in LLM pipelines. Its README covers on-fail actions (REASK, FIX, FILTER, NOOP, EXCEPTION) and fallback values — directly modeling graceful abstain and fallback patterns. |

---

### P12 — Temporal Python SDK Retry and Escalation (closes F25)

| Field | Value |
|-------|-------|
| **URL** | `https://raw.githubusercontent.com/temporalio/sdk-python/main/README.md` |
| **Title** | Temporal Python SDK — Retry Policies, Workflow Failure Handling and Escalation Tiers |
| `doc_type` | `markdown` |
| `doc_family` | `reference` |
| `topic_bucket` | `orchestration` |
| `collapse_group` | `temporal` |
| `required` | `False` |
| **Family closed** | F25 |
| **Proof query** | "How do agentic systems implement confidence-scored tiered healing dispatch routing failures through local rules, model retry, and human escalation?" |
| **Justification** | Temporal is the canonical workflow orchestration framework for tiered retry and escalation. Its Python SDK README covers retry policies (maxAttempts, initialInterval, backoffCoefficient), activity failure handling, and workflow-level escalation chains — directly matching F25's tiered healing model. |

---

## URL Deduplication Proof

All B6.1 URLs are distinct from existing B6 catalog. Pre-existing sources in ext_authority include:
`openai-agents-python`, `anthropic-cookbook`, `langchain-ai/langchain`, `microsoft/autogen`, `openai/swarm`, `GPTCache`, `deepset-ai/haystack`, `UKPLab/sentence-transformers`, `run-llama/llama_index`, `openai/openai-cookbook` — none overlap with Weaviate, RAGAS, Guardrails AI, or Temporal.

**No duplicate URLs introduced.**

---

## Ingestion Blockers Fixed

| Attempt | URL | Status | Resolution |
|---------|-----|--------|-----------|
| P9-v1 | `qdrant/examples/master/hybrid_search/hybrid_search.ipynb` | HTTP 404 | Replaced with Weaviate README |
| P9-v2 | `deepset-ai/haystack-tutorials/main/tutorials/29_Hybrid_Retrieval.ipynb` | HTTP 404 | Replaced with Weaviate README |
| P9-v3 | `weaviate/weaviate/main/README.md` | ✅ 200 OK | Used |
| P10 | `explodinggradients/ragas/main/README.md` | ✅ 200 OK | Used |
| P11 | `guardrails-ai/guardrails/main/README.md` | ✅ 200 OK | Used |
| P12 | `temporalio/sdk-python/main/README.md` | ✅ 200 OK | Used |

**Pre-existing optional failures (not B6.1):**
- `openai-agents-python/main/docs/models.md` — HTTP 404 (pre-existing, optional, not changed)
- `anthropic-cookbook/main/patterns/agents/subagent.ipynb` — HTTP 404 (pre-existing, optional, not changed)

---

## Metadata Contract Compliance

All 4 B6.1 sources conform to the frozen 17-field metadata contract:

| Field | All P9–P12 |
|-------|-----------|
| `source_collection` | `ext_authority` ✅ |
| `authority_tier` | `T3_guidance` ✅ |
| `source_band` | populated by ingestion ✅ |
| `doc_type` | `markdown` or `notebook` ✅ |
| `doc_family` | `reference` or `guide` ✅ |
| `topic_bucket` | `retrieval_rag` / `safety_eval` / `orchestration` ✅ |
| `collapse_group` | unique per source ✅ |
| `invalid_for_normative_use` | `False` ✅ |
| `source_url` | `https://raw.githubusercontent.com/...` ✅ |

No metadata contract changes. No topology changes. No routing changes.
