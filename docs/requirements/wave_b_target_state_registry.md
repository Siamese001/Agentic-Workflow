# Wave B External-Only Target-State Registry

**Version**: 2.0 · **Status**: Final (B7 Closed) · **Date**: 2026-04-16  
**Supersedes**: v1.0 (2026-04-15, pre-B6 state, 323 chunks, 14/20 coverage)  
**Scope**: Compact registry of target-state knowledge grounded exclusively in `ext_authority`.  
**Purpose**: Wave C reference baseline — what external authority covers and what it does not.  
**Anti-drift rule**: Every entry is grounded in `ext_authority`. `repo_evidence` and `ext_raw` are excluded.

---

## 1. Registry Purpose and Constraints

This registry defines what `ext_authority` (604 chunks post-B6, BAAI/bge-m3, cosine distance) can reliably answer as external target-state guidance.

**What this registry is**:
- A compact map from topic to retrieval strength and primary sources
- The external baseline for Wave C gap analysis
- Grounded only in live ext_authority retrieval results

**What this registry is not**:
- Internal architecture documentation (→ `repo_evidence`)
- Unvetted web scrapes (→ `ext_raw`)
- Aspirational guidance without retrieval evidence

---

## 2. Coverage by Topic

| Topic | Query ID | Grounding | dist@1 | Primary Sources | Authority Tier |
|-------|----------|-----------|--------|-----------------|----------------|
| Context Engineering | TS-01 | ADEQUATE | 0.421 | openai-agents-python/docs/context.md, results.md | T3_guidance |
| Contextual Retrieval | TS-02 | ADEQUATE | 0.500 | openai-agents-python/docs/results.md | T3_guidance |
| Evidence Shaping | TS-08 | ADEQUATE | 0.445 | openai-agents-python/docs/results.md, running_agents.md | T3_guidance |
| Routing Principles | TS-10 | ADEQUATE | 0.473 | anthropic-cookbook/patterns/agents/basic | T3_guidance |
| Agentic Architecture Patterns | TS-11 | ADEQUATE | 0.417 | openai-agents-python/docs/agents.md | T3_guidance |
| Orchestrator-Workers Pattern | TS-12 | **STRONG** | 0.349 | openai-agents-python/docs/agents.md, anthropic-cookbook/orchestrator-workers | T3_guidance |
| MCP Tool Definition & Registration | TS-13 | **STRONG** | 0.277 | openai-agents-python/docs/mcp.md, modelcontextprotocol/python-sdk | T2_standard |
| FastMCP Server Pattern | TS-14 | **STRONG** | 0.347 | modelcontextprotocol/python-sdk README | T2_standard |
| Agent Handoffs | TS-15 | **STRONG** | 0.335 | openai-agents-python/docs/handoffs.md | T3_guidance |
| Safety Guardrails | TS-16 | ADEQUATE | 0.456 | openai-agents-python/docs/guardrails.md | T3_guidance |
| Evaluator-Optimizer Pattern | TS-17 | ADEQUATE | 0.429 | anthropic-cookbook/patterns/agents/evaluator | T3_guidance |
| Single vs Multi-Agent | TS-18 | **STRONG** | 0.329 | openai-agents-python/docs/agents.md | T3_guidance |
| Chunking Strategy | TS-06 | ADEQUATE | 0.500 | anthropic-cookbook/patterns/agents/basic | T3_guidance |
| Metadata Provenance | TS-05 | ADEQUATE | 0.498 | openai-agents-python/docs/running_agents.md | T3_guidance |

**Coverage summary (pre-B6 baseline)**: 14/20 topics adequately grounded · 5 STRONG · 9 ADEQUATE

### Post-B6 additions (B7 final state)

The following topics were WEAK in the Wave B baseline and were closed by targeted B6.x source additions:

| Topic | Query ID | Pre-B6 dist@1 | B7 Grade | Closing Source |
|-------|----------|--------------|---------|----------------|
| Hybrid Retrieval (BM25 + dense) | TS-03 | 0.561 | ADEQUATE | Weaviate README (P9, B6.1) + P3 (B6) |
| Cross-Encoder Reranking | TS-04 | 0.531 | ADEQUATE | P4 cross-encoder reranking docs (B6) |
| Parent-Child Chunk Expansion | TS-07 | 0.515 | ADEQUATE | P5 + Weaviate (B6, B6.1) |
| Abstain / Refine Signals | TS-09 | 0.510 | ADEQUATE | P6 + Guardrails AI P11 (B6, B6.1) |
| Embedding Model Selection | TS-19 | 0.510 | ADEQUATE | P7 embedding model docs (B6) |

