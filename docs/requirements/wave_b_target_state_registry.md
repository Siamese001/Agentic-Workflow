# Wave B External-Only Target-State Registry

**Version**: 1.0 · **Status**: Frozen · **Date**: 2026-04-15  
**Scope**: Compact registry of target-state knowledge grounded exclusively in `ext_authority`.  
**Purpose**: Wave C reference baseline — what external authority covers and what it does not.  
**Anti-drift rule**: Every entry is grounded in `ext_authority`. `repo_evidence` and `ext_raw` are excluded.

---

## 1. Registry Purpose and Constraints

This registry defines what `ext_authority` (323 chunks, BAAI/bge-m3, cosine distance) can reliably answer as external target-state guidance.

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

**Coverage summary**: 14/20 topics adequately grounded · 5 STRONG · 9 ADEQUATE

---

## 3. Topics NOT Covered by ext_authority (Wave C Gaps)

These 6 topics returned WEAK grounding (dist@1 > 0.50) — ext_authority has no directly relevant chunks. These are Wave C source requirements.

| Topic | Query ID | dist@1 | Gap Characterization | Wave C Source Needed |
|-------|----------|--------|----------------------|----------------------|
| Hybrid Retrieval (BM25 + dense, score fusion) | TS-03 | 0.561 | No RAG retrieval library docs | Anthropic contextual retrieval cookbook, or LlamaIndex hybrid search docs |
| Cross-Encoder Reranking | TS-04 | 0.531 | No reranking pipeline docs | Cohere reranker docs, Anthropic retrieval cookbook |
| Parent-Child Chunk Expansion | TS-07 | 0.515 | No chunk retrieval pipeline docs | LlamaIndex, or Anthropic contextual retrieval |
| Abstain / Refine Signals | TS-09 | 0.510 | No explicit abstain/refine pattern | Anthropic patterns cookbook, general RAG best practices |
| Embedding Model Selection | TS-19 | 0.510 | No embedding model comparison docs | MTEB leaderboard, model provider embedding guides |
| Normative Requirements Spec | TS-20 | 0.529 | No normative requirements specification docs | Project-specific policy docs → repo_evidence Lane C |

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
  → All ext_authority chunks satisfy this (G1 PASS: 323/323)
```

---

## 6. Registry Freeze Status

| Check | Result |
|-------|--------|
| ext_authority metadata complete | PASS — all 323 chunks have all required fields |
| invalid_for_normative_use=False | PASS — 323/323 chunks |
| source_url starts with https:// | PASS — 323/323 chunks |
| Anti-contamination (repo_evidence) | PASS — 0/100 audit hits from repo_evidence |
| Anti-contamination (ext_raw) | PASS — 0/100 audit hits from ext_raw |
| Coverage ≥ 70% | PASS — 14/20 = 70% |
| Coverage ≥ 75% (G9 soft gate) | FAIL — 14/20 = 70%; 6 retrieval-infra topics need Wave C sources |

**Registry is frozen**. Wave C may extend it by adding sources for the 6 gap topics only.
