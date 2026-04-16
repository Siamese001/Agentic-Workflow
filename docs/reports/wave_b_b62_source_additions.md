# Wave B6.2 — Source Additions Report

**Date:** 2026-04-16  
**Scope:** ext_authority only — 1 new source for F25  
**Base:** B6.1 (29 sources, 586 docs) → B6.2 (30 sources, 592 docs)  
**Anti-drift:** No changes to topology, router, shaper, repo_evidence, ext_raw, or metadata contract

---

## Purpose

Wave B6.1 left F25 unresolved:

| Family | B5R Grade | B6 dist@1 | B6.1 dist@1 | B6.1 Status |
|--------|-----------|-----------|-------------|-------------|
| F25 | WEAK | 0.5043 | 0.5043 | WEAK / MISSING — P12 (Temporal) did not embed close enough |

B6.1 confirmed: the Temporal SDK README (P12) covers infrastructure-level retry policies (maxAttempts, backoff coefficients) which are semantically too distant from the F25 query vocabulary ("confidence-scored tiered healing dispatch", "human escalation", "agentic systems"). B6.2 adds one AI-native source to close this gap.

---

## New Source Added (P13)

### P13 — LangGraph Durable Execution, Human-in-the-Loop Escalation and Agent Failure Recovery (closes F25)

| Field | Value |
|-------|-------|
| **URL** | `https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/langgraph/README.md` |
| **Title** | LangGraph — Durable Execution, Human-in-the-Loop Escalation and Agent Failure Recovery |
| `doc_type` | `markdown` |
| `doc_family` | `reference` |
| `topic_bucket` | `orchestration` |
| `collapse_group` | `langgraph_core` |
| `required` | `False` |
| **Family targeted** | F25 |
| **Proof query** | "How do agentic systems implement confidence-scored tiered healing dispatch routing failures through local rules, model retry, and human escalation?" |

**Why it closes F25:**  
The `libs/langgraph/README.md` explicitly covers two concepts at the core of the F25 query:
- **Durable execution**: "Build agents that persist through failures and can run for extended periods, automatically resuming from exactly where they left off" — directly models tiered failure recovery and healing dispatch.
- **Human-in-the-loop**: "Seamlessly incorporate human oversight by inspecting and modifying agent state at any point during execution" — directly models human escalation as the final tier.

Both are AI-native agent patterns, not infrastructure retry policies.

**Why it is more semantically aligned than Temporal (P12):**  
Temporal models retry as infrastructure scheduler concepts (maxAttempts, initialInterval, backoffCoefficient). The F25 query uses vocabulary from AI agent architecture: "agentic systems", "healing dispatch", "human escalation". LangGraph's library README uses precisely "durable execution", "agent persist through failures", "human-in-the-loop" — overlapping with the query embedding space.

**Why it should improve the F25 proof query:**  
The embedding model should place "durable execution" + "human-in-the-loop" closer to "tiered healing dispatch" + "human escalation" than infrastructure retry terminology. P13 provides 6 new chunks in the orchestration topic bucket targeting this semantic region.

**URL deduplication check:**  
- Existing catalog entry: `https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md` (repo-level README, `collapse_group: "langgraph"`)
- P13: `https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/langgraph/README.md` (library-level README, `collapse_group: "langgraph_core"`)
- **These are distinct files at distinct paths. No duplication introduced.** ✅

---

## Metadata Assignment Summary

| Field | P13 Value |
|-------|-----------|
| `source_collection` | `ext_authority` |
| `source_band` | `supporting_guidance` (assigned by ingestion) |
| `authority_tier` | `T3_guidance` |
| `normative_scope` | populated by ingestion |
| `invalid_for_normative_use` | `False` |
| `source_type` | `external_web` |
| `topic_bucket` | `orchestration` |
| `doc_family` | `reference` |
| `source_url` | `https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/langgraph/README.md` |
| `heading_path` | populated per chunk by section-aware chunker |
| `collapse_group` | `langgraph_core` |
| `title` | LangGraph — Durable Execution, Human-in-the-Loop Escalation and Agent Failure Recovery |
| `chunk_index` | 0-N per chunk |
| `canonical_digest` | SHA256 per chunk (computed by ingestion) |
| `version_or_date` | populated by ingestion |
| `parent_id` | populated by section-aware parent/child hierarchy |
| `child_ids` | populated by section-aware parent/child hierarchy |

All 17 required metadata fields populated. No metadata contract changes.

---

## B6.2 Validation Result — F25

| Metric | B6.1 Baseline | B6.2 Result |
|--------|---------------|-------------|
| `dist@1` | 0.5043 | **0.5043** |
| `delta` | — | 0.0000 |
| `n_rel<0.50` | 0 | 0 |
| P13 in top-5 | — | **no** |
| Grade | WEAK | **WEAK** |

**Assessment:** P13 was successfully ingested (6 new chunks, collection 586→592). However, the semantic gap between the F25 query ("confidence-scored tiered healing dispatch") and all available sources remains too large for the embedding model to bridge with the current P13 content. The `libs/langgraph/README.md` is a concise library introduction (~6KB) that describes capabilities at a high level; it does not contain the dense, implementation-level vocabulary that would rank above 0.50 distance.

Encouraging signal: Rank 3 now shows `running_agents.md` heading "Running agents > Durable execution integrations and human-in-the-loop" at dist=0.5190 — the concept space is being touched but the threshold is not yet crossed.

**F25 remains the single open blocker for B7.**

---

## Anti-Drift Compliance

| Constraint | Status |
|-----------|--------|
| Only `ext_authority` changed | ✅ |
| Only F25 targeted | ✅ |
| `query_router.py` not modified | ✅ |
| `evidence_shaper.py` not modified | ✅ |
| `retrieval_eval_curated.py` not modified | ✅ |
| `repo_evidence` ingestion not modified | ✅ |
| `ext_raw` ingestion not modified | ✅ |
| Metadata contract not changed | ✅ |
| `wave_b_closeout.md` not modified | ✅ |
| `wave_c_handoff_contract.md` not modified | ✅ |
| No F12/F14/F17/F21/F22/F28 sources added | ✅ |
| No Wave C scope | ✅ |
