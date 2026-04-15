# Wave B B5R — Family-to-Query Map

**Date**: 2026-04-15  
**Source**: `tools/diag/b5r_direct_proof_runner.py`  
**Purpose**: Canonical mapping of each B5R family to its proof query for direct ext_authority retrieval.  
**Anti-drift rule**: Query texts are the authoritative proof queries, not the TS-xx naming aliases used in the B5R audit.

---

## Query Status Legend

- **REUSED-TS-xx**: Query text is semantically equivalent to an existing TS evaluation query referenced in the B5R audit.
- **NEW**: Net-new query with no prior TS alias; required for families with no prior retrieval proof.
- **NEW-INTERNAL-PROBE**: Query for an INTERNAL family — used to demonstrate absence of external authority, not to prove coverage.

---

## 31-Family Query Map

| # | Family Name | Blocks B6? | Query Status | Proof Query Text |
|---|-------------|-----------|--------------|-----------------|
| F01 | Request-source modes / bounded ingress | No | REUSED-TS-11 | How do agentic AI systems handle multiple request sources and enforce bounded ingress from queues, APIs, and events? |
| F02 | Identity/quota/schema/normalization/ingress contract | Advisory | REUSED-TS-20 | How do AI agent systems enforce identity verification, quota limits, and schema validation at the system ingress boundary? |
| F03 | L1 intent framing and work classification | No | REUSED-TS-01 | How do AI agent frameworks classify incoming requests and frame user intent into structured work units? |
| F04 | L1 priors/policy/example loading | No | REUSED-TS-11 | How do agentic systems load prior context, policy constraints, and few-shot examples before generating a plan? |
| F05 | L1 decomposition/dependency/proposed-route drafting | No | REUSED-TS-18 | How do AI agents decompose complex tasks into subtasks with dependency ordering and propose execution routes? |
| F06 | L1 validation/simplify/clarify/abstain planning | **YES** | REUSED-TS-09 | When should an AI agent abstain, clarify ambiguity, or simplify a plan rather than proceed with uncertain execution? |
| F07 | L0 route authority/prefilters/freshness/ACL | No | REUSED-TS-10 | How does an agentic system implement route authority, access control lists, and freshness prefilters at the L0 dispatch layer? |
| F08 | R1A exact cache route | **YES** | **NEW** | How do AI systems implement deterministic response caching with policy-key short-circuit routing to avoid redundant LLM inference? |
| F09 | R1B semantic cache route | **YES** | **NEW** | How do vector similarity-based semantic caches retrieve cached LLM responses for semantically equivalent queries without re-running inference? |
| F10 | R3 grounded-context decision | No | REUSED-TS-02 | How do AI agents decide when retrieved external context is required to ground a factual or policy-driven response? |
| F11 | C0 retrieval planning/scoping | No | REUSED-TS-01 | How do agentic retrieval systems plan and scope collection selection, freshness constraints, and query mode before fetching evidence? |
| F12 | C0 evidence fetch: dense/sparse/cache/metadata/parent-child | **YES** | REUSED-TS-03 | How does hybrid dense and sparse retrieval combine BM25 lexical search with vector embeddings for evidence fetching with parent-child chunk expansion? |
| F13 | C0 evidence shaping: dedup/rerank/prune/conflicts | **YES** | REUSED-TS-04 | How do cross-encoder reranking models reorder and prune retrieved evidence chunks to improve relevance before context assembly? |
| F14 | C0 evidence contract: verified chunks/cited spans/refine-abstain | **YES** | REUSED-TS-09 | How do AI retrieval systems determine when retrieved evidence is insufficient and signal that the agent should refine its query or abstain? |
| F15 | Prompt assembly: load/slot/budget/contract | No | REUSED-TS-08 | How do agentic systems assemble prompts by loading templates, slotting retrieved context, and enforcing token budget constraints? |
| F16 | R4 external action route | No | REUSED-TS-13 | How do AI agents dispatch external tool calls, API actions, and compute tasks with payload validation and state mutation tracking? |
| F17 | R5 fallback/clarify/abstain route | **YES** | REUSED-TS-09 | How do AI agent frameworks implement graceful fallback routing and explicit abstain signals when no safe action is available? |
| F18 | Governance invocation and authority context | No | REUSED-TS-16 | How do agentic systems invoke governance checks and load authority context before executing high-risk or policy-sensitive operations? |
| F19 | Structure/registry/classification/policy chokepoint | No | REUSED-TS-13 | How do AI agent frameworks enforce policy chokepoints through registry validation and risk-tier classification of agent actions? |
| F20 | Sovereign egress/compliance artifacts/capability token/sandbox | No | REUSED-TS-13 | How do agentic systems enforce capability tokens, sandbox envelopes, and compliance artifact generation at the egress boundary? |
| F21 | Replay envelope and freeze propagation | No (INTERNAL) | NEW-INTERNAL-PROBE | How do deterministic replay systems implement freeze signal propagation across architectural layers with policy hash verification? |
| F22 | Replay guard: time/entropy/identity/network/reads/writes | No (INTERNAL) | NEW-INTERNAL-PROBE | How do deterministic replay guards intercept wall-clock time, seeded entropy sources, and network calls to ensure reproducible agent execution? |
| F23 | Determinism digest and replay verification | No | REUSED-TS-05 | How do AI systems generate and verify audit trail digests for agent decisions with provenance metadata and cited source attribution? |
| F24 | L2 execution lifecycle E1-E5 | No | REUSED-TS-15 | How do agentic execution frameworks manage the full tool dispatch lifecycle including validation, bounded execution, and output sealing? |
| F25 | Healing/remediation/escalation tiers | **YES** | **NEW** | How do agentic systems implement confidence-scored tiered healing dispatch routing failures through local rules, model retry, and human escalation? |
| F26 | Current-run exit review and explicit dispositions | No | REUSED-TS-17 | How do AI agent frameworks evaluate outputs against quality rubrics and emit explicit ALLOW, DENY, ESCALATE, or COMMIT dispositions at run exit? |
| F27 | HITL airlock and L5 re-clearance | No | REUSED-TS-11 | How do human-in-the-loop review workflows pause agent execution, collect human approval, and re-authorize the agent to continue? |
| F28 | UWG/state sovereignty/write governance/read-surface refresh | Advisory | REUSED-TS-16 | How do agentic systems enforce single-writer state sovereignty with RBAC blast-radius controls and serialized write governance gates? |
| F29 | L6 observability/verify spine/control buses/evidence bundle | No | REUSED-TS-17 | How do AI agent frameworks implement observability with tracing spans, evaluation metrics like Recall@K and MRR, and structured evidence bundles? |
| F30 | Shadow evaluation/RCA/promotion pipeline | No | REUSED-TS-17 | How do agentic learning systems run shadow evaluations, generate root cause analyses, and promote validated rules through a quality gate pipeline? |
| F31 | Capability/tool/model/network/memory/write access-control plane | No | REUSED-TS-13 | How do AI agent frameworks implement access control for tools, models, network calls, and memory writes through capability tokens and invocation records? |

