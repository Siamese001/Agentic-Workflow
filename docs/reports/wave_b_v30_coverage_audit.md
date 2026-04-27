# Wave B v30 Semantic Coverage Audit

**Date**: 2026-04-15
**Baseline**: Wave B external-only target-state audit — 14/20 adequately grounded, G9 FAIL at 70%
**Checklist source**: `docs/reference/_notes/agentic_process_mapping_v34.md` — used as semantic coverage checklist only
**Anti-drift rule**: v30 is a semantic family checklist; it is NOT a target-state authority. Target-state grounding derives exclusively from `ext_authority`. `repo_evidence` and `ext_raw` are excluded.
**Scope**: Classify every mandatory v30 semantic family as STRONG / ADEQUATE / WEAK / MISSING in `ext_authority`.

---

## 1. Ranked Audit Findings

| Rank | Severity | Finding |
|------|----------|---------|
| 1 | **BLOCKING** | **F02 — R1A Exact Cache Route**: MISSING — no `ext_authority` topic covers deterministic policy-driven cache routing in agentic systems |
| 2 | **BLOCKING** | **F03 — R1B Semantic Cache Route**: MISSING — no `ext_authority` topic covers vector-similarity query caching; TS-19 (embedding model, WEAK) is tangential |
| 3 | **BLOCKING** | **F07 — V1 Full Retrieval Pipeline**: WEAK across 4 audit topics (TS-03 hybrid retrieval, TS-04 reranking, TS-07 parent-child expansion, TS-19 embedding model) — no RAG library docs in `ext_authority` |
| 4 | **BLOCKING** | **F10 — R5 Fallback / Abstain-Refine**: WEAK — TS-09 dist@1=0.510; no dedicated external authority for graceful fallback or abstain signal patterns |
| 5 | **SCOPED OUT** | **F12 — L5 Normative Requirements**: WEAK — TS-20 dist@1=0.529; project-specific policy; correct scope is `repo_evidence` Lane C, not `ext_authority` |
| 6 | NON-BLOCKING | **F06 — V1 Dense Vector Retrieval (basic)**: ADEQUATE — core similarity search covered by TS-05 (metadata provenance), TS-06 (chunking strategy) |
| 7 | NON-BLOCKING | **F11 — L5 Guardrails**: ADEQUATE — TS-16 dist@1=0.456 via openai-agents guardrails docs |
| 8 | NON-BLOCKING | **F01 — L0 Route Authority**: ADEQUATE — TS-10 (routing principles), TS-11 (agentic architecture) |
| 9 | NON-BLOCKING | **F04 — R3 Agentic RAG**: ADEQUATE — TS-02, TS-08, TS-10 together cover context-grounded retrieval invocation |
| 10 | NON-BLOCKING | **F05 — C0 Context Assembly**: ADEQUATE — TS-01 (context engineering), TS-08 (evidence shaping) |
| 11 | NON-BLOCKING | **F08 — Prompt Assembly (packaging only)**: ADEQUATE — TS-01, TS-08 cover post-retrieval packaging; v30 explicitly marks this "does not retrieve" |
| 12 | NON-BLOCKING | **F13 — [5] Current-Run Evaluation / Exit Control**: ADEQUATE — TS-17 (evaluator-optimizer) covers evaluation loop and disposition logic |
| 13 | NON-BLOCKING | **F14 — [6] Future-Run Learning / L6 Observability**: ADEQUATE — TS-17 + openai-agents tracing docs in `ext_authority` cover shadow eval and system learning |
| 14 | NON-BLOCKING | **F09 — R4 External Action Route**: STRONG — TS-13 dist@1=0.277, TS-14 dist@1=0.347 |
| 15 | NON-BLOCKING | **F15 — L2 Execution Contract (externally representable)**: STRONG — TS-12 (orchestrator-workers) dist@1=0.349, TS-15 (agent handoffs) dist@1=0.335; internal healing tiers are repo_evidence scope |

---

## 2. v30 Semantic Family Checklist

Extracted from `agentic_process_mapping_v30.md`. Each family represents one mandatory semantic coverage unit.

