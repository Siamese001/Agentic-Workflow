# /windsurf_rules/08_prompt_rag_governance.md
## Prompt Governance, RAG Determinism, and High-Signal Drafting Rules

### 1. Prompt Governance
- All prompts must be stored in a prompt registry.
- Each prompt defines: ID, version, schema, owner, change log.
- Placeholders must be used exactly as declared.

### 2. RAG Determinism
- Same query + same corpus = same retrieval.
- BM25, dense retrieval, and RRF must be deterministic.
- Golden offline datasets required.

### 3. Drafting Rules & High-Signal Requirements
- Drafting stack: Planner(L1) → Executor(L2) → Critic(L1) → Fix(L1) → DAG(L3)
- High-signal outputs require:
  - No fluff
  - Metric injection
  - Persona/company alignment
  - Strict context relevance enforcement