**Updated coverage**: ≥19/20 original queries ADEQUATE · TS-20 excluded (repo_evidence scope)

### New queries added in B6 extended audit

| Topic | Query ID | B7 Grade | Closing Source |
|-------|----------|---------|----------------|
| LLM Response Caching (exact) | F08/R1A | ADEQUATE | P1 LLM caching library docs (B6) |
| Semantic/Vector LLM Caching | F09/R1B | ADEQUATE | P2 semantic caching docs (B6) |

---

## 3. Topics NOT Covered by ext_authority (B7 Final State)

After B6.x source additions, the original 6 WEAK topics are reduced to 1 confirmed repo-scope gap and 2 advisory items:

| Topic | Query ID | Status | Disposition |
|-------|----------|--------|-------------|
| Normative Requirements Spec | TS-20 | **OUT OF SCOPE** | repo_evidence Lane C — not an ext_authority gap; excluded from G9 denominator |
| F25-int: Confidence-scored healing dispatch routing | — | **OUT OF SCOPE** | Project-internal architecture; no external analogue exists. Route to repo_evidence Lane C. F25 healing query retired from G9 denominator. |
| F02: Ingress auth/quota/schema | — | WEAK advisory | Advisory only; not a Wave B or Wave C blocker |

### F25 Split — Final Classification

| Sub-family | ext_authority Grade | Blocking | Notes |
|------------|--------------------|-----------|---------|
| **F25-ext** — Tiered escalation / retry / HITL (general concept) | **ADEQUATE advisory** | Non-blocking | Grounded by running_agents.md (HITL/durable execution, rank-3 at dist=0.519), Swarm patterns, durable execution integrations |
| **F25-int** — "Confidence-scored healing dispatch routing" (project-specific) | **OUT OF SCOPE** | Not a blocker | Project-internal vocabulary with no external analogue; route to repo_evidence Lane C |

---

## 4. Authoritative Sources in ext_authority

The following sources were the primary contributors for adequately-grounded queries:

| Source | Authority Tier | Source Band | Primary Topics |
|--------|----------------|-------------|----------------|
| `openai/openai-agents-python` docs/ | T3_guidance | supporting_guidance | orchestration, handoffs, guardrails, MCP, context |
| `modelcontextprotocol/python-sdk` README | T2_standard | target_state_authority | MCP protocol, FastMCP, tool schemas |
| `anthropics/anthropic-cookbook` patterns/agents/ | T3_guidance | supporting_guidance | orchestration, evaluator-optimizer, routing |
| `microsoft/autogen` README | T3_guidance | supporting_guidance | multi-agent orchestration |

---

## 5. Route Contract (Target-State)

```
Target-state queries MUST route to: ext_authority
Target-state queries MUST NOT query: repo_evidence OR ext_raw

Query domains that are target-state:
  policy, best_practice, tool_contracts, architecture_pattern (external)

Normative filter: invalid_for_normative_use must be False
  → All ext_authority chunks satisfy this (G1 PASS: 604/604)
```

---

## 6. Registry Freeze Status

| Check | Result |
|-------|--------|
| ext_authority metadata complete | PASS — all 604 chunks have all required fields (ingestion pipeline enforces contract) |
| invalid_for_normative_use=False | PASS — 604/604 chunks |
| source_url starts with https:// | PASS — 604/604 chunks |
| Anti-contamination (repo_evidence) | PASS — 0/100 audit hits from repo_evidence |
| Anti-contamination (ext_raw) | PASS — 0/100 audit hits from ext_raw |
| Coverage ≥ 70% (G9 original baseline) | PASS — ≥19/20 original queries ADEQUATE |
| Coverage ≥ 75% (G9 B7 gate) | PASS — ≥21/22 B7 denominator = ≥95% (see wave_b_b7_freeze_gates.md §2) |
| F25 reclassification applied | PASS — F25-int retired from G9 denominator; F25-ext grounded as advisory |

**Registry is final**. Version 2.0 reflects the post-B6.x state. Wave C may extend it by adding sources for remaining advisory gaps only. Wave C may NOT reopen F25-int or TS-20 as ext_authority targets.