| # | v30 Family | v30 Source Section | Classification | TS Topic(s) |
|---|-----------|-------------------|----------------|-------------|
| F01 | L0 Route Authority | [3] L0 ROUTING dispatcher, D1–D5 decision tree | **ADEQUATE** | TS-10, TS-11 |
| F02 | R1A Exact Cache Route | D1: Exact cache key hit by policy → short-circuit | **MISSING** | None |
| F03 | R1B Semantic Cache Route | D2: new_query_vec vs cached_query_vecs, persistent store | **MISSING** | None (TS-19 tangential, WEAK) |
| F04 | R3 Agentic RAG | D3: Requires grounded context → C0 → V1 | **ADEQUATE** | TS-02, TS-08, TS-10 |
| F05 | C0 Context Assembly | C0 CONTEXT ENGINE: intent → query_vec → contextual facts | **ADEQUATE** | TS-01, TS-08 |
| F06 | V1 Vector Retrieval / Evidence Fetch (dense) | V1 VECTOR DATABASE: intent vec vs contextual_text_vec | **ADEQUATE** | TS-05, TS-06 |
| F07 | V1 Full Retrieval Pipeline (hybrid + reranking + expansion) | V1 + advanced strategies implied by R3 | **WEAK** | TS-03 WEAK, TS-04 WEAK, TS-07 WEAK, TS-19 WEAK |
| F08 | Prompt Assembly (packaging, not retrieval) | PROMPT ASSEMBLY: "Packages grounded context / Does not retrieve" | **ADEQUATE** | TS-01, TS-08 |
| F09 | R4 External Action Route | D4: Requires external action → R4 ACTION → L2 tool dispatch | **STRONG** | TS-13 (dist@1=0.277), TS-14 (dist@1=0.347) |
| F10 | R5 Fallback Route | D4 no → R5 FALLBACK: safe, ungrounded default | **WEAK** | TS-09 (dist@1=0.510) |
| F11 | L5 Policy Plane — Guardrails | L5: cross-cutting safety authority over all phases | **ADEQUATE** | TS-16 (dist@1=0.456) |
| F12 | L5 Policy Plane — Normative Requirements | L5: policy invariants, normative specs | **WEAK** | TS-20 (dist@1=0.529) — repo_evidence scope |
| F13 | [5] Current-Run Evaluation / Exit Control | [5] CURRENT-RUN EVALUATION: DENY / ESCALATE / COMMIT → WRITE GATE | **ADEQUATE** | TS-17 (dist@1=0.429) |
| F14 | [6] Future-Run Learning / L6 Observability | [6] SHADOW EVALUATION: telemetry ingest, RCA, system learning | **ADEQUATE** | TS-17, openai-agents tracing docs |
| F15 | L2 Execution Contract Lifecycle (ext. representable) | [4.1] E1–E5: init / validate / execute / heal / synthesize | **STRONG** | TS-12 (dist@1=0.349), TS-15 (dist@1=0.335) |

---

## 3. Mapping from Wave B Registry Topics to v30 Families

| Wave B Topic | Query ID | Grade | dist@1 | v30 Family (primary) |
|--------------|----------|-------|--------|----------------------|
| Context Engineering | TS-01 | ADEQUATE | 0.421 | F05 (C0 Context Assembly), F08 (Prompt Assembly) |
| Contextual Retrieval | TS-02 | ADEQUATE | 0.500 | F04 (R3 Agentic RAG), F06 (V1 dense) |
| Hybrid Retrieval | TS-03 | WEAK | 0.561 | F07 (V1 full pipeline) |
| Cross-Encoder Reranking | TS-04 | WEAK | 0.531 | F07 (V1 full pipeline) |
| Metadata Provenance | TS-05 | ADEQUATE | 0.498 | F06 (V1 dense), F08 (Prompt Assembly) |
| Chunking Strategy | TS-06 | ADEQUATE | 0.500 | F06 (V1 dense) |
| Parent-Child Expansion | TS-07 | WEAK | 0.515 | F07 (V1 full pipeline) |
| Evidence Shaping | TS-08 | ADEQUATE | 0.445 | F05 (C0 Context Assembly), F08 (Prompt Assembly) |
| Abstain / Refine | TS-09 | WEAK | 0.510 | F10 (R5 Fallback Route) |
| Routing Principles | TS-10 | ADEQUATE | 0.473 | F01 (L0 Route Authority), F04 (R3 Agentic RAG) |
| Agentic Architecture | TS-11 | ADEQUATE | 0.417 | F01 (L0 Route Authority), F15 (L2 Lifecycle) |
| Orchestrator-Workers | TS-12 | STRONG | 0.349 | F15 (L2 Lifecycle ext.), F04 (R3 RAG) |
| Tool Contracts MCP | TS-13 | STRONG | 0.277 | F09 (R4 External Action) |
| FastMCP Patterns | TS-14 | STRONG | 0.347 | F09 (R4 External Action) |
| Agent Handoffs | TS-15 | STRONG | 0.335 | F15 (L2 Lifecycle ext.) |
| Safety Guardrails | TS-16 | ADEQUATE | 0.456 | F11 (L5 Guardrails) |
| Evaluator-Optimizer | TS-17 | ADEQUATE | 0.429 | F13 ([5] Exit Control), F14 ([6] Future-Run Learning) |
| Single vs Multi-Agent | TS-18 | STRONG | 0.329 | F01 (L0 Route Authority), F15 (L2 Lifecycle ext.) |
| Embedding Model | TS-19 | WEAK | 0.510 | F07 (V1 full pipeline), F03 (R1B, tangential only) |
| Normative Requirements | TS-20 | WEAK | 0.529 | F12 (L5 Normative — repo_evidence scope) |