---

## Query Statistics

| Status | Count | Families |
|--------|-------|---------|
| REUSED-TS-xx | 26 | F01–F07, F10–F11, F13–F20, F23–F24, F26–F31 |
| NEW | 3 | F08, F09, F25 |
| NEW-INTERNAL-PROBE | 2 | F21, F22 |

The 3 NEW queries correspond exactly to the 3 net-new audit queries identified in the B5R audit (P1/P8 + semantic cache). The 2 INTERNAL probes confirm absence of external authority, not presence.

---

## TS-to-Family Cross-Reference

| TS Alias | Query Target | Families Tested |
|----------|-------------|-----------------|
| TS-01 | Agent intent/planning | F03, F11 |
| TS-02 | Grounded context retrieval | F10 |
| TS-03 | Hybrid dense+sparse retrieval | F12 |
| TS-04 | Cross-encoder reranking | F13 |
| TS-05 | Provenance/audit trail | F23 |
| TS-08 | Dedup/context budget | F15 |
| TS-09 | Abstain/refine/fallback | F06, F14, F17 |
| TS-10 | Route authority/ACL | F07 |
| TS-11 | Multi-agent agentic patterns | F01, F04, F27 |
| TS-12 | Multi-agent coordination | F05 |
| TS-13 | Tool dispatch/capability | F16, F19, F20, F31 |
| TS-15 | Execution lifecycle | F24 |
| TS-16 | Governance/safety | F18, F28 |
| TS-17 | Evaluation/exit review | F26, F29, F30 |
| TS-18 | Task decomposition | F05 |
| TS-20 | Identity/auth/schema | F02 |
| NEW | LLM response caching | F08 |
| NEW | Semantic cache | F09 |
| NEW | Healing tiers | F25 |