**Unmapped v30 families (no Wave B TS topic)**: F02 (R1A Exact Cache), F03 (R1B Semantic Cache)
These two families have no corresponding Wave B audit query and no `ext_authority` coverage. They are net-new gaps discovered by this v30 analysis.

---

## 4. Weak or Missing Semantic Families

### MISSING — No ext_authority Coverage

| Family | v30 Reference | Gap Analysis |
|--------|--------------|-------------|
| **F02 — R1A Exact Cache Route** | D1: "Exact cache key hit by policy?" → short-circuit | No `ext_authority` source covers policy-driven deterministic cache routing for LLM agents. The existing sources (openai-agents, MCP SDK, autogen, anthropic-cookbook) do not address caching patterns. This is a target-state pattern (when/why to short-circuit via exact cache) — external authority required. |
| **F03 — R1B Semantic Cache Route** | D2: "Matches new_query_vec against cached_query_vecs; requires persistent store for cold starts" | No `ext_authority` source covers vector-similarity-based query cache lookup. TS-19 (embedding model dimensions/metrics) is tangential — it does not address the semantic cache routing pattern. Semantic caching requires dedicated sources (e.g., GPTCache, Zilliz semantic cache, semantic caching papers). |

### WEAK — Partial Coverage, dist@1 > 0.50

| Family | TS Topic(s) | dist@1 Range | Gap Characterization |
|--------|------------|-------------|----------------------|
| **F07 — V1 Full Retrieval Pipeline** | TS-03, TS-04, TS-07, TS-19 | 0.510–0.561 | No RAG retrieval library docs in `ext_authority`. Dense similarity (F06) is covered; hybrid fusion, cross-encoder reranking, and parent-child expansion are not. All 4 audit topics return irrelevant top-1 results (openai-agents tool docs, not retrieval library docs). |
| **F10 — R5 Fallback / Abstain-Refine** | TS-09 | 0.510 | Abstain/refine signals are only borderline WEAK. Top results are about agent approval flows (not explicit abstain patterns). A dedicated source on graceful fallback routing and evidence sufficiency thresholds would close this. |
| **F12 — L5 Normative Requirements** | TS-20 | 0.529 | Project-specific normative policy (determinism, provenance, safety invariants) is inherently internal. This is correctly scoped to `repo_evidence` Lane C. Closing this via `ext_authority` would violate the anti-drift rule — internal policy is current-state, not target-state external authority. |

---

## 5. Exact Minimum Source Categories for B6

### Group A — v30 Net-New Gaps (not in Wave B 6-gap list)

| Priority | Gap | Family | Minimum Source Category | Candidate |
|----------|-----|--------|------------------------|-----------|
| P1 | R1A Exact Cache Route | F02 | LLM response caching docs: deterministic cache routing patterns for agentic systems | LangChain caching guide (raw.githubusercontent.com/langchain-ai), Semantic Kernel caching docs |
| P2 | R1B Semantic Cache Route | F03 | Semantic LLM caching: vector-similarity query cache lookup patterns | GPTCache/Zilliz semantic cache tutorial, Milvus semantic cache docs |

### Group B — Known Wave B Gaps Confirmed Still Open by v30

| Priority | Gap | Family | Minimum Source Category | Candidate (per Wave C handoff contract §2) |
|----------|-----|--------|------------------------|-------------------------------------------|
| P3 | Hybrid Retrieval | F07 | RAG library docs: hybrid dense+sparse fusion with score normalization | Anthropic contextual retrieval cookbook, LlamaIndex hybrid search |
| P4 | Cross-Encoder Reranking | F07 | Reranking pipeline docs | Cohere reranker docs, Anthropic retrieval cookbook |
| P5 | Parent-Child Chunk Expansion | F07 | Chunk retrieval pipeline docs | LlamaIndex parent document retriever |
| P6 | Abstain / Refine / Fallback | F10 | Abstain/graceful fallback best practices | Anthropic patterns cookbook, general RAG abstain patterns |
| P7 | Embedding Model Selection | F07 / F03 | Embedding model comparison and selection guide | MTEB leaderboard docs, OpenAI/Cohere/BAAI embedding guides |

**Total B6 ext_authority additions required: 7** (P1–P7)

**Out-of-scope for ext_authority**: F12 (Normative Requirements) → add to `repo_evidence` Lane C, not `ext_authority`. This does not count as a B6 ext_authority source.

**Post-B6 audit target**: Extended audit of 22 queries (20 existing + 2 new for F02, F03). Required: ≥17/22 adequately grounded (77%) to exceed G9 75% threshold.

---

## 6. Final Go/No-Go Verdict for Wave C

**Verdict: NO-GO**

| Criterion | Current State | Required |
|-----------|--------------|---------|
| G1–G8, G10, G11 (hard gates) | PASS — baseline established | Must remain PASS after B6 |
| G9 retrieval strength | FAIL — 14/20 = 70% | ≥15/20 = 75% (current contract) |
| F02 R1A Exact Cache Route | MISSING | Source + audit query required |
| F03 R1B Semantic Cache Route | MISSING | Source + audit query required |
| F07 V1 Full Pipeline | WEAK (4 topics) | 5 source additions (P3–P7) required |
| F10 R5 Fallback / Abstain | WEAK | 1 source addition (P6) required |
| F12 L5 Normative Requirements | WEAK — scoped to repo_evidence | Add to Lane C; not an ext_authority B6 gap |
| B6 source addition plan | NOT DRAFTED | Required before Wave C entry |

**Wave C is blocked by 5 open conditions**:
1. G9 not met — 14/20, 1 below threshold; new sources required
2. F02 MISSING — no ext_authority grounding for exact cache route (net-new v30 gap)
3. F03 MISSING — no ext_authority grounding for semantic cache route (net-new v30 gap)
4. F07 WEAK — 4 retrieval pipeline audit topics below threshold; 5 source additions required
5. F10 WEAK — abstain/fallback audit topic at boundary; 1 source addition required

---

## 7. Single Final Recommendation

**Issue one bounded B6 source-addition prompt** targeting exactly 7 new `ext_authority` sources:

| # | Source to Add | Closes | Closes TS |
|---|--------------|--------|-----------|
| 1 | LLM response caching library docs (deterministic cache routing) | F02 — R1A | NEW |
| 2 | Semantic/vector LLM caching docs (similarity-based cache lookup) | F03 — R1B | NEW |
| 3 | Hybrid dense+sparse retrieval docs (score fusion) | F07 | TS-03 |
| 4 | Cross-encoder reranking docs | F07 | TS-04 |
| 5 | Parent-child chunk expansion docs | F07 | TS-07 |
| 6 | Abstain / graceful fallback best practices | F10 | TS-09 |
| 7 | Embedding model comparison and selection guide | F07 / F03 | TS-19 |

**Do NOT** add TS-20 (Normative Requirements) to `ext_authority`. Route that to `repo_evidence` Lane C.

After B6 ingestion, re-run freeze gates with an extended 22-query audit (TS-01–TS-20 + 2 new F02 / F03 queries). Wave C entry is unblocked when: (a) ≥17/22 adequately grounded and (b) all 11 hard freeze gates continue to pass.
